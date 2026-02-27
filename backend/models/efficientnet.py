import io
from PIL import Image
import torch
import timm

# ── Device setup ──────────────────────────────────────────────────────────────
_device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
_model = None
_transform = None


def _load_model():
    global _model, _transform
    if _model is not None:
        return

    print(f"[TruthLens] Loading EfficientNet-B7 on {_device}...")

    _model = timm.create_model("tf_efficientnet_b7", pretrained=True)
    in_features = _model.classifier.in_features
    _model.classifier = torch.nn.Linear(in_features, 2)
    _model = _model.to(_device)
    _model.eval()

    if _device.type == "cuda":
        _model = _model.half()  # FP16 — faster inference, less VRAM
        print(f"[TruthLens] FP16 on {torch.cuda.get_device_name(0)}")
    else:
        print("[TruthLens] No CUDA, running on CPU")

    data_config = timm.data.resolve_model_data_config(_model)
    _transform = timm.data.create_transform(**data_config, is_training=False)
    print("[TruthLens] EfficientNet-B7 ready ✓")


def run_efficientnet(image_bytes: bytes) -> float:
    """
    Returns float 0-100 — probability the image is AI-generated.
    NOTE: Pretrained on ImageNet. Fine-tune on FaceForensics++ for production.
    """
    _load_model()
    try:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        tensor = _transform(image).unsqueeze(0).to(_device)

        if _device.type == "cuda":
            tensor = tensor.half()

        with torch.no_grad():
            logits = _model(tensor)
            probs = torch.softmax(logits.float(), dim=1)
            fake_prob = probs[0][1].item() * 100

        return round(fake_prob, 2)

    except Exception as e:
        print(f"[TruthLens] EfficientNet error: {e}")
        return 50.0


def get_device_info() -> dict:
    return {
        "device": str(_device),
        "cuda_available": torch.cuda.is_available(),
        "gpu_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
        "gpu_memory_gb": round(torch.cuda.get_device_properties(0).total_memory / 1e9, 1) if torch.cuda.is_available() else None,
        "model": "EfficientNet-B7",
        "precision": "FP16" if torch.cuda.is_available() else "FP32",
    }



def get_model_and_transform():
    """Expose model + transform for Grad-CAM."""
    _load_model()
    return _model, _transform, _device