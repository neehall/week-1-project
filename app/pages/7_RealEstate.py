import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

sys.path.append(str(Path(__file__).resolve().parents[1]))
from common.styling import apply_page_style, style_chart  # noqa: E402
from common import charts  # noqa: E402
from services import realestate_service as svc  # noqa: E402

st.set_page_config(page_title="Real Estate Dashboard", layout="wide")
apply_page_style()
st.title("Real Estate Dashboard")

df = svc.load_data()

st.sidebar.header("Filters")
min_date, max_date = svc.date_bounds(df)
date_range = st.sidebar.date_input("Date range", [min_date, max_date])
cities = st.sidebar.multiselect("City", sorted(df["city"].unique()), default=sorted(df["city"].unique()))
bedrooms = st.sidebar.multiselect("Bedrooms", sorted(df["bedrooms"].unique()), default=sorted(df["bedrooms"].unique()))
price_min, price_max = int(df["zhvi"].min()), int(df["zhvi"].max())
price_range = st.sidebar.slider("Price range ($)", price_min, price_max, (price_min, price_max), step=10_000)

if len(date_range) != 2:
    st.info("Select a start and end date.")
    st.stop()
start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
df_filtered = svc.filter_data(df, start_date, end_date, cities, bedrooms)
df_filtered = df_filtered[df_filtered["zhvi"].between(price_range[0], price_range[1])]

kpi = svc.compute_kpis(df_filtered)
k1, k2, k3, k4 = st.columns(4)
k1.metric("Avg Home Value", f"${kpi['avg_price']:,.0f}")
yoy = kpi["yoy_change_pct"]
k2.metric("YoY Change", f"{yoy:+.1f}%" if yoy is not None else "N/A")
k3.metric("Priciest City", kpi["priciest_city"])
k4.metric("Most Affordable City", kpi["cheapest_city"])

if not df_filtered.empty:
    tab_overview, tab_insights = st.tabs(["Overview", "Insights"])

    with tab_overview:
        row1_left, row1_right = st.columns(2)
        with row1_left:
            st.markdown("**Home Value Trend Over Time**")
            fig = px.line(svc.price_trend(df_filtered), x="date", y="zhvi")
            st.plotly_chart(style_chart(fig), use_container_width=True)
        with row1_right:
            st.markdown("**Avg Home Value by City**")
            fig = px.bar(svc.avg_price_by_city(df_filtered), x="city", y="zhvi")
            st.plotly_chart(style_chart(fig), use_container_width=True)

        row2_left, row2_right = st.columns(2)
        with row2_left:
            st.markdown("**Avg Home Value by Bedrooms**")
            fig = px.bar(svc.avg_price_by_bedrooms(df_filtered), x="bedrooms", y="zhvi")
            st.plotly_chart(style_chart(fig), use_container_width=True)
        with row2_right:
            st.markdown("**Home Value by City (Map)**")
            map_data = svc.city_map_data(df_filtered)
            fig = px.scatter_geo(
                map_data, lat="lat", lon="lon", size="zhvi", color="zhvi",
                hover_name="city", scope="usa", color_continuous_scale="Blues",
            )
            st.plotly_chart(style_chart(fig), use_container_width=True)

    with tab_insights:
        row1_left, row1_right = st.columns(2)
        with row1_left:
            st.markdown("**YoY Price Change by City**")
            fig = px.bar(svc.yoy_change_by_city(df_filtered), x="city", y="yoy_pct")
            st.plotly_chart(style_chart(fig), use_container_width=True)
        with row1_right:
            st.markdown("**Price Trend by Bedroom Count**")
            fig = charts.stacked_area(svc.price_trend_by_bedrooms(df_filtered), x="date", y="zhvi", color="bedrooms")
            st.plotly_chart(style_chart(fig), use_container_width=True)

        row2_left, row2_right = st.columns(2)
        with row2_left:
            st.markdown("**Price Heatmap: City x Bedrooms**")
            fig = charts.heatmap(svc.heatmap_city_bedrooms(df_filtered), x="bedrooms", y="city", z="zhvi")
            st.plotly_chart(style_chart(fig), use_container_width=True)
        with row2_right:
            st.markdown("**Price Distribution**")
            fig = px.histogram(df_filtered, x="zhvi", nbins=30)
            st.plotly_chart(style_chart(fig), use_container_width=True)
else:
    st.info("No data for selected filters.")

with st.expander("Filtered data & download"):
    st.caption(
        "Real Zillow Home Value Index (ZHVI) data, Zillow Research public CSVs. "
        "ZHVI is a smoothed city-level value estimate (33rd-67th percentile tier), "
        "not individual listing prices — so there's no exact price-range filter or "
        "per-property map point; city centroids are used for the map. "
        "See data/fetch_realestate_data.py."
    )
    st.dataframe(df_filtered.reset_index(drop=True))
    csv = df_filtered.to_csv(index=False).encode("utf-8")
    st.download_button("Download filtered data as CSV", csv, "filtered_realestate.csv", "text/csv")
