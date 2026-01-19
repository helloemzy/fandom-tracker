"""
Fetch K-pop comeback schedule RSS and store as CSV for the dashboard.

Run:
    python update_comebacks.py

Output:
    data/comeback_feed.csv
"""

from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
import os
import xml.etree.ElementTree as ET

import pandas as pd
import requests


RSS_URL = "https://kpopofficial.com/category/kpop-comeback-schedule/"
OUTPUT_PATH = "data/comeback_feed.csv"
RETENTION_DAYS = 90


def _parse_pub_date(value):
    if not value:
        return None
    try:
        dt = parsedate_to_datetime(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except (TypeError, ValueError):
        return None


def fetch_rss_items():
    response = requests.get(RSS_URL, timeout=30)
    response.raise_for_status()

    root = ET.fromstring(response.text)
    channel = root.find("channel")
    if channel is None:
        return []

    items = []
    for item in channel.findall("item"):
        title = item.findtext("title") or ""
        link = item.findtext("link") or ""
        pub_date_raw = item.findtext("pubDate") or ""
        pub_date = _parse_pub_date(pub_date_raw)

        items.append({
            "title": title.strip(),
            "link": link.strip(),
            "pub_date": pub_date.isoformat() if pub_date else None,
            "source": "kpopofficial.com",
        })

    return items


def merge_and_trim(existing_df, new_items):
    new_df = pd.DataFrame(new_items)
    if existing_df is None or existing_df.empty:
        combined = new_df
    else:
        combined = pd.concat([existing_df, new_df], ignore_index=True)

    if combined.empty:
        return combined

    combined["pub_date"] = pd.to_datetime(combined["pub_date"], errors="coerce", utc=True)
    combined = combined.dropna(subset=["title", "link"]).drop_duplicates(subset=["title", "link"])

    cutoff = datetime.now(timezone.utc) - timedelta(days=RETENTION_DAYS)
    combined = combined[combined["pub_date"] >= cutoff]
    combined = combined.sort_values("pub_date", ascending=False)
    return combined


def main():
    os.makedirs("data", exist_ok=True)

    try:
        existing_df = pd.read_csv(OUTPUT_PATH)
    except FileNotFoundError:
        existing_df = pd.DataFrame()

    items = fetch_rss_items()
    combined = merge_and_trim(existing_df, items)
    combined.to_csv(OUTPUT_PATH, index=False)
    print(f"Saved {len(combined)} items -> {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
