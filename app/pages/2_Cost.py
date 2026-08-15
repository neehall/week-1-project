import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

sys.path.append(str(Path(__file__).resolve().parents[1]))
from common.styling import apply_page_style, style_chart  # noqa: E402
from services import cost_service as svc  # noqa: E402

st.set_page_config(page_title="Cost Dashboard", layout="wide")
apply_page_style()
st.title("Cost Dashboard")

df = svc.load_data()

st.sidebar.header("Filters")
min_date, max_date = svc.date_bounds(df)
date_range = st.sidebar.date_input("Date range", [min_date, max_date])
regions = st.sidebar.multiselect("Region", sorted(df["region"].unique()), default=sorted(df["region"].unique()))
categories = st.sidebar.multiselect(
    "Cost category", sorted(df["cost_category"].unique()), default=sorted(df["cost_category"].unique())
)

if len(date_range) != 2:
    st.info("Select a start and end date.")
    st.stop()
start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
df_filtered = svc.filter_data(df, start_date, end_date, regions, categories)

kpi = svc.compute_kpis(df_filtered)
k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Cost", f"${kpi['total_cost']:,.2f}")
k2.metric("Avg Monthly Cost", f"${kpi['avg_monthly_cost']:,.2f}")
k3.metric("Regions", kpi["n_regions"])
k4.metric("Top Category", kpi["top_category"])

if not df_filtered.empty:
    row1_left, row1_right = st.columns(2)
    with row1_left:
        st.markdown("**Cost Over Time**")
        fig = px.line(svc.cost_over_time(df_filtered), x="date", y="amount")
        st.plotly_chart(style_chart(fig), use_container_width=True)
    with row1_right:
        st.markdown("**Cost by Region**")
        fig = px.bar(svc.cost_by_region(df_filtered), x="region", y="amount")
        st.plotly_chart(style_chart(fig), use_container_width=True)

    row2_left, row2_right = st.columns(2)
    with row2_left:
        st.markdown("**Cost by Category**")
        fig = px.pie(svc.cost_by_category(df_filtered), names="cost_category", values="amount")
        st.plotly_chart(style_chart(fig), use_container_width=True)
    with row2_right:
        st.markdown("**Region x Category Breakdown**")
        fig = px.bar(
            svc.cost_breakdown_by_region_category(df_filtered),
            x="region",
            y="amount",
            color="cost_category",
        )
        st.plotly_chart(style_chart(fig), use_container_width=True)
else:
    st.info("No data for selected filters.")

with st.expander("Filtered data & download"):
    st.dataframe(df_filtered.reset_index(drop=True))
    csv = df_filtered.to_csv(index=False).encode("utf-8")
    st.download_button("Download filtered data as CSV", csv, "filtered_cost.csv", "text/csv")
