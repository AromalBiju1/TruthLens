import os
from ddgs import DDGS

# Filenames that carry zero signal as a search query.
# Searching for these gives random/irrelevant results (e.g. "human" → anatomy).
_GENERIC_NAMES = {
    "image", "img", "photo", "picture", "pic", "file", "upload", "uploaded",
    "screenshot", "screen", "snap", "capture", "frame", "thumb", "thumbnail",
    "human", "person", "face", "man", "woman", "boy", "girl", "people",
    "unnamed", "untitled", "noname", "default", "sample", "test", "demo",
    "temp", "tmp", "download", "downloaded", "media", "content", "data",
    # numeric-only or very short names (phone default names like "4", "IMG_4")
}


def _is_meaningful_filename(name: str) -> bool:
    """
    Returns True only if the filename stem looks like a real proper-noun title
    (e.g. 'putin_press_conference', 'elon_musk_2024') — not a generic camera slug.
    Heuristic: must be >5 chars, not all digits, not in the skip-list.
    """
    name = name.lower().strip()
    if not name or name in _GENERIC_NAMES:
        return False
    if len(name) <= 5:
        return False
    if name.isdigit():
        return False
    # Typical camera roll slugs: IMG_2048, DSC_0042, DCIM1234 etc.
    if any(name.startswith(p) for p in ("img_", "dsc_", "dcim", "pict", "dscn", "mvc-")):
        return False
    return True


def reverse_search(image_bytes: bytes, filename: str = "", exif: dict = {}) -> list:
    try:
        stem = filename.replace("_", " ").replace("-", " ").split(".")[0].strip()

        # Priority 1: use EXIF camera + date for a provenance-style search
        camera   = (exif or {}).get("camera", "")
        date_str = (exif or {}).get("date_taken", "") or ""
        year     = date_str[:4] if len(date_str) >= 4 else ""

        if camera and year:
            query = f"{stem} {camera} {year}".strip() if _is_meaningful_filename(stem) else f"photo {camera} {year}"
        elif _is_meaningful_filename(stem):
            # Priority 2: filename looks like a real title — use it
            query = stem
        else:
            # Fallback: generic deepfake/AI detection context search
            query = "AI generated face deepfake detection real photo"

        with DDGS() as ddgs:
            results = list(ddgs.images(query, max_results=5))

        return [
            {
                "url":       r.get("url", ""),
                "title":     r.get("title", ""),
                "thumbnail": r.get("thumbnail", ""),
                "date":      None,
            }
            for r in results
        ]
    except Exception as e:
        print(f"[TruthLens] Reverse search error: {e}")
        return []

def reverse_search_serpapi(image_url: str) -> list:
    """
    Real SerpAPI reverse image search.
    Activate by calling this instead of reverse_search_mock()
    once you're ready to use your 100 credits.
    """
    try:
        from serpapi import GoogleSearch
        params = {
            "engine": "google_reverse_image",
            "image_url": image_url,
            "api_key": os.getenv("SERPAPI_KEY"),
        }
        results = GoogleSearch(params).get_dict()
        image_results = results.get("image_results", [])[:5]
        return [
            {
                "url": r.get("link", ""),
                "title": r.get("title", ""),
                "thumbnail": r.get("thumbnail", ""),
                "date": r.get("date", None),
            }
            for r in image_results
        ]
    except Exception as e:
        print(f"SerpAPI error: {e}")
        return []