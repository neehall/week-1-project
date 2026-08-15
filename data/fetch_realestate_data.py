"""
Downloads real Zillow Home Value Index (ZHVI) data — Zillow Research's
public, free, no-auth CSVs (https://www.zillow.com/research/data/) —
segmented by bedroom count, for a curated list of major US cities, and
reshapes the wide monthly columns into a long time series.

Writes data/realestate_zhvi.csv with columns:
    city, state, metro, bedrooms, date, zhvi

ZHVI is Zillow's smoothed, seasonally-adjusted estimate of home value
for the 33rd-67th percentile tier of homes in each city (their
methodology, not a raw individual-listing price) - it does not include
per-listing fields like an exact price or a specific address/map
point, so this dashboard aggregates at city level rather than mapping
individual properties. See data/README notes / SESSION_LOG.md.

Re-run to refresh (network required, ~200MB total download):
    python3 data/fetch_realestate_data.py
"""
import io

import pandas as pd
import requests

BASE = "https://files.zillowstatic.com/research/public_csvs/zhvi"
BEDROOMS = [1, 2, 3, 4, 5]
MIN_DATE = "2020-01-01"

# (city, state) -> keep only these, to keep the dataset a manageable size.
# Reuses the same well-known metro list as the Climate dashboard where
# possible, for a consistent set of cities across dashboards.
CITIES = {
    ("Los Angeles", "CA"), ("Chicago", "IL"), ("Houston", "TX"), ("Phoenix", "AZ"),
    ("San Diego", "CA"), ("Miami", "FL"), ("Seattle", "WA"), ("New York", "NY"),
    ("Cleveland", "OH"), ("Detroit", "MI"), ("Denver", "CO"), ("Salt Lake City", "UT"),
    ("Atlanta", "GA"), ("Boston", "MA"), ("Austin", "TX"), ("San Antonio", "TX"),
    ("Portland", "OR"), ("Pittsburgh", "PA"), ("San Francisco", "CA"), ("Nashville", "TN"),
}


def fetch_bedroom(bedrooms: int) -> pd.DataFrame:
    url = f"{BASE}/City_zhvi_bdrmcnt_{bedrooms}_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv"
    resp = requests.get(url, timeout=120)
    resp.raise_for_status()
    df = pd.read_csv(io.StringIO(resp.text))
    df = df[df.apply(lambda r: (r["RegionName"], r["State"]) in CITIES, axis=1)]

    date_cols = [c for c in df.columns if c[:4].isdigit()]
    long = df.melt(
        id_vars=["RegionName", "State", "Metro"],
        value_vars=date_cols,
        var_name="date",
        value_name="zhvi",
    )
    long = long[long["date"] >= MIN_DATE]
    long["bedrooms"] = bedrooms
    long = long.rename(columns={"RegionName": "city", "State": "state", "Metro": "metro"})
    return long.dropna(subset=["zhvi"])


if __name__ == "__main__":
    frames = [fetch_bedroom(b) for b in BEDROOMS]
    out = pd.concat(frames, ignore_index=True)
    out = out[["city", "state", "metro", "bedrooms", "date", "zhvi"]].sort_values(["city", "bedrooms", "date"])
    out.to_csv("data/realestate_zhvi.csv", index=False)
    print(f"data/realestate_zhvi.csv: {len(out)} rows, {out['city'].nunique()} cities, {out['date'].min()}–{out['date'].max()}")
