import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

sys.path.append(str(Path(__file__).resolve().parents[1]))
from common.styling import apply_page_style, style_chart  # noqa: E402
from common import charts  # noqa: E402
from services import capex_service as svc  # noqa: E402

st.set_page_config(page_title="Capex Dashboard", layout="wide")
apply_page_style()
st.title("Capex Dashboard")

df = svc.load_data()

st.sidebar.header("Filters")
min_date, max_date = svc.date_bounds(df)
date_range = st.sidebar.date_input("Date range", [min_date, max_date])
regions = st.sidebar.multiselect("Region", sorted(df["region"].unique()), default=sorted(df["region"].unique()))
asset_categories = st.sidebar.multiselect(
    "Asset category", sorted(df["asset_category"].unique()), default=sorted(df["asset_category"].unique())
)

if len(date_range) != 2:
    st.info("Select a start and end date.")
    st.stop()
start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
df_filtered = svc.filter_data(df, start_date, end_date, regions, asset_categories)

kpi = svc.compute_kpis(df_filtered)
k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Capex", f"${kpi['total_capex']:,.2f}")
k2.metric("Projects", kpi["n_projects"])
k3.metric("Avg Project Size", f"${kpi['avg_project_size']:,.2f}")
k4.metric("Largest Project", f"${kpi['largest_project']:,.2f}")

if not df_filtered.empty:
    tab_overview, tab_insights = st.tabs(["Overview", "Insights"])

    with tab_overview:
        row1_left, row1_right = st.columns(2)
        with row1_left:
            st.markdown("**Capex Over Time**")
            fig = px.bar(svc.capex_over_time(df_filtered), x="date", y="amount")
            st.plotly_chart(style_chart(fig), use_container_width=True)
        with row1_right:
            st.markdown("**Capex by Region**")
            fig = px.bar(svc.capex_by_region(df_filtered), x="region", y="amount")
            st.plotly_chart(style_chart(fig), use_container_width=True)

        row2_left, row2_right = st.columns(2)
        with row2_left:
            st.markdown("**Capex by Asset Category**")
            fig = px.pie(svc.capex_by_asset_category(df_filtered), names="asset_category", values="amount")
            st.plotly_chart(style_chart(fig), use_container_width=True)
        with row2_right:
            st.markdown("**Top Projects**")
            top = svc.top_projects(df_filtered)
            fig = px.bar(top.sort_values("amount"), x="amount", y="project_name", orientation="h")
            st.plotly_chart(style_chart(fig), use_container_width=True)

    with tab_insights:
        row1_left, row1_right = st.columns(2)
        with row1_left:
            st.markdown("**Cumulative Capex Over Time**")
            fig = px.area(svc.cumulative_capex_over_time(df_filtered), x="date", y="cumulative")
            st.plotly_chart(style_chart(fig), use_container_width=True)
        with row1_right:
            st.markdown("**Capex Heatmap: Region x Asset Category**")
            fig = charts.heatmap(svc.capex_heatmap_region_asset(df_filtered), x="asset_category", y="region", z="amount")
            st.plotly_chart(style_chart(fig), use_container_width=True)

        row2_left, row2_right = st.columns(2)
        with row2_left:
            st.markdown("**Capex Share: Region > Asset Category**")
            fig = charts.treemap(svc.region_asset_treemap(df_filtered), path=["region", "asset_category"], values="amount")
            st.plotly_chart(style_chart(fig), use_container_width=True)
        with row2_right:
            st.markdown("**Top Projects — 80/20 (Pareto)**")
            fig = charts.pareto(df_filtered, "project_name", "amount")
            st.plotly_chart(style_chart(fig), use_container_width=True)
else:
    st.info("No data for selected filters.")

with st.expander("Filtered data & download"):
    st.dataframe(df_filtered.reset_index(drop=True))
    csv = df_filtered.to_csv(index=False).encode("utf-8")
    st.download_button("Download filtered data as CSV", csv, "filtered_capex.csv", "text/csv")
