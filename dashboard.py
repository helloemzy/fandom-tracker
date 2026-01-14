import os
from datetime import datetime
import pandas as pd
import plotly.express as px
import streamlit as st

from app.config import load_metrics_config, load_watchlist, load_templates
from app.db import get_engine, init_db
from app.ingest import run_demo_ingest
from app.queries import (
    load_observations_df,
    latest_observations,
    metric_timeseries,
    data_health
)


st.set_page_config(
    page_title="Signal Index",
    page_icon="📊",
    layout="wide"
)


@st.cache_data(ttl=300)
def load_data(version_key=None):
    engine = get_engine()
    return load_observations_df(engine)


def get_db_version():
    db_path = os.getenv("SIGNAL_INDEX_DB", "data/app.db")
    return os.path.getmtime(db_path) if os.path.exists(db_path) else None


def ensure_demo_data(engine):
    try:
        count = pd.read_sql("SELECT COUNT(*) AS count FROM observations", engine)["count"][0]
    except Exception:
        count = 0
    if count == 0:
        run_demo_ingest()


def format_value(value_num, value_text, unit):
    if unit == "ordinal" and value_text:
        return value_text
    if value_num is None or pd.isna(value_num):
        return "-"
    if unit == "rank_1_100":
        return f"#{int(value_num)}"
    if unit == "percent":
        return f"{value_num:.1f}%"
    if unit in {"count", "units"}:
        return f"{int(value_num):,}"
    if unit in {"score", "composite_score"}:
        return f"{value_num:.1f}"
    return f"{value_num}"


engine = init_db(get_engine())
ensure_demo_data(engine)

pillars_config, metrics_config = load_metrics_config()
watchlist = load_watchlist()
templates = load_templates()

st.title("Signal Index")
st.caption("Metrics-driven tracking across Impact, Fandom Power, and Value")

st.sidebar.header("Data Controls")
if st.sidebar.button("Refresh Demo Data"):
    with st.spinner("Loading demo data..."):
        rows = run_demo_ingest()
        st.cache_data.clear()
        st.success(f"Loaded {rows} demo observations.")
        st.rerun()

page = st.sidebar.radio(
    "Navigate",
    [
        "Overview",
        "Artist Detail",
        "Comparisons",
        "Content Planner",
        "Data Health"
    ]
)

observations = load_data(get_db_version())

if observations.empty:
    st.warning("No observations loaded yet. Use 'Refresh Demo Data' to load the demo CSV.")
    st.stop()

latest_df = latest_observations(observations)

latest_date = observations["date"].max()
if pd.notna(latest_date):
    st.info(f"Latest data date: {latest_date}")


if page == "Overview":
    st.subheader("Latest Snapshot")

    pillar_keys = list(pillars_config.keys())
    selected_pillar = st.selectbox(
        "Pillar",
        pillar_keys,
        format_func=lambda k: pillars_config.get(k, k)
    )

    pillar_metric_keys = [
        key for key, meta in metrics_config.items() if meta["pillar"] == selected_pillar
    ]

    snapshot = latest_df[latest_df["metric_key"].isin(pillar_metric_keys)].copy()
    snapshot["metric"] = snapshot["metric_key"].map(
        lambda k: metrics_config[k]["display_name"]
    )
    snapshot["value_display"] = snapshot.apply(
        lambda row: format_value(row["value_num"], row["value_text"], row["unit"]),
        axis=1
    )

    pivot = snapshot.pivot(index="person", columns="metric", values="value_display")
    st.dataframe(pivot, use_container_width=True)

    st.subheader("Metric Trend")
    metric_key = st.selectbox(
        "Metric",
        pillar_metric_keys,
        format_func=lambda k: metrics_config[k]["display_name"]
    )

    trend_df = metric_timeseries(observations, metric_key)
    if trend_df.empty:
        st.info("No history for this metric yet.")
    else:
        fig = px.line(
            trend_df,
            x="date",
            y="value_num",
            color="person",
            markers=True,
            labels={"value_num": metrics_config[metric_key]["display_name"]}
        )
        if metrics_config[metric_key]["directionality"] == "lower_is_better":
            fig.update_yaxes(autorange="reversed")
        st.plotly_chart(fig, use_container_width=True)

elif page == "Artist Detail":
    st.subheader("Artist Detail")
    people = sorted(observations["person"].unique().tolist())
    selected_person = st.selectbox("Artist", people)

    tabs = st.tabs([pillars_config[k] for k in pillars_config.keys()])
    for tab, pillar_key in zip(tabs, pillars_config.keys()):
        with tab:
            metric_keys = [
                key for key, meta in metrics_config.items() if meta["pillar"] == pillar_key
            ]
            for metric_key in metric_keys:
                metric_label = metrics_config[metric_key]["display_name"]
                person_metric = metric_timeseries(
                    observations,
                    metric_key,
                    people=[selected_person]
                )
                if person_metric.empty:
                    continue
                fig = px.line(
                    person_metric,
                    x="date",
                    y="value_num",
                    markers=True,
                    labels={"value_num": metric_label}
                )
                if metrics_config[metric_key]["directionality"] == "lower_is_better":
                    fig.update_yaxes(autorange="reversed")
                st.markdown(f"**{metric_label}**")
                st.plotly_chart(fig, use_container_width=True)

elif page == "Comparisons":
    st.subheader("Compare Artists")
    metric_key = st.selectbox(
        "Metric",
        list(metrics_config.keys()),
        format_func=lambda k: metrics_config[k]["display_name"]
    )
    people = sorted(observations["person"].unique().tolist())
    selected_people = st.multiselect("Artists", people, default=people[:3])

    compare_df = metric_timeseries(observations, metric_key, selected_people)
    if compare_df.empty:
        st.info("No data available for this metric.")
    else:
        fig = px.line(
            compare_df,
            x="date",
            y="value_num",
            color="person",
            markers=True,
            labels={"value_num": metrics_config[metric_key]["display_name"]}
        )
        if metrics_config[metric_key]["directionality"] == "lower_is_better":
            fig.update_yaxes(autorange="reversed")
        st.plotly_chart(fig, use_container_width=True)

        latest_compare = latest_df[latest_df["metric_key"] == metric_key].copy()
        latest_compare["value_display"] = latest_compare.apply(
            lambda row: format_value(row["value_num"], row["value_text"], row["unit"]),
            axis=1
        )
        st.dataframe(
            latest_compare[["person", "value_display"]].set_index("person"),
            use_container_width=True
        )

elif page == "Content Planner":
    st.subheader("Content Planner")
    template_labels = [t["label"] for t in templates]
    template_choice = st.selectbox("Template", template_labels)

    selected_template = next(
        (t for t in templates if t["label"] == template_choice),
        templates[0]
    )

    people = sorted(observations["person"].unique().tolist())
    selected_person = st.selectbox("Artist", people)
    metric_key = st.selectbox(
        "Metric",
        list(metrics_config.keys()),
        format_func=lambda k: metrics_config[k]["display_name"]
    )

    latest_metric = latest_df[
        (latest_df["person"] == selected_person) &
        (latest_df["metric_key"] == metric_key)
    ]

    value_display = "-"
    if not latest_metric.empty:
        row = latest_metric.iloc[0]
        value_display = format_value(row["value_num"], row["value_text"], row["unit"])

    filled = selected_template["body"].format(
        name=selected_person,
        metric=metrics_config[metric_key]["display_name"],
        value=value_display,
        pillar=pillars_config[metrics_config[metric_key]["pillar"]],
        date=latest_date
    )

    st.text_area("Generated Post", filled, height=160)

elif page == "Data Health":
    st.subheader("Data Health")
    health_df = data_health(observations, metrics_config)
    if health_df.empty:
        st.info("No data loaded yet.")
    else:
        health_df["status"] = health_df["days_since"].apply(
            lambda d: "ok" if d <= 1 else "stale"
        )
        health_df = health_df[[
            "display_name",
            "cadence",
            "last_date",
            "days_since",
            "status"
        ]]
        st.dataframe(health_df, use_container_width=True)
