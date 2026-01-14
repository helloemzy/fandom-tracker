import os
import requests


PLATFORMS = {
    "melon": "realtime_rank",
    "genie": "genie_realtime_rank",
    "vibe": "vibe_realtime_rank",
    "bugs": "bugs_realtime_rank"
}

DEFAULT_BASE_URL = "https://korea-music-chart-api-autumn-sun-1261.fly.dev"


def _get_base_url():
    base_url = os.getenv("KOREA_CHART_API_BASE_URL")
    if not base_url:
        base_url = DEFAULT_BASE_URL
    return base_url.rstrip("/")


def _fetch_json(url):
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.json()


def fetch_chart(platform):
    base_url = _get_base_url()
    url = f"{base_url}/{platform}/chart"
    return _fetch_json(url)


def fetch_artist_chart(platform, artist_name):
    base_url = _get_base_url()
    url = f"{base_url}/{platform}/chart/{artist_name}"
    return _fetch_json(url)


def fetch_artist_albums(platform, artist_name):
    base_url = _get_base_url()
    if platform == "bugs":
        path = "album"
    else:
        path = "albums"
    url = f"{base_url}/{platform}/{path}/{artist_name}"
    return _fetch_json(url)


def fetch_album_songs(platform, album_number):
    base_url = _get_base_url()
    if platform == "bugs":
        path = "song"
    else:
        path = "songs"
    url = f"{base_url}/{platform}/{path}/{album_number}"
    return _fetch_json(url)
