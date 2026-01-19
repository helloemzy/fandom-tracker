import pandas as pd
import streamlit as st

from connectors.billboard_api import BILLBOARD_CHARTS, fetch_chart as fetch_billboard_chart
from connectors.korea_chart_api import fetch_chart, PLATFORMS
from connectors.youtube_music_charts_api import fetch_music_charts


st.set_page_config(
    page_title="Signal Index",
    page_icon="📊",
    layout="wide"
)


@st.cache_data(ttl=60)
def load_korea_payload(platform, refresh_key=0):
    try:
        return fetch_chart(platform), None
    except Exception as exc:
        return None, f"{type(exc).__name__}: {exc}"


@st.cache_data(ttl=21600)
def load_billboard_payload(chart_name, options, refresh_key=0):
    try:
        options = options or {}
        return fetch_billboard_chart(
            chart_name,
            date=options.get("date"),
            year=options.get("year")
        ), None
    except Exception as exc:
        return None, f"{type(exc).__name__}: {exc}"


@st.cache_data(ttl=900)
def load_youtube_payload(region_code, max_results, api_key, refresh_key=0):
    try:
        return fetch_music_charts(
            region_code=region_code,
            max_results=max_results,
            api_key=api_key
        ), None
    except Exception as exc:
        return None, f"{type(exc).__name__}: {exc}"


def payload_to_df(payload):
    if not payload:
        return pd.DataFrame()
    if isinstance(payload, list):
        return pd.DataFrame(payload)
    if isinstance(payload, dict):
        entries = payload.get("entries")
        if isinstance(entries, list):
            return pd.DataFrame(entries)
        data = payload.get("data")
        if isinstance(data, list):
            return pd.DataFrame(data)
        return pd.DataFrame([payload])
    return pd.DataFrame()


@st.cache_data(ttl=900)
def load_comeback_feed(csv_path="data/comeback_feed.csv"):
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        return pd.DataFrame()
    except Exception as exc:
        st.error(f"Comeback feed load failed: {type(exc).__name__}: {exc}")
        return pd.DataFrame()

    if df.empty:
        return df

    if "pub_date" in df.columns:
        df["pub_date"] = pd.to_datetime(df["pub_date"], errors="coerce", utc=True)
        df = df.sort_values("pub_date", ascending=False)

    return df


st.title("Signal Index")
st.caption("Live Korea + Billboard chart API data (no database).")

all_platforms = list(PLATFORMS.keys())
request_type = st.sidebar.radio(
    "Data Source",
    ["Korean Music Charts", "Billboard Charts", "YouTube Music Charts"]
)

if request_type == "Korean Music Charts":
    platform_choice = st.sidebar.selectbox(
        "Platform",
        ["All"] + all_platforms
    )
    platform = None if platform_choice == "All" else platform_choice
    billboard_date = None
    billboard_year = None
    youtube_region = None
    youtube_max_results = None
else:
    billboard_date = None
    billboard_year = None
    if request_type == "Billboard Charts":
        chart_choice = st.sidebar.radio(
            "Billboard Charts",
            ["Select a chart..."] + BILLBOARD_CHARTS,
            index=0
        )
        platform = None if chart_choice == "Select a chart..." else chart_choice
        billboard_date = st.sidebar.text_input("Billboard date (YYYY-MM-DD)", value="").strip()
        billboard_year = st.sidebar.text_input("Billboard year (YYYY)", value="").strip()
        youtube_region = None
        youtube_max_results = None
    else:
        platform = "youtube"
        youtube_region = st.sidebar.text_input("Region code", value="US").strip().upper()
        youtube_max_results = st.sidebar.slider("Max results", min_value=10, max_value=50, value=50, step=5)

if st.sidebar.button("Refresh"):
    st.session_state["live_refresh"] = st.session_state.get("live_refresh", 0) + 1

refresh_key = st.session_state.get("live_refresh", 0)

payloads = {}
errors = {}

if platform is None and request_type == "Billboard Charts":
    st.info("Select a Billboard chart from the sidebar to load data.")
elif platform is None:
    if request_type == "Korean Music Charts":
        platform_keys = all_platforms
    else:
        platform_keys = BILLBOARD_CHARTS
    total = len(platform_keys)
    progress = st.progress(0)
    status = st.empty()
    for current, platform_key in enumerate(platform_keys, start=1):
        status.text(f"Loading {platform_key} ({current}/{total})...")
        progress.progress(current / total)
        if request_type == "Billboard Charts":
            options = {
                "date": billboard_date or None,
                "year": None if billboard_date else (billboard_year or None)
            }
            payload, error = load_billboard_payload(platform_key, options, refresh_key)
        else:
            payload, error = load_korea_payload(platform_key, refresh_key)
        if error:
            errors[platform_key] = error
        else:
            payloads[platform_key] = payload
    status.empty()
    progress.empty()
else:
    if request_type == "Billboard Charts":
        options = {
            "date": billboard_date or None,
            "year": None if billboard_date else (billboard_year or None)
        }
        payload, error = load_billboard_payload(platform, options, refresh_key)
    elif request_type == "YouTube Music Charts":
        api_key = None
        try:
            api_key = st.secrets.get("YOUTUBE_API_KEY")
        except Exception:
            api_key = None
        payload, error = load_youtube_payload(
            youtube_region or "US",
            youtube_max_results or 50,
            api_key,
            refresh_key
        )
        platform = "YouTube Music Charts"
    else:
        payload, error = load_korea_payload(platform, refresh_key)
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
        if request_type == "Billboard Charts" and isinstance(payload, dict):
            title = payload.get("title") or platform_key
            date = payload.get("date")
            subtitle = f"{title} ({date})" if date else title
            st.subheader(subtitle)
        elif request_type == "YouTube Music Charts":
            st.subheader(platform_key)
        else:
            st.subheader(f"{platform_key.capitalize()} Chart")
        chart_df = payload_to_df(payload)
        if chart_df.empty:
            st.info("No data returned.")
        else:
            st.dataframe(chart_df, use_container_width=True)

        with st.expander(f"Raw response: {platform_key}"):
            st.json(payload)

st.subheader("Upcoming Kpop Comebacks")
comeback_df = load_comeback_feed()
if comeback_df.empty:
    st.info("No comeback feed data yet. Run the RSS workflow to populate.")
else:
    columns = [col for col in ["pub_date", "title", "link", "source"] if col in comeback_df.columns]
    st.dataframe(comeback_df[columns].head(50), use_container_width=True)
