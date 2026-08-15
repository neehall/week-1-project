import sys
from pathlib import Path

import plotly.express as px
import streamlit as st

sys.path.append(str(Path(__file__).resolve().parents[1]))
from common.styling import apply_page_style, style_chart  # noqa: E402
from common import charts  # noqa: E402
from services import jobmarket_service as svc  # noqa: E402

st.set_page_config(page_title="Job Market Dashboard", layout="wide")
apply_page_style()
st.title("Job Market Dashboard")

df = svc.load_data()

st.sidebar.header("Filters")
cities = st.sidebar.multiselect("City", sorted(df["city"].unique()), default=sorted(df["city"].unique()))
top_industries_default = list(svc.top_industries(df, n=8))
industries = st.sidebar.multiselect("Industry", sorted(df["industry"].unique()), default=top_industries_default)
experience = st.sidebar.multiselect("Experience", svc.EXPERIENCE_ORDER, default=svc.EXPERIENCE_ORDER)

df_filtered = svc.filter_data(df, cities, industries, experience)

kpi = svc.compute_kpis(df_filtered)
k1, k2, k3, k4 = st.columns(4)
k1.metric("Avg Salary", f"${kpi['avg_salary']:,.0f}")
k2.metric("Top-Paying Industry", kpi["top_industry"])
k3.metric("Most Represented City", kpi["top_city"])
k4.metric("Total Responses", f"{kpi['total_responses']:,}")

if not df_filtered.empty:
    tab_overview, tab_insights = st.tabs(["Overview", "Insights"])

    with tab_overview:
        row1_left, row1_right = st.columns(2)
        with row1_left:
            st.markdown("**Salary Distribution**")
            fig = px.histogram(df_filtered, x="salary", nbins=30)
            st.plotly_chart(style_chart(fig), use_container_width=True)
        with row1_right:
            st.markdown("**Avg Salary by Industry**")
            fig = px.bar(svc.salary_by_industry(df_filtered), x="industry", y="salary")
            st.plotly_chart(style_chart(fig), use_container_width=True)

        row2_left, row2_right = st.columns(2)
        with row2_left:
            st.markdown("**Responses by City (Demand)**")
            fig = px.bar(svc.responses_by_city(df_filtered), x="city", y="responses")
            st.plotly_chart(style_chart(fig), use_container_width=True)
        with row2_right:
            st.markdown("**Avg Salary by Experience**")
            fig = px.bar(svc.salary_by_experience(df_filtered), x="experience", y="salary")
            st.plotly_chart(style_chart(fig), use_container_width=True)

    with tab_insights:
        row1_left, row1_right = st.columns(2)
        with row1_left:
            st.markdown("**Salary Range by City**")
            fig = px.box(svc.salary_distribution_by_city(df_filtered), x="city", y="salary")
            st.plotly_chart(style_chart(fig), use_container_width=True)
        with row1_right:
            st.markdown("**Salary Heatmap: Industry x Experience**")
            fig = charts.heatmap(svc.heatmap_industry_experience(df_filtered), x="experience", y="industry", z="salary")
            st.plotly_chart(style_chart(fig), use_container_width=True)

        row2_left, row2_right = st.columns(2)
        with row2_left:
            st.markdown("**Most Common Job Titles — 80/20 (Pareto)**")
            title_counts = df_filtered["job_title"].value_counts().reset_index()
            title_counts.columns = ["job_title", "count"]
            fig = charts.pareto(title_counts, "job_title", "count")
            st.plotly_chart(style_chart(fig), use_container_width=True)
        with row2_right:
            st.markdown("**Responses Share: Industry > Experience**")
            fig = charts.treemap(svc.industry_treemap(df_filtered), path=["industry", "experience"], values="responses")
            st.plotly_chart(style_chart(fig), use_container_width=True)
else:
    st.info("No data for selected filters.")

with st.expander("Filtered data & download"):
    st.caption(
        "Real 'Ask a Manager' 2019 salary survey — crowd-sourced, self-reported job "
        "title, industry, experience, location, and salary. No 'skills required' "
        "field exists in this real survey, so unlike salary-by-role and demand-by-city "
        "(both real), there's no skills-trend chart here. 'Responses' means survey "
        "respondents, not live job postings. See data/fetch_jobmarket_data.py."
    )
    st.dataframe(df_filtered.reset_index(drop=True))
    csv = df_filtered.to_csv(index=False).encode("utf-8")
    st.download_button("Download filtered data as CSV", csv, "filtered_jobmarket.csv", "text/csv")
