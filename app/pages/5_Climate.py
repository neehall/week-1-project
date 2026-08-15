import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

sys.path.append(str(Path(__file__).resolve().parents[1]))
from common.styling import apply_page_style, style_chart  # noqa: E402
from common import charts  # noqa: E402
from services import climate_service as svc  # noqa: E402

st.set_page_config(page_title="Climate Dashboard", layout="wide")
apply_page_style()
st.title("Climate Dashboard")

df = svc.load_data()

st.sidebar.header("Filters")
min_date, max_date = svc.date_bounds(df)
date_range = st.sidebar.date_input("Date range", [min_date, max_date])
cities = st.sidebar.multiselect("City", sorted(df["city"].unique()), default=sorted(df["city"].unique()))

if len(date_range) != 2:
    st.info("Select a start and end date.")
    st.stop()
start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
df_filtered = svc.filter_data(df, start_date, end_date, cities)

kpi = svc.compute_kpis(df_filtered)
k1, k2, k3, k4 = st.columns(4)
k1.metric("Avg AQI", f"{kpi['avg_aqi']:.0f}")
k2.metric("Worst City (avg)", kpi["worst_city"])
k3.metric("Unhealthy+ Days", f"{kpi['pct_unhealthy_days']:.1f}%")
yoy = kpi["yoy_change_pct"]
k4.metric("YoY Change (2023→2024)", f"{yoy:+.1f}%" if yoy is not None else "N/A")

if not df_filtered.empty:
    tab_overview, tab_insights = st.tabs(["Overview", "Insights"])

    with tab_overview:
        row1_left, row1_right = st.columns(2)
        with row1_left:
            st.markdown("**AQI Over Time**")
            fig = px.line(svc.aqi_over_time(df_filtered), x="date", y="aqi")
            st.plotly_chart(style_chart(fig), use_container_width=True)
        with row1_right:
            st.markdown("**Avg AQI by City**")
            fig = px.bar(svc.avg_aqi_by_city(df_filtered), x="city", y="aqi")
            st.plotly_chart(style_chart(fig), use_container_width=True)

        row2_left, row2_right = st.columns(2)
        with row2_left:
            st.markdown("**AQI Category Distribution**")
            fig = px.pie(svc.category_distribution(df_filtered), names="category", values="days")
            st.plotly_chart(style_chart(fig), use_container_width=True)
        with row2_right:
            st.markdown("**Top Pollution Spikes**")
            top = svc.top_spike_days(df_filtered)
            top["label"] = top["city"] + " — " + top["date"].dt.strftime("%Y-%m-%d")
            fig = px.bar(top.sort_values("aqi"), x="aqi", y="label", orientation="h")
            st.plotly_chart(style_chart(fig), use_container_width=True)

    with tab_insights:
        row1_left, row1_right = st.columns(2)
        with row1_left:
            st.markdown("**Seasonal Pattern: Avg AQI by Month**")
            months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
            fig = px.bar(svc.monthly_seasonal_pattern(df_filtered), x="month", y="aqi", category_orders={"month": months})
            st.plotly_chart(style_chart(fig), use_container_width=True)
        with row1_right:
            st.markdown("**Year-over-Year AQI by City**")
            fig = px.bar(svc.yoy_by_city(df_filtered), x="city", y="aqi", color="year", barmode="group")
            st.plotly_chart(style_chart(fig), use_container_width=True)

        row2_left, row2_right = st.columns(2)
        with row2_left:
            st.markdown("**AQI Heatmap: City x Month**")
            fig = charts.heatmap(svc.heatmap_city_month(df_filtered), x="month", y="city", z="aqi")
            st.plotly_chart(style_chart(fig), use_container_width=True)
        with row2_right:
            st.markdown("**Category Share by Defining Pollutant**")
            fig = charts.treemap(svc.pollutant_breakdown(df_filtered), path=["category", "defining_parameter"], values="days")
            st.plotly_chart(style_chart(fig), use_container_width=True)
else:
    st.info("No data for selected filters.")

with st.expander("Filtered data & download"):
    st.caption(
        "Real US EPA AirData (public domain) — daily AQI, 2023–2024, 20 US metros. "
        "No temperature column: EPA AirData doesn't publish it. See data/fetch_climate_data.py."
    )
    st.dataframe(df_filtered.reset_index(drop=True))
    csv = df_filtered.to_csv(index=False).encode("utf-8")
    st.download_button("Download filtered data as CSV", csv, "filtered_climate.csv", "text/csv")
