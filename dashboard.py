import pandas as pd
import streamlit as st

from connectors.korea_chart_api import (
    fetch_album_songs,
    fetch_artist_albums,
    fetch_artist_chart,
    fetch_chart,
    PLATFORMS
)


st.set_page_config(
    page_title="Signal Index",
    page_icon="📊",
    layout="wide"
)


@st.cache_data(ttl=60)
def load_live_payload(kind, platform, value, refresh_key=0):
    try:
        if kind == "chart":
            return fetch_chart(platform), None
        if kind == "artist_chart":
            return fetch_artist_chart(platform, value), None
        if kind == "artist_albums":
            return fetch_artist_albums(platform, value), None
        if kind == "album_songs":
            return fetch_album_songs(platform, value), None
        return None, "Unknown request type."
    except Exception as exc:
        return None, f"{type(exc).__name__}: {exc}"


def normalize_text(value):
    if value is None:
        return ""
    return "".join(ch for ch in str(value).lower() if ch.isalnum())


def payload_to_df(payload):
    if not payload:
        return pd.DataFrame()
    if isinstance(payload, list):
        return pd.DataFrame(payload)
    if isinstance(payload, dict):
        data = payload.get("data")
        if isinstance(data, list):
            return pd.DataFrame(data)
        return pd.DataFrame([payload])
    return pd.DataFrame()


def filter_chart_entries(payload, artist_query):
    chart_df = payload_to_df(payload)
    if chart_df.empty:
        return chart_df

    query_norm = normalize_text(artist_query)
    if not query_norm:
        return chart_df

    def matches(value):
        return query_norm in normalize_text(value)

    artist_cols = [col for col in ["artistName", "artist"] if col in chart_df.columns]
    if not artist_cols:
        return chart_df

    mask = None
    for col in artist_cols:
        col_mask = chart_df[col].apply(matches)
        mask = col_mask if mask is None else (mask | col_mask)
    return chart_df[mask]


st.title("Signal Index")
st.caption("Live Korea chart API data (no database).")

all_platforms = list(PLATFORMS.keys())
request_type = st.sidebar.radio(
    "Endpoint",
    [
        "Chart",
        "Artist chart",
        "Artist albums",
        "Album songs"
    ]
)

platform = None
if request_type in {"Chart", "Artist chart"}:
    platform_choice = st.sidebar.selectbox(
        "Platform",
        ["All"] + all_platforms
    )
    platform = None if platform_choice == "All" else platform_choice
else:
    platform = st.sidebar.selectbox("Platform", all_platforms)

artist_name = ""
album_number = ""
if request_type in {"Artist chart", "Artist albums"}:
    artist_name = st.sidebar.text_input("Artist name", value="").strip()
if request_type == "Album songs":
    album_number = st.sidebar.text_input("Album number", value="").strip()

if request_type == "Artist chart":
    st.caption("Artist search uses partial matching against the full chart list.")

if st.sidebar.button("Refresh"):
    st.session_state["live_refresh"] = st.session_state.get("live_refresh", 0) + 1

refresh_key = st.session_state.get("live_refresh", 0)

if request_type in {"Artist chart", "Artist albums"} and not artist_name:
    st.info("Enter an artist name to fetch data.")
    st.stop()

if request_type == "Album songs" and not album_number:
    st.info("Enter an album number to fetch songs.")
    st.stop()

kind_map = {
    "Chart": ("chart", None),
    "Artist chart": ("chart", None),
    "Artist albums": ("artist_albums", artist_name or None),
    "Album songs": ("album_songs", album_number or None)
}

kind, value = kind_map[request_type]
payloads = {}
errors = {}

if request_type in {"Chart", "Artist chart"} and platform is None:
    for platform_key in all_platforms:
        payload, error = load_live_payload(kind, platform_key, value, refresh_key)
        if error:
            errors[platform_key] = error
        else:
            payloads[platform_key] = payload
else:
    payload, error = load_live_payload(kind, platform, value, refresh_key)
    if error:
        errors[platform] = error
    else:
        payloads[platform] = payload

if errors:
    for platform_key, message in errors.items():
        st.error(f"{platform_key} fetch failed: {message}")

    if not payloads:
        st.info("No data returned.")
    else:
        for platform_key, payload in payloads.items():
            st.subheader(f"{platform_key.capitalize()} Chart")
            if request_type == "Artist chart":
                chart_df = filter_chart_entries(payload, artist_name)
                if chart_df.empty:
                    st.info("No matching artists found.")
            else:
                chart_df = payload_to_df(payload)
            if chart_df.empty:
                st.info("No data returned.")
            else:
                st.dataframe(chart_df, use_container_width=True)

        with st.expander(f"Raw response: {platform_key}"):
            st.json(payload)
