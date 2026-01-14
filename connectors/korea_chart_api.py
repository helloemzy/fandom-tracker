import os
import requests


PLATFORMS = {
    "melon": "realtime_rank",
    "genie": "genie_realtime_rank",
    "vibe": "vibe_realtime_rank",
    "bugs": "bugs_realtime_rank"
}


def fetch_chart(platform):
    base_url = os.getenv("KOREA_CHART_API_BASE_URL")
    if not base_url:
        return None

    url = f"{base_url.rstrip('/')}/{platform}/chart"
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.json()
