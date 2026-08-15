"""Data access + business logic for the Revenue dashboard.
Pages import from here; they never read sales_data.csv directly."""
import pandas as pd
import streamlit as st

DATA_PATH = "data/sales_data.csv"


@st.cache_data
def load_data(path: str = DATA_PATH) -> pd.DataFrame:
    return pd.read_csv(path, parse_dates=["order_date"])


def date_bounds(df: pd.DataFrame):
    return df["order_date"].min(), df["order_date"].max()


def filter_data(df, start_date, end_date, regions, categories, segments, product_search=""):
    mask = (
        (df["order_date"] >= start_date)
        & (df["order_date"] <= end_date)
        & (df["region"].isin(regions))
        & (df["category"].isin(categories))
        & (df["customer_segment"].isin(segments))
    )
    out = df.loc[mask].copy()
    if product_search:
        out = out[out["product_name"].str.contains(product_search, case=False, na=False)]
    return out


def compute_kpis(df: pd.DataFrame) -> dict:
    avg_discount = df["discount"].mean()
    return {
        "total_sales": df["sales"].sum(),
        "total_profit": df["profit"].sum(),
        "avg_discount": 0 if pd.isna(avg_discount) else avg_discount,
        "total_quantity": int(df["quantity"].sum() or 0),
    }


def sales_over_time(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby("order_date")["sales"].sum().reset_index()


def sales_by_region(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby("region")["sales"].sum().reset_index().sort_values("sales", ascending=False)


def sales_by_category(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby("category")["sales"].sum().reset_index().sort_values("sales", ascending=False)


def top_products(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    return (
        df.groupby("product_name")["sales"]
        .sum()
        .reset_index()
        .sort_values("sales", ascending=False)
        .head(n)
    )
