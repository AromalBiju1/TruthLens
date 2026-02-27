import io
import cv2
import numpy as np
import torch
import torch.nn.functional as F
import base64
from PIL import Image


class GradCam:
    def __init__(self, model, target_layer):
        self.model = model
        self.target_layer = target_layer
        self.gradients = None
        self.activation = None
        self.register_hooks()

    def register_hooks(self):
        def forward_hook(module, inp, output):
            # Some layers return tuples/ModelOutput — always grab first tensor element
            if isinstance(output, torch.Tensor):
                self.activation = output.detach()
            elif isinstance(output, (tuple, list)) and len(output) > 0:
                self.activation = output[0].detach()
            else:
                # ModelOutput / dataclass — try index access
                try:
                    self.activation = output[0].detach()
                except Exception:
                    self.activation = None

        def backward_hook(module, grad_input, grad_output):
            if grad_output and grad_output[0] is not None:
                self.gradients = grad_output[0].detach()
            else:
                self.gradients = None

        self._fwd_handle = self.target_layer.register_forward_hook(forward_hook)
        self._bwd_handle = self.target_layer.register_full_backward_hook(backward_hook)

    def remove_hooks(self):
        self._fwd_handle.remove()
        self._bwd_handle.remove()

    def _to_spatial(self, t: torch.Tensor) -> torch.Tensor:
        """
        Normalise any tensor to (B, C, H, W) for Grad-CAM pooling.
          2D  (B, C)      → (B, C, 1, 1)
          3D  (B, N, C)   → (B, C, √N, √N)   Swin style
          3D  (B, C, N)   → (B, C, N, 1)
          4D  (B, C, H, W)→ unchanged
        """
        if t.dim() == 2:
            return t.unsqueeze(-1).unsqueeze(-1)          # (B, C, 1, 1)
        if t.dim() == 3:
            B, D1, D2 = t.shape
            # Swin layernorm output is (B, H*W, C) — last dim is channels
            side = int(D1 ** 0.5)
            if side * side == D1:
                # (B, H*W, C) → (B, C, H, W)
                return t.permute(0, 2, 1).reshape(B, D2, side, side)
            else:
                return t.permute(0, 2, 1).unsqueeze(-1)  # (B, C, N, 1)
        return t  # already 4D

    def generate(self, tensor: torch.Tensor, class_idx: int = 0) -> np.ndarray:
        self.model.zero_grad()
        output = self.model(tensor.float())

        # HuggingFace models wrap output in SequenceClassifierOutput
        logits = output.logits if hasattr(output, "logits") else output[0]
        score = logits[0][class_idx]
        score.backward()

        if self.activation is None or self.gradients is None:
            raise RuntimeError("Hooks did not capture activations/gradients.")

        act  = self._to_spatial(self.activation)
        grad = self._to_spatial(self.gradients)

        weights = grad.mean(dim=(2, 3), keepdim=True)
        cam = (weights * act).sum(dim=1, keepdim=True)
        cam = F.relu(cam).squeeze().cpu().numpy()

        # squeeze() on a (1,1,1,1) → scalar — guard against it
        if cam.ndim == 0:
            cam = np.array([[float(cam)]])

        cam = (cam - cam.min()) / (cam.max() - cam.min() + 1e-8)
        self.remove_hooks()
        return cam


def _find_target_layer(model):
    """
    Pick the best Grad-CAM target layer for the given model.
    Layer must output a plain Tensor (not a dataclass) so hooks capture clean shapes.
    """
    # Swin (HuggingFace) — swin.layernorm outputs plain (B, H*W, C)
    # AVOID swin.layers[-1]: it outputs SwinStageOutput (dataclass), gradients are unreliable
    if hasattr(model, "swin"):
        if hasattr(model.swin, "layernorm"):
            return model.swin.layernorm
        if hasattr(model.swin, "layers"):
            # last SwinLayer block's norm — still a plain tensor output
            return model.swin.layers[-1].blocks[-1].layernorm_after

    # ViT (HuggingFace)
    if hasattr(model, "vit") and hasattr(model.vit, "layernorm"):
        return model.vit.layernorm

    # EfficientNet (timm)
    if hasattr(model, "blocks"):
        return model.blocks[-1]

    # ResNet
    if hasattr(model, "layer4"):
        return model.layer4

    # Generic fallback — last leaf module with own parameters
    last = None
    for _, module in model.named_modules():
        if list(module.parameters(recurse=False)):
            last = module
    if last:
        return last

    raise ValueError("[TruthLens] Could not find a Grad-CAM target layer.")


def generate_heatmap(model, transform, device, image_bytes: bytes) -> str:
    """
    Runs Grad-CAM on the image (always CPU to avoid OOM after CLIP + Swin on GPU).
    Returns base64 JPEG heatmap — red = high suspicion, blue = clean.
    Handles Swin, ViT, EfficientNet, ResNet backbones safely.
    """
    try:
        import copy
        image     = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        img_array = np.array(image)

        model_cpu = copy.deepcopy(model).float().cpu()
        model_cpu.eval()

        tensor       = transform(image).unsqueeze(0).float()  # CPU already
        target_layer = _find_target_layer(model_cpu)
        gradcam      = GradCam(model_cpu, target_layer)
        cam          = gradcam.generate(tensor, class_idx=0)   # 0 = artificial

        cam_resized = cv2.resize(cam, (img_array.shape[1], img_array.shape[0]))
        heatmap     = cv2.applyColorMap(np.uint8(255 * cam_resized), cv2.COLORMAP_JET)
        heatmap     = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)
        overlay     = (0.5 * img_array + 0.5 * heatmap).astype(np.uint8)

        buf = io.BytesIO()
        Image.fromarray(overlay).save(buf, format="JPEG", quality=85)
        b64 = base64.b64encode(buf.getvalue()).decode()

        del model_cpu
        return f"data:image/jpeg;base64,{b64}"

    except Exception as e:
        print(f"[TruthLens] Grad-CAM error: {e}")
        return ""
