"""
Downloads the real USAID SCMS (Supply Chain Management System) Delivery
History Dataset — public health-commodity shipment records, originally
published via USAID/data.gov, mirrored as a plain CSV at
github.com/jrcinco/supply-chain-shipment-price-data — and derives
delivery-performance fields from it.

Writes data/logistics_shipments.csv with columns:
    country, region, shipment_mode, product_group, vendor,
    scheduled_date, delivered_date, delay_days, status (On Time/Delayed),
    quantity, line_item_value, weight_kg, freight_cost_usd

This dataset covers real shipments (mode, country, scheduled vs. actual
delivery dates, freight cost, weight) but has no warehouse/inventory
dimension, so there's no "stock levels over time" here — the dashboard
focuses on what's real: delivery times by region, on-time vs. delayed
rates, and shipment-mode/freight cost patterns. See SESSION_LOG.md.

Re-run to refresh (network required):
    python3 data/fetch_logistics_data.py
"""
import pandas as pd
import requests

URL = "https://raw.githubusercontent.com/jrcinco/supply-chain-shipment-price-data/master/SCMS_Delivery_History_Dataset.csv"

# Country -> region, for the 43 countries in this dataset.
REGION_MAP = {
    "Afghanistan": "Asia", "Kazakhstan": "Asia", "Kyrgyzstan": "Asia",
    "Pakistan": "Asia", "Vietnam": "Asia",
    "Lebanon": "Middle East & North Africa", "Libya": "Middle East & North Africa",
    "Belize": "Latin America & Caribbean", "Dominican Republic": "Latin America & Caribbean",
    "Guatemala": "Latin America & Caribbean", "Guyana": "Latin America & Caribbean",
    "Haiti": "Latin America & Caribbean",
}
DEFAULT_REGION = "Sub-Saharan Africa"  # all other countries in this dataset


def main(path: str = "data/logistics_shipments.csv"):
    resp = requests.get(URL, timeout=60)
    resp.raise_for_status()
    df = pd.read_csv(pd.io.common.StringIO(resp.text), encoding="utf-8-sig")

    df["scheduled_date"] = pd.to_datetime(df["Scheduled Delivery Date"], format="%d-%b-%y", errors="coerce")
    df["delivered_date"] = pd.to_datetime(df["Delivered to Client Date"], format="%d-%b-%y", errors="coerce")
    df = df.dropna(subset=["scheduled_date", "delivered_date"])

    df["delay_days"] = (df["delivered_date"] - df["scheduled_date"]).dt.days
    df["status"] = df["delay_days"].apply(lambda d: "On Time" if d <= 0 else "Delayed")
    df["region"] = df["Country"].map(lambda c: REGION_MAP.get(c, DEFAULT_REGION))
    df["freight_cost_usd"] = pd.to_numeric(df["Freight Cost (USD)"], errors="coerce")

    out = df.rename(
        columns={
            "Country": "country",
            "Shipment Mode": "shipment_mode",
            "Product Group": "product_group",
            "Vendor": "vendor",
            "Line Item Quantity": "quantity",
            "Line Item Value": "line_item_value",
            "Weight (Kilograms)": "weight_kg",
        }
    )[
        [
            "country", "region", "shipment_mode", "product_group", "vendor",
            "scheduled_date", "delivered_date", "delay_days", "status",
            "quantity", "line_item_value", "weight_kg", "freight_cost_usd",
        ]
    ]
    out = out.dropna(subset=["shipment_mode"])
    out.to_csv(path, index=False)
    print(f"{path}: {len(out)} rows, {out['country'].nunique()} countries, {out['scheduled_date'].min()}–{out['scheduled_date'].max()}")


if __name__ == "__main__":
    main()
