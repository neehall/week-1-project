"""Data access + business logic for the Gaming (Valorant) dashboard.

Data is real, live-scraped Valorant competitive stats from blitz.gg via
github.com/IronicNinja/valorant-stats — see data/fetch_gaming_data.py
for provenance. It's an aggregate snapshot (per agent/map/rank), not
individual match-by-match history, so there's no calendar-time
dimension; the dashboard uses rank tier (Iron -> Diamond) as its trend
axis instead of fabricating dates (see SESSION_LOG.md for why)."""
import pandas as pd
import streamlit as st

AGENT_PATH = "data/gaming_agent_stats.csv"
MAP_PATH = "data/gaming_map_stats.csv"

RANK_ORDER = [
    "Iron 1", "Iron 2", "Iron 3",
    "Bronze 1", "Bronze 2", "Bronze 3",
    "Silver 1", "Silver 2", "Silver 3",
    "Gold 1", "Gold 2", "Gold 3",
    "Platinum 1", "Platinum 2", "Platinum 3",
    "Diamond 1", "Diamond 2", "Diamond 3",
]


@st.cache_data
def load_agent_data(path: str = AGENT_PATH) -> pd.DataFrame:
    return pd.read_csv(path)


@st.cache_data
def load_map_data(path: str = MAP_PATH) -> pd.DataFrame:
    return pd.read_csv(path)


def filter_agent_data(df, maps, ranks, agents):
    mask = df["map"].isin(maps) & df["rank"].isin(ranks) & df["agent"].isin(agents)
    return df.loc[mask].copy()


def filter_map_data(df, ranks):
    return df.loc[df["rank"].isin(ranks)].copy()


def compute_kpis(agent_df: pd.DataFrame) -> dict:
    if agent_df.empty:
        return {"avg_kd": 0, "avg_win_rate": 0, "top_agent": "-", "total_matches": 0}
    top_agent = agent_df.groupby("agent")["win_rate"].mean().idxmax()
    return {
        "avg_kd": agent_df["kd"].mean(),
        "avg_win_rate": agent_df["win_rate"].mean(),
        "top_agent": top_agent,
        "total_matches": int(agent_df["num_matches"].sum()),
    }


def kd_by_agent(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby("agent")["kd"].mean().reset_index().sort_values("kd", ascending=False)


def win_rate_by_agent(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby("agent")["win_rate"].mean().reset_index().sort_values("win_rate", ascending=False)


def pick_rate_by_agent(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    return (
        df.groupby("agent")["pick_rate"]
        .mean()
        .reset_index()
        .sort_values("pick_rate", ascending=False)
        .head(n)
    )


def map_win_rates(map_df: pd.DataFrame) -> pd.DataFrame:
    return map_df.groupby("map")[["atk_win_pct", "def_win_pct"]].mean().reset_index()


# --- Insights tab ---------------------------------------------------------

def win_rate_by_rank(df: pd.DataFrame, top_n_agents: int = 6) -> pd.DataFrame:
    """Win rate progression across skill tiers — the "trend" axis this
    dataset actually supports, in place of a calendar-time trend."""
    top_agents = df.groupby("agent")["num_matches"].sum().sort_values(ascending=False).head(top_n_agents).index
    out = df[df["agent"].isin(top_agents)]
    return out.groupby(["rank", "agent"])["win_rate"].mean().reset_index()


def kd_vs_winrate(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby("agent").agg(kd=("kd", "mean"), win_rate=("win_rate", "mean"), matches=("num_matches", "sum")).reset_index()


def heatmap_agent_map(df: pd.DataFrame) -> pd.DataFrame:
    return df[df["map"] != "All Maps"].groupby(["map", "agent"])["win_rate"].mean().reset_index()


def map_pickrate_treemap(df: pd.DataFrame) -> pd.DataFrame:
    out = df[df["map"] != "All Maps"].copy()
    return out.groupby(["map", "agent"])["pick_rate"].mean().reset_index()
