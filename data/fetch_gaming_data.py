"""
Downloads real Valorant competitive statistics — scraped from blitz.gg
and published by github.com/IronicNinja/valorant-stats (MIT-licensed
public repo, updated periodically) — and reshapes them into two CSVs:

  data/gaming_agent_stats.csv  — per agent, per map, per rank tier:
      K/D, kills, deaths, assists, win rate, pick rate, ACS, first
      blood %, matches played.
  data/gaming_map_stats.csv    — per map, per rank tier: play rate,
      attack/defense win rate, matches played.

There is no calendar-time dimension in this data (it's a live snapshot,
not match-by-match history), so the Gaming dashboard uses rank tier
(skill progression, Iron -> Diamond) as its trend axis instead of
fabricating dates next to real numbers. See SESSION_LOG.md for why.

Re-run to refresh (network required):
    python3 data/fetch_gaming_data.py
"""
import pandas as pd
import requests

BASE = "https://raw.githubusercontent.com/IronicNinja/valorant-stats/master"
MAPS = ["all", "ascent", "bind", "breeze", "haven", "icebox", "split"]
TIERS = list(range(3, 21))  # Iron 1 through Diamond 3

# Riot's public competitive-tier enum.
RANK_NAMES = {
    3: "Iron 1", 4: "Iron 2", 5: "Iron 3",
    6: "Bronze 1", 7: "Bronze 2", 8: "Bronze 3",
    9: "Silver 1", 10: "Silver 2", 11: "Silver 3",
    12: "Gold 1", 13: "Gold 2", 14: "Gold 3",
    15: "Platinum 1", 16: "Platinum 2", 17: "Platinum 3",
    18: "Diamond 1", 19: "Diamond 2", 20: "Diamond 3",
}
RANK_ORDER = [RANK_NAMES[t] for t in TIERS]


def _pct(series: pd.Series) -> pd.Series:
    return series.astype(str).str.rstrip("%").astype(float)


def _num(series: pd.Series) -> pd.Series:
    return series.astype(str).str.replace(",", "").astype(float)


def fetch_agent_stats() -> pd.DataFrame:
    frames = []
    for game_map in MAPS:
        for tier in TIERS:
            url = f"{BASE}/agents_data/{game_map}/agents_competitive_tier={tier}.csv"
            resp = requests.get(url, timeout=30)
            if resp.status_code != 200:
                continue
            df = pd.read_csv(pd.io.common.StringIO(resp.text))
            df["map"] = "All Maps" if game_map == "all" else game_map.title()
            df["rank_tier"] = tier
            df["rank"] = RANK_NAMES[tier]
            frames.append(df)
    out = pd.concat(frames, ignore_index=True)
    out = out.rename(
        columns={
            "Agent Name": "agent",
            "KD": "kd",
            "Kills": "kills",
            "Deaths": "deaths",
            "Assists": "assists",
            "ACS": "acs",
        }
    )
    out["win_rate"] = _pct(out["Win Rate"])
    out["pick_rate"] = _pct(out["Pick Rate"])
    out["first_blood_pct"] = _pct(out["First Blood"])
    out["num_matches"] = _num(out["Num Matches"]).astype(int)
    return out[
        [
            "map", "rank_tier", "rank", "agent", "kd", "kills", "deaths", "assists",
            "win_rate", "pick_rate", "acs", "first_blood_pct", "num_matches",
        ]
    ]


def fetch_map_stats() -> pd.DataFrame:
    frames = []
    for tier in TIERS:
        url = f"{BASE}/map_data/maps_competitive_tier={tier}.csv"
        resp = requests.get(url, timeout=30)
        if resp.status_code != 200:
            continue
        df = pd.read_csv(pd.io.common.StringIO(resp.text))
        df["rank_tier"] = tier
        df["rank"] = RANK_NAMES[tier]
        frames.append(df)
    out = pd.concat(frames, ignore_index=True)
    out = out.rename(columns={"Map Name": "map"})
    out["play_rate"] = _pct(out["Play Rate"])
    out["atk_win_pct"] = _pct(out["Atk Win"])
    out["def_win_pct"] = _pct(out["Def Win"])
    out["num_matches"] = _num(out["Num Matches"]).astype(int)
    return out[["map", "rank_tier", "rank", "play_rate", "atk_win_pct", "def_win_pct", "num_matches"]]


if __name__ == "__main__":
    agent_stats = fetch_agent_stats()
    agent_stats.to_csv("data/gaming_agent_stats.csv", index=False)
    print(f"data/gaming_agent_stats.csv: {len(agent_stats)} rows")

    map_stats = fetch_map_stats()
    map_stats.to_csv("data/gaming_map_stats.csv", index=False)
    print(f"data/gaming_map_stats.csv: {len(map_stats)} rows")
