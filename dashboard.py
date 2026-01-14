import pandas as pd
import streamlit as st

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
        return None, "Unknown request type."
    except Exception as exc:
        return None, f"{type(exc).__name__}: {exc}"


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


st.title("Signal Index")
st.caption("Live Korea chart API data (no database).")

all_platforms = list(PLATFORMS.keys())
request_type = "Korean Music Charts"

platform_choice = st.sidebar.selectbox(
    "Platform",
    ["All"] + all_platforms
)
platform = None if platform_choice == "All" else platform_choice

if st.sidebar.button("Refresh"):
    st.session_state["live_refresh"] = st.session_state.get("live_refresh", 0) + 1

refresh_key = st.session_state.get("live_refresh", 0)

kind_map = {
    "Korean Music Charts": ("chart", None)
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
        chart_df = payload_to_df(payload)
        if chart_df.empty:
            st.info("No data returned.")
        else:
            st.dataframe(chart_df, use_container_width=True)

        with st.expander(f"Raw response: {platform_key}"):
            st.json(payload)
