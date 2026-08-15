"""Data access + business logic for the Job Market dashboard.

Data is the real "Ask a Manager" 2019 salary survey — a large, public,
crowd-sourced survey of self-reported job title, industry, experience,
location, and salary — see data/fetch_jobmarket_data.py for
provenance. It has no "skills required" field, so unlike the other
metrics (which are real), there is no skills-trend chart here (see
SESSION_LOG.md for why). "Responses" below means survey respondents,
not live job postings."""
import pandas as pd
import streamlit as st

DATA_PATH = "data/jobmarket_salaries.csv"

EXPERIENCE_ORDER = [
    "1 year or less", "2 - 4 years", "5 - 7 years", "8 - 10 years",
    "11 - 20 years", "21 - 30 years", "31 - 40 years", "41 years or more",
]


@st.cache_data
def load_data(path: str = DATA_PATH) -> pd.DataFrame:
    return pd.read_csv(path)


def filter_data(df, cities, industries, experience):
    return df[df["city"].isin(cities) & df["industry"].isin(industries) & df["experience"].isin(experience)].copy()


def compute_kpis(df: pd.DataFrame) -> dict:
    if df.empty:
        return {"avg_salary": 0, "top_industry": "-", "top_city": "-", "total_responses": 0}
    top_industry = df.groupby("industry")["salary"].mean().idxmax()
    top_city = df["city"].value_counts().idxmax()
    return {
        "avg_salary": df["salary"].mean(),
        "top_industry": top_industry,
        "top_city": top_city,
        "total_responses": len(df),
    }


def salary_by_industry(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    top = df["industry"].value_counts().head(n).index
    return (
        df[df["industry"].isin(top)]
        .groupby("industry")["salary"]
        .mean()
        .reset_index()
        .sort_values("salary", ascending=False)
    )


def responses_by_city(df: pd.DataFrame) -> pd.DataFrame:
    return df["city"].value_counts().reset_index(name="responses").rename(columns={"index": "city"})


def salary_by_experience(df: pd.DataFrame) -> pd.DataFrame:
    out = df.groupby("experience")["salary"].mean().reset_index()
    out["experience"] = pd.Categorical(out["experience"], categories=EXPERIENCE_ORDER, ordered=True)
    return out.sort_values("experience")


# --- Insights tab ---------------------------------------------------------

def top_industries(df: pd.DataFrame, n: int = 8):
    return df["industry"].value_counts().head(n).index


def salary_distribution_by_city(df: pd.DataFrame, n: int = 8) -> pd.DataFrame:
    top = df["city"].value_counts().head(n).index
    return df[df["city"].isin(top)]


def heatmap_industry_experience(df: pd.DataFrame) -> pd.DataFrame:
    top = top_industries(df)
    out = df[df["industry"].isin(top)]
    return out.groupby(["experience", "industry"])["salary"].mean().reset_index()


def industry_treemap(df: pd.DataFrame) -> pd.DataFrame:
    top = top_industries(df)
    out = df[df["industry"].isin(top)]
    return out.groupby(["industry", "experience"]).size().reset_index(name="responses")
