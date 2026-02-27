import io
import numpy as np
from PIL import Image
import insightface
from insightface.app import FaceAnalysis

_app = None

def load():
    global _app
    if _app is not None:
        return
    print("[TruthLens] Loading InsightFace on CUDA...")
    _app = FaceAnalysis(
        name="buffalo_l",
        providers=["CUDAExecutionProvider", "CPUExecutionProvider"]
    )
    _app.prepare(ctx_id=0, det_size=(640, 640))
    print("[TruthLens] InsightFace loaded ✓")


def extract_face(image_bytes: bytes) -> tuple:
    load()
    try:
        img_array = np.array(Image.open(io.BytesIO(image_bytes)).convert("RGB"))
        faces = _app.get(img_array)

        if not faces:
            return None, {"faces_found": 0, "message": "No face detected — analyzing full image"}

        #take highest confidence face
        face = max(faces, key=lambda f: f.det_score)
        x1, y1, x2, y2 = [int(v) for v in face.bbox]

        # Add padding
        h, w = img_array.shape[:2]
        pad = 30
        x1 = max(0, x1 - pad)
        y1 = max(0, y1 - pad)
        x2 = min(w, x2 + pad)
        y2 = min(h, y2 + pad)

        face_crop = img_array[y1:y2, x1:x2]

        return face_crop, {
            "faces_found": len(faces),
            "confidence": round(float(face.det_score) * 100, 2),
            "landmarks": face.kps.tolist() if face.kps is not None else [],
            "bbox": {"x1": x1, "y1": y1, "x2": x2, "y2": y2}
        }

    except Exception as e:
        print(f"[TruthLens] InsightFace error: {e}")
        return None, {"faces_found": 0, "message": str(e)}


def face_to_bytes(face_array: np.ndarray) -> bytes:
    """Convert numpy face array back to bytes for model input."""
    image = Image.fromarray(face_array)
    buf = io.BytesIO()
    image.save(buf, format="JPEG")
    return buf.getvalue()