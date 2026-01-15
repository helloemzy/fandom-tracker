import pandas as pd
import streamlit as st

from connectors.billboard_api import BILLBOARD_CHARTS, fetch_chart as fetch_billboard_chart
from connectors.korea_chart_api import fetch_chart, PLATFORMS


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
        if kind == "billboard":
            options = value or {}
            return fetch_billboard_chart(
                platform,
                date=options.get("date"),
                year=options.get("year")
            ), None
        return None, "Unknown request type."
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


st.title("Signal Index")
st.caption("Live Korea + Billboard chart API data (no database).")

all_platforms = list(PLATFORMS.keys())
request_type = st.sidebar.selectbox(
    "Data Source",
    ["Korean Music Charts", "Billboard Charts"]
)

if request_type == "Korean Music Charts":
    platform_choice = st.sidebar.selectbox(
        "Platform",
        ["All"] + all_platforms
    )
    platform = None if platform_choice == "All" else platform_choice
    chart_choice = None
    billboard_date = None
    billboard_year = None
else:
    chart_choice = st.sidebar.selectbox(
        "Chart",
        ["All"] + BILLBOARD_CHARTS
    )
    platform = None if chart_choice == "All" else chart_choice
    billboard_date = st.sidebar.text_input("Billboard date (YYYY-MM-DD)", value="").strip()
    billboard_year = st.sidebar.text_input("Billboard year (YYYY)", value="").strip()

if st.sidebar.button("Refresh"):
    st.session_state["live_refresh"] = st.session_state.get("live_refresh", 0) + 1

refresh_key = st.session_state.get("live_refresh", 0)

kind_map = {
    "Korean Music Charts": ("chart", None),
    "Billboard Charts": ("billboard", None)
}

kind, value = kind_map[request_type]
payloads = {}
errors = {}

if platform is None:
    if request_type == "Korean Music Charts":
        platform_keys = all_platforms
    else:
        platform_keys = BILLBOARD_CHARTS
    for platform_key in platform_keys:
        if request_type == "Billboard Charts":
            options = {
                "date": billboard_date or None,
                "year": None if billboard_date else (billboard_year or None)
            }
            value = options
        payload, error = load_live_payload(kind, platform_key, value, refresh_key)
        if error:
            errors[platform_key] = error
        else:
            payloads[platform_key] = payload
else:
    if request_type == "Billboard Charts":
        options = {
            "date": billboard_date or None,
            "year": None if billboard_date else (billboard_year or None)
        }
        value = options
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
        if request_type == "Billboard Charts" and isinstance(payload, dict):
            title = payload.get("title") or platform_key
            date = payload.get("date")
            subtitle = f"{title} ({date})" if date else title
            st.subheader(subtitle)
        else:
            st.subheader(f"{platform_key.capitalize()} Chart")
        chart_df = payload_to_df(payload)
        if chart_df.empty:
            st.info("No data returned.")
        else:
            st.dataframe(chart_df, use_container_width=True)

        with st.expander(f"Raw response: {platform_key}"):
            st.json(payload)
