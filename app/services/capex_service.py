"""Data access + business logic for the Capex dashboard."""
import pandas as pd
import streamlit as st

DATA_PATH = "data/capex_data.csv"


@st.cache_data
def load_data(path: str = DATA_PATH) -> pd.DataFrame:
    return pd.read_csv(path, parse_dates=["date"])


def date_bounds(df: pd.DataFrame):
    return df["date"].min(), df["date"].max()


def filter_data(df, start_date, end_date, regions, asset_categories):
    mask = (
        (df["date"] >= start_date)
        & (df["date"] <= end_date)
        & (df["region"].isin(regions))
        & (df["asset_category"].isin(asset_categories))
    )
    return df.loc[mask].copy()


def compute_kpis(df: pd.DataFrame) -> dict:
    return {
        "total_capex": df["amount"].sum(),
        "n_projects": len(df),
        "avg_project_size": df["amount"].mean() if not df.empty else 0,
        "largest_project": df["amount"].max() if not df.empty else 0,
    }


def capex_over_time(df: pd.DataFrame) -> pd.DataFrame:
    monthly = df.set_index("date").resample("MS")["amount"].sum().reset_index()
    return monthly


def capex_by_region(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby("region")["amount"].sum().reset_index().sort_values("amount", ascending=False)


def capex_by_asset_category(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby("asset_category")["amount"].sum().reset_index().sort_values("amount", ascending=False)


def top_projects(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    return df.sort_values("amount", ascending=False).head(n)[["project_name", "region", "asset_category", "amount"]]
