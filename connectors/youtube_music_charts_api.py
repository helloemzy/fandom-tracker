import os
import requests


def _get_api_key():
    return os.getenv("YOUTUBE_API_KEY")


def fetch_music_charts(region_code="US", max_results=50, api_key=None):
    api_key = api_key or _get_api_key()
    if not api_key:
        raise ValueError("YOUTUBE_API_KEY is not set.")

    params = {
        "part": "snippet,statistics",
        "chart": "mostPopular",
        "videoCategoryId": "10",
        "regionCode": region_code,
        "maxResults": max_results,
        "key": api_key,
    }
    response = requests.get(
        "https://www.googleapis.com/youtube/v3/videos",
        params=params,
        timeout=30
    )
    response.raise_for_status()
    payload = response.json()

    items = payload.get("items", [])
    results = []
    for idx, item in enumerate(items, start=1):
        snippet = item.get("snippet") or {}
        stats = item.get("statistics") or {}
        thumbnails = snippet.get("thumbnails") or {}
        thumb = thumbnails.get("default") or thumbnails.get("medium") or {}
        view_count = stats.get("viewCount")
        like_count = stats.get("likeCount")

        results.append({
            "rank": idx,
            "title": snippet.get("title"),
            "artist": snippet.get("channelTitle"),
            "video_id": item.get("id"),
            "views": int(view_count) if view_count is not None else None,
            "likes": int(like_count) if like_count is not None else None,
            "published_at": snippet.get("publishedAt"),
            "thumbnail": thumb.get("url"),
        })

    return {
        "data": results,
        "raw": payload
    }
