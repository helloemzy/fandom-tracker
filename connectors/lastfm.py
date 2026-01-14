import os
import requests


LASTFM_API_URL = "https://ws.audioscrobbler.com/2.0/"


def fetch_artist_stats(artist_name):
    api_key = os.getenv("LASTFM_API_KEY")
    if not api_key:
        return None

    params = {
        "method": "artist.getinfo",
        "artist": artist_name,
        "api_key": api_key,
        "format": "json"
    }
    response = requests.get(LASTFM_API_URL, params=params, timeout=20)
    response.raise_for_status()
    payload = response.json()

    artist = payload.get("artist")
    if not artist or "stats" not in artist:
        return None

    stats = artist["stats"]
    return {
        "listeners": int(stats.get("listeners", 0)),
        "playcount": int(stats.get("playcount", 0))
    }
