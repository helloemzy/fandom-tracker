import pandas as pd
from datetime import date, timedelta


def load_demo_observations(path="data/demo_observations.csv", shift_to_today=True):
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["date"]).dt.date

    if shift_to_today and not df.empty:
        max_date = df["date"].max()
        offset = date.today() - max_date
        df["date"] = df["date"].apply(lambda d: d + offset)

    return df
