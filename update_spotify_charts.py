"""
Fetch Spotify Global Daily chart from Kworb and compute daily deltas.

Run:
    python update_spotify_charts.py

Outputs:
    data/spotify_global_daily_history.csv
    data/spotify_global_daily_latest.csv
"""

from datetime import datetime, timezone
from io import StringIO
import os

import pandas as pd
import requests


KWORB_GLOBAL_DAILY_URL = "https://kworb.net/spotify/country/global_daily.html"
HISTORY_PATH = "data/spotify_global_daily_history.csv"
LATEST_PATH = "data/spotify_global_daily_latest.csv"
HEADERS = {
    "User-Agent": "Signal-Index-Bot/1.0 (Educational Project; Contact: signalindex@example.com)"
}


def fetch_global_daily():
    response = requests.get(KWORB_GLOBAL_DAILY_URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    tables = pd.read_html(StringIO(response.text))
    if not tables:
        raise ValueError("No tables found on Kworb page.")
    df = tables[0]
    required_cols = {"Pos", "Artist and Title", "Streams"}
    if not required_cols.issubset(df.columns):
        raise ValueError("Kworb table columns changed.")
    df = df.rename(
        columns={
            "Pos": "rank",
            "Artist and Title": "artist_title",
            "Streams": "streams",
        }
    )

    artist_title = df["artist_title"].astype(str).str.split(" - ", n=1, expand=True)
    df["artist"] = artist_title[0].str.strip()
    df["title"] = artist_title[1].str.strip() if artist_title.shape[1] > 1 else None

    df["rank"] = pd.to_numeric(df["rank"], errors="coerce")
    df["streams"] = (
        df["streams"]
        .astype(str)
        .str.replace(",", "", regex=False)
    )
    df["streams"] = pd.to_numeric(df["streams"], errors="coerce")

    df["date"] = datetime.now(timezone.utc).date().isoformat()
    df["chart"] = "spotify_global_daily"

    return df[["date", "chart", "rank", "artist", "title", "streams"]]


def load_history():
    try:
        return pd.read_csv(HISTORY_PATH)
    except FileNotFoundError:
        return pd.DataFrame()


def save_history(history_df):
    history_df.to_csv(HISTORY_PATH, index=False)


def compute_latest(history_df):
    if history_df.empty:
        return pd.DataFrame()

    history_df["date"] = pd.to_datetime(history_df["date"], errors="coerce")
    dates = sorted(history_df["date"].dropna().dt.date.unique())
    if len(dates) < 2:
        latest = history_df[history_df["date"].dt.date == dates[-1]].copy()
        latest["delta_streams"] = None
        latest["delta_rank"] = None
        return latest

    current_date = dates[-1]
    prev_date = dates[-2]

    current = history_df[history_df["date"].dt.date == current_date].copy()
    previous = history_df[history_df["date"].dt.date == prev_date].copy()

    previous_keyed = previous.set_index(["artist", "title"])
    current_keyed = current.set_index(["artist", "title"])

    current_keyed["prev_streams"] = previous_keyed["streams"]
    current_keyed["prev_rank"] = previous_keyed["rank"]
    current_keyed["delta_streams"] = current_keyed["streams"] - current_keyed["prev_streams"]
    current_keyed["delta_rank"] = current_keyed["prev_rank"] - current_keyed["rank"]

    latest = current_keyed.reset_index()
    return latest


def main():
    os.makedirs("data", exist_ok=True)

    try:
        latest_df = fetch_global_daily()
    except Exception as exc:
        print(f"Kworb fetch failed: {type(exc).__name__}: {exc}")
        return
    history_df = load_history()

    combined = pd.concat([history_df, latest_df], ignore_index=True)
    combined = combined.drop_duplicates(subset=["date", "artist", "title"], keep="last")
    combined = combined.sort_values(["date", "rank"])
    save_history(combined)

    latest = compute_latest(combined)
    latest.to_csv(LATEST_PATH, index=False)
    print(f"Saved {len(latest)} rows -> {LATEST_PATH}")


if __name__ == "__main__":
    main()
