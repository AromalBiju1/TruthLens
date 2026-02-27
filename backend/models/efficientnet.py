import io
from PIL import Image
import torch
from transformers import ViTForImageClassification, ViTImageProcessor

# ── Device setup ──────────────────────────────────────────────────────────────
_device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
_model = None
_processor = None

# Using umm-maybe/AI-image-detector — ViT trained specifically on real vs AI-generated images.
# Replaces the original tf_efficientnet_b7 + random untrained Linear(in, 2) head
# which was outputting meaningless random logits (pretrained backbone, zero-trained classifier).
MODEL_ID = "umm-maybe/AI-image-detector"


def _load_model():
    global _model, _processor
    if _model is not None:
        return

    print(f"[TruthLens] Loading AI-image-detector on {_device}...")

    _processor = ViTImageProcessor.from_pretrained(MODEL_ID)
    _model = ViTForImageClassification.from_pretrained(MODEL_ID)
    _model = _model.to(_device)
    _model.eval()

    if _device.type == "cuda":
        _model = _model.half()
        print(f"[TruthLens] FP16 on {torch.cuda.get_device_name(0)}")
    else:
        print("[TruthLens] No CUDA, running on CPU")

    print("[TruthLens] AI-image-detector ready ✓")


def run_efficientnet(image_bytes: bytes) -> float:
    """
    Returns float 0-100 — probability the image is AI-generated.
    Uses umm-maybe/AI-image-detector (ViT fine-tuned on real vs AI images).

    Label mapping for this model:
      label 0 = artificial (AI-generated)
      label 1 = human (real photograph)
    """
    _load_model()
    try:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        inputs = _processor(images=image, return_tensors="pt").to(_device)

        if _device.type == "cuda":
            inputs = {k: v.half() if v.dtype == torch.float32 else v
                      for k, v in inputs.items()}

        with torch.no_grad():
            logits = _model(**inputs).logits
            probs = torch.softmax(logits.float(), dim=1)[0]

        # Model labels: 0=artificial, 1=human  →  fake_prob = prob[0]
        id2label = _model.config.id2label
        fake_idx = next(
            (i for i, lbl in id2label.items() if "artificial" in lbl.lower()),
            0
        )
        fake_prob = probs[fake_idx].item() * 100

        return round(fake_prob, 2)

    except Exception as e:
        print(f"[TruthLens] Detector error: {e}")
        return 50.0


def get_device_info() -> dict:
    return {
        "device": str(_device),
        "cuda_available": torch.cuda.is_available(),
        "gpu_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
        "gpu_memory_gb": round(
            torch.cuda.get_device_properties(0).total_memory / 1e9, 1
        ) if torch.cuda.is_available() else None,
        "model": MODEL_ID,
        "precision": "FP16" if torch.cuda.is_available() else "FP32",
    }


def get_model_and_transform():
    """
    Expose model + processor for Grad-CAM.
    Returns (model, transform_fn, device) — transform_fn wraps the ViT processor
    into a torchvision-compatible callable for gradcam.py compatibility.
    """
    _load_model()

    import torchvision.transforms as T
    # Grad-CAM needs a torchvision transform that returns a CHW tensor.
    # Use the processor's image_mean/std to stay consistent.
    mean = _processor.image_mean
    std  = _processor.image_std
    size = _processor.size.get("height", 224)

    transform = T.Compose([
        T.Resize((size, size)),
        T.ToTensor(),
        T.Normalize(mean=mean, std=std),
    ])

    return _model, transform, _device