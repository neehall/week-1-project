"""
Downloads real, public daily Air Quality Index (AQI) data from the US EPA
AirData platform (https://aqs.epa.gov/aqsweb/airdata/download_files.html,
public domain) for 2023-2024, filters it down to a curated set of 20
well-known US metro counties, and writes data/climate_aqi.csv.

Source columns: State Name, county Name, State Code, County Code, Date,
AQI, Category, Defining Parameter, Defining Site, Number of Sites Reporting.
Note: this dataset does NOT include temperature — EPA AirData reports
pollutant-derived AQI only. The Climate dashboard focuses on what this
real data actually supports well: pollution spikes, seasonal patterns,
and year-over-year AQI change.

Re-run to refresh/re-derive (network required):
    python3 data/fetch_climate_data.py
"""
import io
import zipfile

import pandas as pd
import requests

YEARS = (2023, 2024)
URL_TEMPLATE = "https://aqs.epa.gov/aqsweb/airdata/daily_aqi_by_county_{year}.zip"

# County -> friendly "City, ST" label, for a readable, familiar set of cities.
CITIES = {
    ("California", "Los Angeles"): "Los Angeles, CA",
    ("Illinois", "Cook"): "Chicago, IL",
    ("Texas", "Harris"): "Houston, TX",
    ("Arizona", "Maricopa"): "Phoenix, AZ",
    ("California", "San Diego"): "San Diego, CA",
    ("Florida", "Miami-Dade"): "Miami, FL",
    ("Washington", "King"): "Seattle, WA",
    ("New York", "New York"): "New York, NY",
    ("Ohio", "Cuyahoga"): "Cleveland, OH",
    ("Michigan", "Wayne"): "Detroit, MI",
    ("Colorado", "Denver"): "Denver, CO",
    ("Utah", "Salt Lake"): "Salt Lake City, UT",
    ("Georgia", "Fulton"): "Atlanta, GA",
    ("Massachusetts", "Suffolk"): "Boston, MA",
    ("Texas", "Travis"): "Austin, TX",
    ("Texas", "Bexar"): "San Antonio, TX",
    ("Oregon", "Multnomah"): "Portland, OR",
    ("Pennsylvania", "Allegheny"): "Pittsburgh, PA",
    ("District Of Columbia", "District of Columbia"): "Washington, DC",
    ("California", "San Francisco"): "San Francisco, CA",
}


def fetch_year(year: int) -> pd.DataFrame:
    resp = requests.get(URL_TEMPLATE.format(year=year), timeout=60)
    resp.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
        name = [n for n in zf.namelist() if n.endswith(".csv")][0]
        with zf.open(name) as f:
            return pd.read_csv(f)


def main(path: str = "data/climate_aqi.csv"):
    frames = []
    for year in YEARS:
        df = fetch_year(year)
        df["key"] = list(zip(df["State Name"], df["county Name"]))
        df = df[df["key"].isin(CITIES.keys())].copy()
        df["city"] = df["key"].map(CITIES)
        frames.append(df)

    out = pd.concat(frames, ignore_index=True).rename(
        columns={
            "Date": "date",
            "AQI": "aqi",
            "Category": "category",
            "Defining Parameter": "defining_parameter",
            "State Name": "state",
        }
    )[["date", "city", "state", "aqi", "category", "defining_parameter"]]
    out = out.sort_values(["city", "date"]).reset_index(drop=True)
    out.to_csv(path, index=False)
    print(f"{path}: {len(out)} rows, {out['city'].nunique()} cities, {out['date'].min()}–{out['date'].max()}")


if __name__ == "__main__":
    main()
