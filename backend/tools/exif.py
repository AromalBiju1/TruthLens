import io
from PIL import Image
from PIL.ExifTags import TAGS


def extract_exif(image_bytes:bytes) -> dict:
    """
    Extracts EXIF metadata from image.
    Stripped EXIF is a strong signal of manipulation —
    most AI generators produce images with no metadata at all.
    """

    try:
        image = Image.open(io.BytesIO(image_bytes))
        exif_data = image._getexif()
        if not exif_data:
            return{
                "stripped" : True,
                "camera": None,
                "software":None,
                "date_taken" :None,
                "gps":False,
                "raw": {}
            }
        decoded = {}
        for tag_id, value in exif_data.items():
            tag = TAGS.get(tag_id,tag_id)
            try:
                decoded[tag] = str(value)
            except Exception:
                continue

        return{
                "stripped" : False,
                "camera": decoded.get("Model"),
                "software":decoded.get("Software"),
                "date_taken" :decoded.get("DateTimeOriginal"),
                "gps":"GPSInfo" in decoded,
                "raw": decoded
            }
    except Exception as e:
        print(f"Exif error: {e}")
        return{
                "stripped" : True,
                "camera": None,
                "software":None,
                "date_taken" :None,
                "gps":False,
                "raw": {}
            }


