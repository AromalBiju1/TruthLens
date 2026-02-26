import os


def reverse_search_mock() -> list:
    """
    Mock reverse image search results for development.
    Swap this with real SerpAPI / googlesearch call when ready.
    """
    return [
        {
            "url": "https://example.com/original-photo",
            "title": "Possible original source found",
            "thumbnail": "",
            "date": "2024-03-10"
        },
        {
            "url": "https://socialmedia.example.com/post/123",
            "title": "Shared on social media",
            "thumbnail": "",
            "date": "2024-05-22"
        },
    ]


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