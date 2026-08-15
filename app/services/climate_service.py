"""Data access + business logic for the Climate/Air Quality dashboard.

Data is real US EPA AirData (public domain), not synthetic — see
data/fetch_climate_data.py for provenance. It covers AQI only; EPA
AirData does not publish temperature, so there is no temperature
metric here (see SESSION_LOG.md for why)."""
import pandas as pd
import streamlit as st

DATA_PATH = "data/climate_aqi.csv"

UNHEALTHY_THRESHOLD = 101  # AQI >= 101 is "Unhealthy for Sensitive Groups" or worse


@st.cache_data
def load_data(path: str = DATA_PATH) -> pd.DataFrame:
    return pd.read_csv(path, parse_dates=["date"])


def date_bounds(df: pd.DataFrame):
    return df["date"].min(), df["date"].max()


def filter_data(df, start_date, end_date, cities):
    mask = (df["date"] >= start_date) & (df["date"] <= end_date) & (df["city"].isin(cities))
    return df.loc[mask].copy()


def compute_kpis(df: pd.DataFrame) -> dict:
    if df.empty:
        return {"avg_aqi": 0, "worst_city": "-", "pct_unhealthy_days": 0, "yoy_change_pct": None}

    avg_aqi = df["aqi"].mean()
    worst_city = df.groupby("city")["aqi"].mean().idxmax()
    pct_unhealthy = (df["aqi"] >= UNHEALTHY_THRESHOLD).mean() * 100

    by_year = df.groupby(df["date"].dt.year)["aqi"].mean()
    yoy_change_pct = None
    if 2023 in by_year.index and 2024 in by_year.index and by_year[2023] != 0:
        yoy_change_pct = (by_year[2024] - by_year[2023]) / by_year[2023] * 100

    return {
        "avg_aqi": avg_aqi,
        "worst_city": worst_city,
        "pct_unhealthy_days": pct_unhealthy,
        "yoy_change_pct": yoy_change_pct,
    }


def aqi_over_time(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby("date")["aqi"].mean().reset_index()


def avg_aqi_by_city(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby("city")["aqi"].mean().reset_index().sort_values("aqi", ascending=False)


def category_distribution(df: pd.DataFrame) -> pd.DataFrame:
    return df["category"].value_counts().reset_index(name="days").rename(columns={"index": "category"})


def top_spike_days(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    return df.sort_values("aqi", ascending=False).head(n)[["date", "city", "aqi", "category", "defining_parameter"]]


# --- Insights tab ---------------------------------------------------------

def monthly_seasonal_pattern(df: pd.DataFrame) -> pd.DataFrame:
    """Average AQI by calendar month, collapsed across years — reveals the
    seasonal pattern (e.g. summer ozone/wildfire spikes) that a raw daily
    trend line buries in noise."""
    out = df.copy()
    out["month"] = out["date"].dt.month_name().str[:3]
    order = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    monthly = out.groupby("month")["aqi"].mean().reindex(order).reset_index()
    return monthly


def yoy_by_city(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["year"] = out["date"].dt.year.astype(str)
    return out.groupby(["city", "year"])["aqi"].mean().reset_index()


def heatmap_city_month(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["month"] = out["date"].dt.to_period("M").dt.to_timestamp()
    return out.groupby(["month", "city"])["aqi"].mean().reset_index()


def pollutant_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby(["category", "defining_parameter"]).size().reset_index(name="days")
