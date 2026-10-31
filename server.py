
import os
import json
import httpx
from fastmcp import FastMCP

mcp = FastMCP("Pexels Music Video Finder")

PEXELS_API = "https://api.pexels.com"
TIMEOUT = 30.0


def pexels_get(endpoint: str, params: dict) -> dict:
    key = os.getenv("PEXELS_API_KEY")
    if not key:
        raise ValueError("PEXELS_API_KEY is not configured on the server.")

    response = httpx.get(
        f"{PEXELS_API}{endpoint}",
        headers={"Authorization": key},
        params=params,
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    return response.json()


@mcp.tool
def search_pexels_photos(
    query: str,
    orientation: str = "landscape",
    per_page: int = 10,
) -> str:
    """Search Pexels photos for music-video scenes."""
    if not 1 <= per_page <= 20:
        raise ValueError("per_page must be between 1 and 20.")

    data = pexels_get(
        "/v1/search",
        {
            "query": query,
            "orientation": orientation,
            "per_page": per_page,
        },
    )

    results = []
    for photo in data.get("photos", []):
        results.append({
            "photographer": photo.get("photographer"),
            "photo_url": photo.get("url"),
            "image": photo.get("src", {}).get("large"),
            "download": photo.get("src", {}).get("original"),
            "alt": photo.get("alt"),
        })

    return json.dumps({
        "source": "Pexels",
        "credit": "Photos provided by Pexels",
        "results": results,
    }, ensure_ascii=False)


@mcp.tool
def search_pexels_videos(
    query: str,
    orientation: str = "landscape",
    per_page: int = 10,
) -> str:
    """Search Pexels videos for music-video scenes."""
    if not 1 <= per_page <= 20:
        raise ValueError("per_page must be between 1 and 20.")

    data = pexels_get(
        "/v1/videos/search",
        {
            "query": query,
            "orientation": orientation,
            "per_page": per_page,
        },
    )

    results = []
    for video in data.get("videos", []):
        files = [
            {
                "quality": f.get("quality"),
                "width": f.get("width"),
                "height": f.get("height"),
                "file_type": f.get("file_type"),
                "link": f.get("link"),
            }
            for f in video.get("video_files", [])
            if f.get("file_type") == "video/mp4"
        ]

        results.append({
            "video_url": video.get("url"),
            "duration_seconds": video.get("duration"),
            "preview": video.get("image"),
            "files": files,
        })

    return json.dumps({
        "source": "Pexels",
        "credit": "Videos provided by Pexels",
        "results": results,
    }, ensure_ascii=False)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "10000"))
    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=port,
        path="/mcp",
    )
