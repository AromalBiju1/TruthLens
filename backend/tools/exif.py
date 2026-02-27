import io
from PIL import Image
from PIL.ExifTags import TAGS

# These formats almost never carry EXIF — web platforms strip it before serving.
# Flagging these as "suspicious for no EXIF" causes false positives on real web images.
_EXIF_OPTIONAL_FORMATS = {"WEBP", "PNG", "GIF", "BMP", "TIFF"}


def extract_exif(image_bytes: bytes) -> dict:
    """
    Extracts EXIF metadata from image.
    Stripped EXIF is a signal of manipulation for JPEG camera photos,
    but is completely normal for WebP/PNG images served from the web —
    all major browsers and CDNs strip metadata before delivery.

    Returns:
        stripped          (bool) — True if no EXIF found
        stripped_expected (bool) — True if the format normally has no EXIF (webp/png/etc)
        camera, software, date_taken, gps, raw — standard EXIF fields
    """
    try:
        image = Image.open(io.BytesIO(image_bytes))
        fmt = (image.format or "").upper()
        exif_optional = fmt in _EXIF_OPTIONAL_FORMATS

        exif_data = image._getexif()
        if not exif_data:
            return {
                "stripped": True,
                "stripped_expected": exif_optional,
                "format": fmt,
                "camera": None,
                "software": None,
                "date_taken": None,
                "gps": False,
                "raw": {},
            }

        decoded = {}
        for tag_id, value in exif_data.items():
            tag = TAGS.get(tag_id, tag_id)
            try:
                decoded[tag] = str(value)
            except Exception:
                continue

        return {
            "stripped": False,
            "stripped_expected": False,
            "format": fmt,
            "camera": decoded.get("Model"),
            "software": decoded.get("Software"),
            "date_taken": decoded.get("DateTimeOriginal"),
            "gps": "GPSInfo" in decoded,
            "raw": decoded,
        }

    except Exception as e:
        print(f"[TruthLens] EXIF error: {e}")
        return {
            "stripped": True,
            "stripped_expected": False,
            "format": "UNKNOWN",
            "camera": None,
            "software": None,
            "date_taken": None,
            "gps": False,
            "raw": {},
        }
