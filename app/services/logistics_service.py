"""Data access + business logic for the Logistics dashboard.

Data is the real USAID SCMS Delivery History Dataset (public health-
commodity shipments) — see data/fetch_logistics_data.py for
provenance. It covers real shipment mode, country/region, scheduled vs.
actual delivery dates, and freight cost, but has no warehouse/inventory
dimension, so there is no "stock levels over time" metric here (see
SESSION_LOG.md for why)."""
import pandas as pd
import streamlit as st

DATA_PATH = "data/logistics_shipments.csv"


@st.cache_data
def load_data(path: str = DATA_PATH) -> pd.DataFrame:
    return pd.read_csv(path, parse_dates=["scheduled_date", "delivered_date"])


def date_bounds(df: pd.DataFrame):
    return df["scheduled_date"].min(), df["scheduled_date"].max()


def filter_data(df, start_date, end_date, regions, modes):
    mask = (
        (df["scheduled_date"] >= start_date)
        & (df["scheduled_date"] <= end_date)
        & (df["region"].isin(regions))
        & (df["shipment_mode"].isin(modes))
    )
    return df.loc[mask].copy()


def compute_kpis(df: pd.DataFrame) -> dict:
    if df.empty:
        return {"on_time_rate": 0, "avg_delay": 0, "avg_freight": 0, "total_shipments": 0}
    return {
        "on_time_rate": (df["status"] == "On Time").mean() * 100,
        "avg_delay": df["delay_days"].mean(),
        "avg_freight": df["freight_cost_usd"].mean(),
        "total_shipments": len(df),
    }


def status_by_region(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby(["region", "status"]).size().reset_index(name="shipments")


def avg_delay_by_region(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby("region")["delay_days"].mean().reset_index().sort_values("delay_days", ascending=False)


def mode_distribution(df: pd.DataFrame) -> pd.DataFrame:
    return df["shipment_mode"].value_counts().reset_index(name="shipments").rename(columns={"index": "shipment_mode"})


def freight_by_mode(df: pd.DataFrame) -> pd.DataFrame:
    return df.dropna(subset=["freight_cost_usd"]).groupby("shipment_mode")["freight_cost_usd"].mean().reset_index()


# --- Insights tab ---------------------------------------------------------

def on_time_rate_by_year(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["year"] = out["scheduled_date"].dt.year
    return out.groupby("year")["status"].apply(lambda s: (s == "On Time").mean() * 100).reset_index(name="on_time_rate")


def delay_heatmap_region_mode(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby(["region", "shipment_mode"])["delay_days"].mean().reset_index()


def product_group_treemap(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby(["region", "product_group"])["quantity"].sum().reset_index()


def freight_pareto_by_country(df: pd.DataFrame):
    return df.dropna(subset=["freight_cost_usd"])
