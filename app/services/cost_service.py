"""Data access + business logic for the Cost dashboard."""
import pandas as pd
import streamlit as st

DATA_PATH = "data/cost_data.csv"


@st.cache_data
def load_data(path: str = DATA_PATH) -> pd.DataFrame:
    return pd.read_csv(path, parse_dates=["date"])


def date_bounds(df: pd.DataFrame):
    return df["date"].min(), df["date"].max()


def filter_data(df, start_date, end_date, regions, categories):
    mask = (
        (df["date"] >= start_date)
        & (df["date"] <= end_date)
        & (df["region"].isin(regions))
        & (df["cost_category"].isin(categories))
    )
    return df.loc[mask].copy()


def compute_kpis(df: pd.DataFrame) -> dict:
    total = df["amount"].sum()
    n_months = df["date"].nunique() or 1
    return {
        "total_cost": total,
        "avg_monthly_cost": total / n_months,
        "n_regions": df["region"].nunique(),
        "top_category": (df.groupby("cost_category")["amount"].sum().idxmax() if not df.empty else "-"),
    }


def cost_over_time(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby("date")["amount"].sum().reset_index()


def cost_by_region(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby("region")["amount"].sum().reset_index().sort_values("amount", ascending=False)


def cost_by_category(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby("cost_category")["amount"].sum().reset_index().sort_values("amount", ascending=False)


def cost_breakdown_by_region_category(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby(["region", "cost_category"])["amount"].sum().reset_index()


# --- Insights tab ---------------------------------------------------------

def cost_trend_by_category(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby(["date", "cost_category"])["amount"].sum().reset_index()


def cost_heatmap_region_month(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["month"] = out["date"].dt.to_period("M").dt.to_timestamp()
    return out.groupby(["month", "region"])["amount"].sum().reset_index()


def cost_region_category_treemap(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby(["region", "cost_category"])["amount"].sum().reset_index()
