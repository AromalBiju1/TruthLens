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
        def forward_hook(module,inpuut,output):
            self.activation = output.detach()
        def backward_hook(module,grad_input,grad_output):
            self.gradients = grad_output[0].detach()

        self.target_layer.register_forward_hook(forward_hook)     
        self.target_layer.register_full_backward_hook(backward_hook)    



    def generate(self,tensor:torch.Tensor,class_idx: int = 1)->np.ndarray:
        self.model.zero_grad()
        #must be fp32 for gradients
        tensor = tensor.float()
        output = self.model(tensor)
        score = output[0][class_idx]
        score.backward()

        #global avg pool the gradients

        weights = self.gradients.mean(dim=(2,3),keepdim=True)
        cam = (weight*self.activation).sum(dim=1,keepdim=True)
        cam = F.relu(cam)
        cam = cam.squeeze().cpu().numpy()
        cam = (cam - cam.min()) / (cam.max() - cam.min() + 1e-8)
        return cam


    def generate_heatmap(model,transform,device,image_bytes:bytes)->str:
        """Runs Grad-CAM on the image.
        Returns base64 encoded heatmap overlay — red = high suspicion"""
        try:
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            img_array = np.array(image)

            #fp32 for gradient computation
            model_fp32 = model.float()
            tensor = transform(image).unsqueeze(0).to(device).float()
             # Target last conv block of EfficientNet
            target_layer = model_fp32.blocks[-1]
            gradcam = GradCam(model_fp32,target_layer)
            cam = gradcam.generate(tensor,class_idx=1)
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

            # Cast back to FP16 if on CUDA
            if device.type == "cuda":
                model.half()

            return f"data:image/jpeg;base64,{b64}"

        except Exception as e:
            print(f"[TruthLens] Grad-CAM error: {e}")
            return ""






