import os
import requests


DEFAULT_BASE_URL = "https://ws.audioscrobbler.com/2.0/"


def _get_api_key():
    return os.getenv("LASTFM_API_KEY")


def _fetch(params, api_key):
    api_key = api_key or _get_api_key()
    if not api_key:
        raise ValueError("LASTFM_API_KEY is not set.")

    merged = {
        "api_key": api_key,
        "format": "json",
    }
    merged.update(params)

    response = requests.get(DEFAULT_BASE_URL, params=merged, timeout=30)
    response.raise_for_status()
    return response.json()


def fetch_top_artists(limit=50, period="7day", api_key=None):
    payload = _fetch(
        {
            "method": "chart.getTopArtists",
            "limit": limit,
            "period": period,
        },
        api_key,
    )
    artists = payload.get("artists", {}).get("artist", [])
    data = []
    for idx, artist in enumerate(artists, start=1):
        data.append(
            {
                "rank": idx,
                "name": artist.get("name"),
                "playcount": artist.get("playcount"),
                "listeners": artist.get("listeners"),
                "url": artist.get("url"),
            }
        )
    return {"data": data, "meta": payload.get("artists", {}).get("@attr", {})}


def fetch_top_tracks(limit=50, period="7day", api_key=None):
    payload = _fetch(
        {
            "method": "chart.getTopTracks",
            "limit": limit,
            "period": period,
        },
        api_key,
    )
    tracks = payload.get("tracks", {}).get("track", [])
    data = []
    for idx, track in enumerate(tracks, start=1):
        artist = track.get("artist", {})
        data.append(
            {
                "rank": idx,
                "title": track.get("name"),
                "artist": artist.get("name") if isinstance(artist, dict) else artist,
                "playcount": track.get("playcount"),
                "listeners": track.get("listeners"),
                "url": track.get("url"),
            }
        )
    return {"data": data, "meta": payload.get("tracks", {}).get("@attr", {})}
