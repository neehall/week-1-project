import sys
from pathlib import Path

import streamlit as st

sys.path.append(str(Path(__file__).resolve().parent))
from common.styling import apply_page_style  # noqa: E402
from services import (  # noqa: E402
    revenue_service,
    cost_service,
    capex_service,
    opex_service,
    climate_service,
)

st.set_page_config(page_title="Analytics Hub", layout="wide", page_icon="📊")
apply_page_style()
st.title("Analytics Hub")
st.caption("Pick a dashboard from the sidebar, or jump in below.")

revenue_kpi = revenue_service.compute_kpis(revenue_service.load_data())
cost_kpi = cost_service.compute_kpis(cost_service.load_data())
capex_kpi = capex_service.compute_kpis(capex_service.load_data())
opex_kpi = opex_service.compute_kpis(opex_service.load_data())
climate_kpi = climate_service.compute_kpis(climate_service.load_data())

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total Revenue", f"${revenue_kpi['total_sales']:,.0f}")
k2.metric("Total Cost", f"${cost_kpi['total_cost']:,.0f}")
k3.metric("Total Capex", f"${capex_kpi['total_capex']:,.0f}")
k4.metric("Total Opex", f"${opex_kpi['total_opex']:,.0f}")
k5.metric("Avg AQI (all cities)", f"{climate_kpi['avg_aqi']:.0f}")

st.divider()

st.markdown("#### Finance")
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown("**💰 Revenue**")
    st.caption("Sales, profit, and product performance.")
    st.page_link("pages/1_Revenue.py", label="Open", icon="➡️")
with c2:
    st.markdown("**🧾 Cost**")
    st.caption("COGS, logistics, marketing, and admin cost.")
    st.page_link("pages/2_Cost.py", label="Open", icon="➡️")
with c3:
    st.markdown("**🏗️ Capex**")
    st.caption("Capital projects and asset spend.")
    st.page_link("pages/3_Capex.py", label="Open", icon="➡️")
with c4:
    st.markdown("**🧮 Opex**")
    st.caption("Recurring operating expense by department.")
    st.page_link("pages/4_Opex.py", label="Open", icon="➡️")

st.markdown("#### Climate & Environment")
c5, _, _, _ = st.columns(4)
with c5:
    st.markdown("**🌎 Climate**")
    st.caption("Real EPA AQI data — pollution spikes, seasonality, YoY change.")
    st.page_link("pages/5_Climate.py", label="Open", icon="➡️")

with st.expander("About this app"):
    st.markdown(
        """
        Each dashboard is an independent, self-contained module:

        - **`services/`** — data loading, filtering, and business logic for
          one domain. No page reads a CSV directly; it always goes through
          its service module.
        - **`pages/`** — presentation only. Each page renders its domain's
          KPIs and charts using its own service module.
        - **`common/`** — shared styling/chart-builder helpers used by every
          page, so all dashboards fit on one screen without scrolling.

        This is a modular monolith (one Streamlit process, cleanly
        separated by domain) rather than networked microservices — see
        SESSION_LOG.md for why.

        **Data provenance:** Revenue is illustrative sample data. Cost,
        Capex, and Opex are synthetic (generated, not real). Climate is
        real US EPA AirData (public domain) — see
        `data/fetch_climate_data.py`.
        """
    )
