"""Data access + business logic for the Real Estate dashboard.

Data is real Zillow Home Value Index (ZHVI) data — Zillow Research's
public CSVs — see data/fetch_realestate_data.py for provenance. ZHVI is
a smoothed, seasonally-adjusted city-level value estimate (33rd-67th
percentile home tier), not individual listing prices/addresses, so
there's no per-listing "price range" filter or exact map point; the
dashboard filters/aggregates at the city + bedroom-count level instead
and maps city centroids, not individual properties."""
import pandas as pd
import streamlit as st

DATA_PATH = "data/realestate_zhvi.csv"

# Public city-centroid coordinates (not from Zillow), used only to place
# each city on the map — same 20 cities as data/fetch_realestate_data.py.
CITY_COORDS = {
    "Los Angeles": (34.0522, -118.2437), "Chicago": (41.8781, -87.6298),
    "Houston": (29.7604, -95.3698), "Phoenix": (33.4484, -112.0740),
    "San Diego": (32.7157, -117.1611), "Miami": (25.7617, -80.1918),
    "Seattle": (47.6062, -122.3321), "New York": (40.7128, -74.0060),
    "Cleveland": (41.4993, -81.6944), "Detroit": (42.3314, -83.0458),
    "Denver": (39.7392, -104.9903), "Salt Lake City": (40.7608, -111.8910),
    "Atlanta": (33.7490, -84.3880), "Boston": (42.3601, -71.0589),
    "Austin": (30.2672, -97.7431), "San Antonio": (29.4241, -98.4936),
    "Portland": (45.5152, -122.6784), "Pittsburgh": (40.4406, -79.9959),
    "San Francisco": (37.7749, -122.4194), "Nashville": (36.1627, -86.7816),
}


@st.cache_data
def load_data(path: str = DATA_PATH) -> pd.DataFrame:
    return pd.read_csv(path, parse_dates=["date"])


def date_bounds(df: pd.DataFrame):
    return df["date"].min(), df["date"].max()


def filter_data(df, start_date, end_date, cities, bedrooms):
    mask = (
        (df["date"] >= start_date)
        & (df["date"] <= end_date)
        & (df["city"].isin(cities))
        & (df["bedrooms"].isin(bedrooms))
    )
    return df.loc[mask].copy()


def compute_kpis(df: pd.DataFrame) -> dict:
    if df.empty:
        return {"avg_price": 0, "yoy_change_pct": None, "priciest_city": "-", "cheapest_city": "-"}

    avg_price = df["zhvi"].mean()
    by_city = df.groupby("city")["zhvi"].mean()
    priciest, cheapest = by_city.idxmax(), by_city.idxmin()

    by_year = df.groupby(df["date"].dt.year)["zhvi"].mean()
    years = sorted(by_year.index)
    yoy = None
    if len(years) >= 2 and by_year[years[-2]] != 0:
        yoy = (by_year[years[-1]] - by_year[years[-2]]) / by_year[years[-2]] * 100

    return {"avg_price": avg_price, "yoy_change_pct": yoy, "priciest_city": priciest, "cheapest_city": cheapest}


def price_trend(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby("date")["zhvi"].mean().reset_index()


def avg_price_by_city(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby("city")["zhvi"].mean().reset_index().sort_values("zhvi", ascending=False)


def avg_price_by_bedrooms(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby("bedrooms")["zhvi"].mean().reset_index().sort_values("bedrooms")


def city_map_data(df: pd.DataFrame) -> pd.DataFrame:
    out = df.groupby("city")["zhvi"].mean().reset_index()
    out["lat"] = out["city"].map(lambda c: CITY_COORDS.get(c, (None, None))[0])
    out["lon"] = out["city"].map(lambda c: CITY_COORDS.get(c, (None, None))[1])
    return out.dropna(subset=["lat", "lon"])


# --- Insights tab ---------------------------------------------------------

def yoy_change_by_city(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["year"] = out["date"].dt.year
    by_city_year = out.groupby(["city", "year"])["zhvi"].mean().reset_index()
    years = sorted(by_city_year["year"].unique())
    if len(years) < 2:
        return pd.DataFrame(columns=["city", "yoy_pct"])
    latest, prior = years[-1], years[-2]
    pivot = by_city_year.pivot(index="city", columns="year", values="zhvi")
    pivot = pivot.dropna(subset=[latest, prior])
    result = ((pivot[latest] - pivot[prior]) / pivot[prior] * 100).reset_index()
    result.columns = ["city", "yoy_pct"]
    return result.sort_values("yoy_pct", ascending=False)


def price_trend_by_bedrooms(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["bedrooms"] = out["bedrooms"].astype(str) + " BR"
    return out.groupby(["date", "bedrooms"])["zhvi"].mean().reset_index()


def heatmap_city_bedrooms(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["bedrooms"] = out["bedrooms"].astype(str) + " BR"
    return out.groupby(["bedrooms", "city"])["zhvi"].mean().reset_index()
