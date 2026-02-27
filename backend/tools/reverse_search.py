import os


from ddgs import DDGS
import base64



def reverse_search(image_bytes: bytes, filename: str = "", exif: dict = {}) -> list:
    try:
        # Build a meaningful query from what we know
        query = filename.replace("_", " ").replace("-", " ").split(".")[0]
        if not query or query in ["image", "photo", "img", "4", "unnamed"]:
            query = "AI generated face deepfake"

        with DDGS() as ddgs:
            results = list(ddgs.images(
                query,
                max_results=5
            ))

        return [
            {
                "url": r.get("url", ""),
                "title": r.get("title", ""),
                "thumbnail": r.get("thumbnail", ""),
                "date": None
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