"""Data access + business logic for the Opex dashboard."""
import pandas as pd
import streamlit as st

DATA_PATH = "data/opex_data.csv"


@st.cache_data
def load_data(path: str = DATA_PATH) -> pd.DataFrame:
    return pd.read_csv(path, parse_dates=["date"])


def date_bounds(df: pd.DataFrame):
    return df["date"].min(), df["date"].max()


def filter_data(df, start_date, end_date, regions, departments):
    mask = (
        (df["date"] >= start_date)
        & (df["date"] <= end_date)
        & (df["region"].isin(regions))
        & (df["department"].isin(departments))
    )
    return df.loc[mask].copy()


def compute_kpis(df: pd.DataFrame) -> dict:
    total = df["amount"].sum()
    n_months = df["date"].nunique() or 1
    return {
        "total_opex": total,
        "avg_monthly_opex": total / n_months,
        "n_departments": df["department"].nunique(),
        "top_expense_type": (df.groupby("expense_type")["amount"].sum().idxmax() if not df.empty else "-"),
    }


def opex_over_time(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby("date")["amount"].sum().reset_index()


def opex_by_department(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby("department")["amount"].sum().reset_index().sort_values("amount", ascending=False)


def opex_by_expense_type(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby("expense_type")["amount"].sum().reset_index().sort_values("amount", ascending=False)
