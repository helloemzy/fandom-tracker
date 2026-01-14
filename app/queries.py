import pandas as pd
from datetime import date
from app.db import get_engine


def load_observations_df(engine=None):
    engine = engine or get_engine()
    query = """
        SELECT
            p.person_key,
            p.display_name AS person,
            p.category,
            o.metric_key,
            o.pillar,
            o.source,
            o.date,
            o.value_num,
            o.value_text,
            o.unit
        FROM observations o
        JOIN people p ON p.id = o.person_id
    """
    df = pd.read_sql(query, engine)
    if not df.empty:
        df["date"] = pd.to_datetime(df["date"]).dt.date
    return df


def latest_observations(df):
    if df.empty:
        return df
    df_sorted = df.sort_values("date")
    return df_sorted.groupby(["person", "metric_key"], as_index=False).tail(1)


def metric_timeseries(df, metric_key, people=None):
    if df.empty:
        return df
    mask = df["metric_key"] == metric_key
    if people:
        mask &= df["person"].isin(people)
    return df.loc[mask].sort_values("date")


def compute_latest_deltas(df):
    if df.empty:
        return df
    df_sorted = df.sort_values("date")
    grouped = df_sorted.groupby(["person", "metric_key"], as_index=False)
    latest = grouped.tail(1)
    previous = grouped.nth(-2).reset_index()
    merged = latest.merge(
        previous[["person", "metric_key", "value_num"]],
        on=["person", "metric_key"],
        how="left",
        suffixes=("", "_prev")
    )
    merged["delta"] = merged["value_num"] - merged["value_num_prev"]
    return merged


def data_health(df, metrics_config):
    if df.empty:
        return pd.DataFrame(columns=["metric_key", "last_date", "days_since"])

    latest_dates = (
        df.groupby("metric_key")["date"]
        .max()
        .reset_index()
        .rename(columns={"date": "last_date"})
    )
    today = date.today()
    latest_dates["days_since"] = latest_dates["last_date"].apply(lambda d: (today - d).days)
    latest_dates["display_name"] = latest_dates["metric_key"].map(
        lambda key: metrics_config[key]["display_name"]
    )
    latest_dates["cadence"] = latest_dates["metric_key"].map(
        lambda key: metrics_config[key]["cadence"]
    )
    return latest_dates
