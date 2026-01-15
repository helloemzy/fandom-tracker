import os
from urllib.parse import quote

import requests


DEFAULT_BASE_URL = "https://billboard-charts.fly.dev"

BILLBOARD_CHARTS = [
    "adult-contemporary",
    "alternative-songwriters",
    "artist-100",
    "australia-songs-hotw",
    "australian-albums",
    "austria-songs-hotw",
    "belgium-songs-hotw",
    "billboard-200",
    "billboard-argentina-hot-100",
    "billboard-brasil-hot-100",
    "billboard-colombia-hot-100",
    "billboard-global-200",
    "billboard-italy-albums-top-100",
    "billboard-italy-hot-100",
    "billboard-korea-global-k-songs",
    "billboard-korea-hot-100",
    "billboard-philippines-hot-100",
    "billboard-philippines-top-philippine-songs",
    "billboard-thailand-top-thai-country-songs",
    "billboard-thailand-top-thai-songs",
    "billboard-vietnam-hot-100-songs",
    "billboard-vietnam-top-vietnamese-songs",
    "bolivia-songs-hotw",
    "canadian-albums",
    "canadian-hot-100",
    "chile-songs-hotw",
    "china-tme-uni-songs",
    "christian-airplay",
    "christian-albums",
    "christian-producers",
    "christian-songs",
    "christian-songwriters",
    "christian-streaming-songs",
    "country-airplay",
    "country-albums",
    "country-producers",
    "country-songs",
    "country-songwriters",
    "croatia-songs-hotw",
    "czech-republic-songs-hotw",
    "dance-electronic-producers",
    "dance-electronic-songs",
    "dance-electronic-songwriters",
    "dance-pop-producers",
    "dance-pop-songwriters",
    "decade-end",
    "denmark-songs-hotw",
    "digital-song-sales",
    "ecuador-songs-hotw",
    "feed",
    "finland-songs-hotw",
    "france-songs-hotw",
    "german-albums",
    "germany-songs-hotw",
    "gospel-albums",
    "gospel-producers",
    "gospel-songs",
    "gospel-songwriters",
    "greatest-of-all-time-holiday-100-songs",
    "greatest-of-all-time-top-holiday-albums",
    "greece-albums",
    "greece-songs-hotw",
    "hard-rock-songwriters",
    "holiday-100-producers",
    "holiday-100-songwriters",
    "hot-100",
    "hot-100-producers",
    "hot-100-songwriters",
    "hot-alternative-songs",
    "hot-dance-pop-songs",
    "hot-hard-rock-songs",
    "hot-latin-pop-songs",
    "hot-latin-rhythm-songs",
    "hot-regional-mexican-songs",
    "hot-tropical-songs",
    "hungary-songs-hotw",
    "iceland-songs-hotw",
    "india-songs-hotw",
    "indonesia-songs-hotw",
    "ireland-songs-hotw",
    "japan-hot-100",
    "latin-airplay",
    "latin-albums",
    "latin-songs",
    "latin-songwriters",
    "luxembourg-songs-hotw",
    "malaysia-songs-hotw",
    "mexico-songs-hotw",
    "netherlands-songs-hotw",
    "new-zealand-songs-hotw",
    "norway-songs-hotw",
    "official-uk-albums",
    "official-uk-songs",
    "peru-songs-hotw",
    "poland-songs-hotw",
    "pop-songs",
    "portugal-songs-hotw",
    "r-b-hip-hop-albums",
    "r-b-hip-hop-songs",
    "rap-producers",
    "rap-song",
    "rap-songwriters",
    "rb-producers",
    "rb-songwriters",
    "rock-alternative-producers",
    "rock-alternative-songwriters",
    "rock-producers",
    "rock-songs",
    "rock-songwriters",
    "romania-songs-hotw",
    "singapore-songs-hotw",
    "slovakia-songs-hotw",
    "soundtracks",
    "south-africa-songs-hotw",
    "spain-songs-hotw",
    "summer-songs",
    "sweden-songs-hotw",
    "switzerland-songs-hotw",
    "taiwan-songs-hotw",
    "top-artists-of-the-21st-century",
    "top-billboard-200-albums-of-the-21st-century",
    "top-country-albums-of-the-21st-century",
    "top-country-artists-of-the-21st-century",
    "top-hot-100-songs-of-the-21st-century",
    "top-hot-country-songs-of-the-21st-century",
    "top-latin-albums-of-the-21st-century",
    "top-latin-artists-of-the-21st-century",
    "top-latin-songs-of-the-21st-century",
    "top-rb-hip-hop-albums-of-the-21st-century",
    "top-rb-hip-hop-artists-of-the-21st-century",
    "top-rb-hip-hop-songs-of-the-21st-century",
    "top-rock-alternative-albums",
    "top-streaming-albums",
    "top-women-artists-of-the-21st-century",
    "turkey-songs-hotw",
    "u-k-songs-hotw",
]


def _get_base_url():
    base_url = os.getenv("BILLBOARD_CHART_API_BASE_URL")
    if not base_url:
        base_url = DEFAULT_BASE_URL
    return base_url.rstrip("/")


def _fetch_json(url, params=None):
    response = requests.get(url, params=params, timeout=60)
    response.raise_for_status()
    return response.json()


def fetch_chart(chart_name, date=None, year=None):
    base_url = _get_base_url()
    if not chart_name:
        return None
    safe_chart = quote(str(chart_name), safe="")
    url = f"{base_url}/chart/{safe_chart}"

    params = {}
    if date:
        params["date"] = date
    if year:
        params["year"] = year

    return _fetch_json(url, params=params or None)
