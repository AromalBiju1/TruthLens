import io
import cv2
import numpy as np
import torch
import torch.nn.functional as F
import base64
from PIL import Image

class GradCam:
    def __init__(self,model,target_layer):
        self.model = model
        self.target_layer = target_layer
        self.gradients = None
        self.activation = None
        self.register_hooks()
    def register_hooks(self):
        def forward_hook(module, inpuut, output):
            self.activation = output.detach()
        def backward_hook(module, grad_input, grad_output):
            self.gradients = grad_output[0].detach()

        self._fwd_handle = self.target_layer.register_forward_hook(forward_hook)
        self._bwd_handle = self.target_layer.register_full_backward_hook(backward_hook)

    def remove_hooks(self):
        self._fwd_handle.remove()
        self._bwd_handle.remove()



    def generate(self,tensor:torch.Tensor,class_idx: int = 1)->np.ndarray:
        self.model.zero_grad()
        #must be fp32 for gradients
        tensor = tensor.float()
        output = self.model(tensor)
        score = output[0][class_idx]
        score.backward()

        #global avg pool the gradients

        weights = self.gradients.mean(dim=(2,3),keepdim=True)
        cam = (weights * self.activation).sum(dim=1, keepdim=True)
        cam = F.relu(cam)
        cam = cam.squeeze().cpu().numpy()
        cam = (cam - cam.min()) / (cam.max() - cam.min() + 1e-8)
        self.remove_hooks()
        return cam


def generate_heatmap(model, transform, device, image_bytes: bytes) -> str:
    """Runs Grad-CAM on the image.
    Always runs on CPU to avoid VRAM OOM — GPU is already used by EfficientNet + CLIP.
    Returns base64 encoded heatmap overlay — red = high suspicion."""
    try:
        import copy
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        img_array = np.array(image)

        # Run entirely on CPU to avoid VRAM OOM after EfficientNet + CLIP.
        # Grad-CAM is visualization-only; CPU is fast enough.
        cpu_device = torch.device("cpu")
        model_cpu = copy.deepcopy(model).float().to(cpu_device)
        model_cpu.eval()

        tensor = transform(image).unsqueeze(0).to(cpu_device).float()
        target_layer = model_cpu.blocks[-1]
        gradcam = GradCam(model_cpu, target_layer)
        cam = gradcam.generate(tensor, class_idx=1)

        cam_resized = cv2.resize(cam, (img_array.shape[1], img_array.shape[0]))

        # Apply JET colormap — red = suspicious, blue = clean
        heatmap = cv2.applyColorMap(np.uint8(255 * cam_resized), cv2.COLORMAP_JET)
        heatmap = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)

        # Overlay on original
        overlay = (0.5 * img_array + 0.5 * heatmap).astype(np.uint8)

        # Encode to base64 for sending to frontend
        buf = io.BytesIO()
        Image.fromarray(overlay).save(buf, format="JPEG", quality=85)
        b64 = base64.b64encode(buf.getvalue()).decode()

        # Clean up CPU copy explicitly
        del model_cpu

        return f"data:image/jpeg;base64,{b64}"

    except Exception as e:
        print(f"[TruthLens] Grad-CAM error: {e}")
        return ""






