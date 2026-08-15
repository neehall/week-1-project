import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

sys.path.append(str(Path(__file__).resolve().parents[1]))
from common.styling import apply_page_style, style_chart  # noqa: E402
from common import charts  # noqa: E402
from services import logistics_service as svc  # noqa: E402

st.set_page_config(page_title="Logistics Dashboard", layout="wide")
apply_page_style()
st.title("Logistics Dashboard")

df = svc.load_data()

st.sidebar.header("Filters")
min_date, max_date = svc.date_bounds(df)
date_range = st.sidebar.date_input("Scheduled date range", [min_date, max_date])
regions = st.sidebar.multiselect("Region", sorted(df["region"].unique()), default=sorted(df["region"].unique()))
modes = st.sidebar.multiselect("Shipment mode", sorted(df["shipment_mode"].unique()), default=sorted(df["shipment_mode"].unique()))

if len(date_range) != 2:
    st.info("Select a start and end date.")
    st.stop()
start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
df_filtered = svc.filter_data(df, start_date, end_date, regions, modes)

kpi = svc.compute_kpis(df_filtered)
k1, k2, k3, k4 = st.columns(4)
k1.metric("On-Time Rate", f"{kpi['on_time_rate']:.1f}%")
k2.metric("Avg Delay", f"{kpi['avg_delay']:+.1f} days")
k3.metric("Avg Freight Cost", f"${kpi['avg_freight']:,.0f}")
k4.metric("Total Shipments", f"{kpi['total_shipments']:,}")

if not df_filtered.empty:
    tab_overview, tab_insights = st.tabs(["Overview", "Insights"])

    with tab_overview:
        row1_left, row1_right = st.columns(2)
        with row1_left:
            st.markdown("**Delivery Status by Region**")
            fig = px.bar(svc.status_by_region(df_filtered), x="region", y="shipments", color="status", barmode="stack")
            st.plotly_chart(style_chart(fig), use_container_width=True)
        with row1_right:
            st.markdown("**Avg Delay by Region**")
            fig = px.bar(svc.avg_delay_by_region(df_filtered), x="region", y="delay_days")
            st.plotly_chart(style_chart(fig), use_container_width=True)

        row2_left, row2_right = st.columns(2)
        with row2_left:
            st.markdown("**Shipment Mode Distribution**")
            fig = px.pie(svc.mode_distribution(df_filtered), names="shipment_mode", values="shipments")
            st.plotly_chart(style_chart(fig), use_container_width=True)
        with row2_right:
            st.markdown("**Avg Freight Cost by Mode**")
            fig = px.bar(svc.freight_by_mode(df_filtered), x="shipment_mode", y="freight_cost_usd")
            st.plotly_chart(style_chart(fig), use_container_width=True)

    with tab_insights:
        row1_left, row1_right = st.columns(2)
        with row1_left:
            st.markdown("**On-Time Rate by Year**")
            fig = px.line(svc.on_time_rate_by_year(df_filtered), x="year", y="on_time_rate", markers=True)
            st.plotly_chart(style_chart(fig), use_container_width=True)
        with row1_right:
            st.markdown("**Delay Heatmap: Region x Mode**")
            fig = charts.heatmap(svc.delay_heatmap_region_mode(df_filtered), x="shipment_mode", y="region", z="delay_days")
            st.plotly_chart(style_chart(fig), use_container_width=True)

        row2_left, row2_right = st.columns(2)
        with row2_left:
            st.markdown("**Shipment Volume Share: Region > Product Group**")
            fig = charts.treemap(svc.product_group_treemap(df_filtered), path=["region", "product_group"], values="quantity")
            st.plotly_chart(style_chart(fig), use_container_width=True)
        with row2_right:
            st.markdown("**Freight Cost by Country — 80/20 (Pareto)**")
            fig = charts.pareto(svc.freight_pareto_by_country(df_filtered), "country", "freight_cost_usd")
            st.plotly_chart(style_chart(fig), use_container_width=True)
else:
    st.info("No data for selected filters.")

with st.expander("Filtered data & download"):
    st.caption(
        "Real USAID SCMS Delivery History Dataset (public health-commodity shipments). "
        "No warehouse/inventory dimension in this real data, so there's no stock-levels "
        "metric here. ~40% of freight cost values are text placeholders "
        "(e.g. 'Freight Included in Commodity Cost') in the source data and are excluded "
        "from freight cost charts. See data/fetch_logistics_data.py."
    )
    st.dataframe(df_filtered.reset_index(drop=True))
    csv = df_filtered.to_csv(index=False).encode("utf-8")
    st.download_button("Download filtered data as CSV", csv, "filtered_logistics.csv", "text/csv")
