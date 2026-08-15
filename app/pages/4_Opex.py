import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

sys.path.append(str(Path(__file__).resolve().parents[1]))
from common.styling import apply_page_style, style_chart  # noqa: E402
from common import charts  # noqa: E402
from services import opex_service as svc  # noqa: E402

st.set_page_config(page_title="Opex Dashboard", layout="wide")
apply_page_style()
st.title("Opex Dashboard")

df = svc.load_data()

st.sidebar.header("Filters")
min_date, max_date = svc.date_bounds(df)
date_range = st.sidebar.date_input("Date range", [min_date, max_date])
regions = st.sidebar.multiselect("Region", sorted(df["region"].unique()), default=sorted(df["region"].unique()))
departments = st.sidebar.multiselect(
    "Department", sorted(df["department"].unique()), default=sorted(df["department"].unique())
)

if len(date_range) != 2:
    st.info("Select a start and end date.")
    st.stop()
start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
df_filtered = svc.filter_data(df, start_date, end_date, regions, departments)

kpi = svc.compute_kpis(df_filtered)
k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Opex", f"${kpi['total_opex']:,.2f}")
k2.metric("Avg Monthly Opex", f"${kpi['avg_monthly_opex']:,.2f}")
k3.metric("Departments", kpi["n_departments"])
k4.metric("Top Expense Type", kpi["top_expense_type"])

if not df_filtered.empty:
    tab_overview, tab_insights = st.tabs(["Overview", "Insights"])

    with tab_overview:
        row1_left, row1_right = st.columns(2)
        with row1_left:
            st.markdown("**Opex Over Time**")
            fig = px.line(svc.opex_over_time(df_filtered), x="date", y="amount")
            st.plotly_chart(style_chart(fig), use_container_width=True)
        with row1_right:
            st.markdown("**Opex by Department**")
            fig = px.bar(svc.opex_by_department(df_filtered), x="department", y="amount")
            st.plotly_chart(style_chart(fig), use_container_width=True)

        row2_left, row2_right = st.columns(2)
        with row2_left:
            st.markdown("**Opex by Expense Type**")
            fig = px.pie(svc.opex_by_expense_type(df_filtered), names="expense_type", values="amount")
            st.plotly_chart(style_chart(fig), use_container_width=True)
        with row2_right:
            st.markdown("**Expense Type by Department**")
            fig = px.bar(
                df_filtered.groupby(["department", "expense_type"])["amount"].sum().reset_index(),
                x="department",
                y="amount",
                color="expense_type",
            )
            fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0))
            st.plotly_chart(style_chart(fig), use_container_width=True)

    with tab_insights:
        row1_left, row1_right = st.columns(2)
        with row1_left:
            st.markdown("**Opex Trend by Expense Type**")
            fig = charts.stacked_area(svc.opex_trend_by_expense_type(df_filtered), x="date", y="amount", color="expense_type")
            st.plotly_chart(style_chart(fig), use_container_width=True)
        with row1_right:
            st.markdown("**Opex Heatmap: Department x Expense Type**")
            fig = charts.heatmap(svc.opex_heatmap_department_expense(df_filtered), x="expense_type", y="department", z="amount")
            st.plotly_chart(style_chart(fig), use_container_width=True)

        row2_left, row2_right = st.columns(2)
        with row2_left:
            st.markdown("**Opex Share: Department > Expense Type**")
            fig = charts.treemap(svc.department_expense_treemap(df_filtered), path=["department", "expense_type"], values="amount")
            st.plotly_chart(style_chart(fig), use_container_width=True)
        with row2_right:
            st.markdown("**Opex by Expense Type — 80/20 (Pareto)**")
            fig = charts.pareto(df_filtered, "expense_type", "amount")
            st.plotly_chart(style_chart(fig), use_container_width=True)
else:
    st.info("No data for selected filters.")

with st.expander("Filtered data & download"):
    st.dataframe(df_filtered.reset_index(drop=True))
    csv = df_filtered.to_csv(index=False).encode("utf-8")
    st.download_button("Download filtered data as CSV", csv, "filtered_opex.csv", "text/csv")
