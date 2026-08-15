import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

sys.path.append(str(Path(__file__).resolve().parents[1]))
from common.styling import apply_page_style, style_chart  # noqa: E402
from common import charts  # noqa: E402
from services import revenue_service as svc  # noqa: E402

st.set_page_config(page_title="Revenue Dashboard", layout="wide")
apply_page_style()
st.title("Revenue Dashboard")

df = svc.load_data()

st.sidebar.header("Filters")
min_date, max_date = svc.date_bounds(df)
date_range = st.sidebar.date_input("Order date range", [min_date, max_date])
regions = st.sidebar.multiselect("Region", sorted(df["region"].unique()), default=sorted(df["region"].unique()))
categories = st.sidebar.multiselect("Category", sorted(df["category"].unique()), default=sorted(df["category"].unique()))
segments = st.sidebar.multiselect(
    "Customer segment", sorted(df["customer_segment"].unique()), default=sorted(df["customer_segment"].unique())
)
product_search = st.sidebar.text_input("Search product name (contains)")

if len(date_range) != 2:
    st.info("Select a start and end date.")
    st.stop()
start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
df_filtered = svc.filter_data(df, start_date, end_date, regions, categories, segments, product_search)

kpi = svc.compute_kpis(df_filtered)
k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Sales", f"${kpi['total_sales']:,.2f}")
k2.metric("Total Profit", f"${kpi['total_profit']:,.2f}")
k3.metric("Avg Discount", f"{kpi['avg_discount'] * 100:.1f}%")
k4.metric("Total Quantity", kpi["total_quantity"])

if not df_filtered.empty:
    tab_overview, tab_insights = st.tabs(["Overview", "Insights"])

    with tab_overview:
        row1_left, row1_right = st.columns(2)
        with row1_left:
            st.markdown("**Sales Over Time**")
            fig = px.line(svc.sales_over_time(df_filtered), x="order_date", y="sales")
            st.plotly_chart(style_chart(fig), use_container_width=True)
        with row1_right:
            st.markdown("**Sales by Region**")
            fig = px.bar(svc.sales_by_region(df_filtered), x="region", y="sales")
            st.plotly_chart(style_chart(fig), use_container_width=True)

        row2_left, row2_right = st.columns(2)
        with row2_left:
            st.markdown("**Sales by Category**")
            fig = px.pie(svc.sales_by_category(df_filtered), names="category", values="sales")
            st.plotly_chart(style_chart(fig), use_container_width=True)
        with row2_right:
            st.markdown("**Top Products**")
            top = svc.top_products(df_filtered)
            fig = px.bar(top.sort_values("sales"), x="sales", y="product_name", orientation="h")
            st.plotly_chart(style_chart(fig), use_container_width=True)

    with tab_insights:
        row1_left, row1_right = st.columns(2)
        with row1_left:
            st.markdown("**Profit Margin by Category**")
            margin = svc.profit_margin_by_category(df_filtered)
            fig = px.bar(margin, x="category", y="margin_pct", color="margin_pct", color_continuous_scale="RdYlGn")
            st.plotly_chart(style_chart(fig), use_container_width=True)
        with row1_right:
            st.markdown("**Sales Trend by Category**")
            fig = charts.stacked_area(svc.sales_trend_by_category(df_filtered), x="month", y="sales", color="category")
            st.plotly_chart(style_chart(fig), use_container_width=True)

        row2_left, row2_right = st.columns(2)
        with row2_left:
            st.markdown("**Sales Heatmap: Region x Month**")
            fig = charts.heatmap(svc.monthly_sales_by_region(df_filtered), x="month", y="region", z="sales")
            st.plotly_chart(style_chart(fig), use_container_width=True)
        with row2_right:
            st.markdown("**Top Products — 80/20 (Pareto)**")
            fig = charts.pareto(df_filtered, "product_name", "sales")
            st.plotly_chart(style_chart(fig), use_container_width=True)
else:
    st.info("No data for selected filters.")

with st.expander("Filtered data & download"):
    st.dataframe(df_filtered.reset_index(drop=True))
    csv = df_filtered.to_csv(index=False).encode("utf-8")
    st.download_button("Download filtered data as CSV", csv, "filtered_revenue.csv", "text/csv")
