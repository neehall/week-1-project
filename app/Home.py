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
    gaming_service,
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
gaming_kpi = gaming_service.compute_kpis(gaming_service.load_agent_data())

k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("Total Revenue", f"${revenue_kpi['total_sales']:,.0f}")
k2.metric("Total Cost", f"${cost_kpi['total_cost']:,.0f}")
k3.metric("Total Capex", f"${capex_kpi['total_capex']:,.0f}")
k4.metric("Total Opex", f"${opex_kpi['total_opex']:,.0f}")
k5.metric("Avg AQI (all cities)", f"{climate_kpi['avg_aqi']:.0f}")
k6.metric("Avg Agent Win Rate", f"{gaming_kpi['avg_win_rate']:.1f}%")

st.divider()

# Flat wrapping grid, not one row per category — a per-category row wastes
# most of its width whenever a category has 1-2 dashboards, and stacking
# rows vertically is exactly what breaks the one-screen-fit invariant as
# more dashboards get added. Each card carries its own category tag
# instead, so this keeps scaling as dashboards #7-9 are added.
DASHBOARDS = [
    ("💰", "Revenue", "Finance", "Sales, profit, and product performance.", "pages/1_Revenue.py"),
    ("🧾", "Cost", "Finance", "COGS, logistics, marketing, and admin cost.", "pages/2_Cost.py"),
    ("🏗️", "Capex", "Finance", "Capital projects and asset spend.", "pages/3_Capex.py"),
    ("🧮", "Opex", "Finance", "Recurring operating expense by department.", "pages/4_Opex.py"),
    ("🌎", "Climate", "Climate & Environment", "Real EPA AQI data — pollution spikes, seasonality, YoY change.", "pages/5_Climate.py"),
    ("🎮", "Gaming", "Gaming", "Real Valorant stats — K/D, win rate, map performance by rank.", "pages/6_Gaming.py"),
]

cols = st.columns(4)
for i, (icon, name, category, caption, path) in enumerate(DASHBOARDS):
    with cols[i % 4]:
        st.markdown(f"**{icon} {name}**")
        st.caption(f"{category} — {caption}")
        st.page_link(path, label="Open", icon="➡️")

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
        `data/fetch_climate_data.py`. Gaming is real Valorant competitive
        stats scraped from blitz.gg — see `data/fetch_gaming_data.py`.
        """
    )
