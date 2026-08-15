import sys
from pathlib import Path

import plotly.express as px
import streamlit as st

sys.path.append(str(Path(__file__).resolve().parents[1]))
from common.styling import apply_page_style, style_chart  # noqa: E402
from common import charts  # noqa: E402
from services import gaming_service as svc  # noqa: E402

st.set_page_config(page_title="Gaming Dashboard", layout="wide")
apply_page_style()
st.title("Gaming Dashboard")

agent_df = svc.load_agent_data()
map_df = svc.load_map_data()

st.sidebar.header("Filters")
# Default to the individual maps (not the "All Maps" aggregate row) so the
# Insights tab's per-map heatmap/treemap have data to show out of the box.
map_options = sorted(agent_df["map"].unique())
default_maps = [m for m in map_options if m != "All Maps"]
maps = st.sidebar.multiselect("Map", map_options, default=default_maps)
ranks = st.sidebar.multiselect("Rank", svc.RANK_ORDER, default=svc.RANK_ORDER)
agents = st.sidebar.multiselect("Agent", sorted(agent_df["agent"].unique()), default=sorted(agent_df["agent"].unique()))

agent_filtered = svc.filter_agent_data(agent_df, maps or agent_df["map"].unique(), ranks, agents)
map_filtered = svc.filter_map_data(map_df, ranks)

kpi = svc.compute_kpis(agent_filtered)
k1, k2, k3, k4 = st.columns(4)
k1.metric("Avg K/D", f"{kpi['avg_kd']:.2f}")
k2.metric("Avg Win Rate", f"{kpi['avg_win_rate']:.1f}%")
k3.metric("Top Agent (win rate)", kpi["top_agent"])
k4.metric("Matches Analyzed", f"{kpi['total_matches']:,}")

if not agent_filtered.empty:
    tab_overview, tab_insights = st.tabs(["Overview", "Insights"])

    with tab_overview:
        row1_left, row1_right = st.columns(2)
        with row1_left:
            st.markdown("**K/D by Agent**")
            fig = px.bar(svc.kd_by_agent(agent_filtered), x="agent", y="kd")
            st.plotly_chart(style_chart(fig), use_container_width=True)
        with row1_right:
            st.markdown("**Win Rate by Agent**")
            fig = px.bar(svc.win_rate_by_agent(agent_filtered), x="agent", y="win_rate")
            st.plotly_chart(style_chart(fig), use_container_width=True)

        row2_left, row2_right = st.columns(2)
        with row2_left:
            st.markdown("**Map Performance: Attack vs Defense Win %**")
            mw = svc.map_win_rates(map_filtered).melt(id_vars="map", var_name="side", value_name="win_pct")
            fig = px.bar(mw, x="map", y="win_pct", color="side", barmode="group")
            st.plotly_chart(style_chart(fig), use_container_width=True)
        with row2_right:
            st.markdown("**Most Picked Agents**")
            top = svc.pick_rate_by_agent(agent_filtered)
            fig = px.bar(top.sort_values("pick_rate"), x="pick_rate", y="agent", orientation="h")
            st.plotly_chart(style_chart(fig), use_container_width=True)

    with tab_insights:
        row1_left, row1_right = st.columns(2)
        with row1_left:
            st.markdown("**Win Rate by Rank (top 6 most-played agents)**")
            fig = px.line(
                svc.win_rate_by_rank(agent_filtered),
                x="rank", y="win_rate", color="agent",
                category_orders={"rank": svc.RANK_ORDER},
            )
            fig.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0))
            st.plotly_chart(style_chart(fig), use_container_width=True)
        with row1_right:
            st.markdown("**K/D vs Win Rate by Agent**")
            kv = svc.kd_vs_winrate(agent_filtered)
            fig = px.scatter(kv, x="kd", y="win_rate", size="matches", color="agent", text="agent")
            fig.update_traces(textposition="top center")
            st.plotly_chart(style_chart(fig), use_container_width=True)

        row2_left, row2_right = st.columns(2)
        with row2_left:
            st.markdown("**Win Rate Heatmap: Agent x Map**")
            fig = charts.heatmap(svc.heatmap_agent_map(agent_filtered), x="map", y="agent", z="win_rate")
            st.plotly_chart(style_chart(fig), use_container_width=True)
        with row2_right:
            st.markdown("**Pick Rate Share: Map > Agent**")
            fig = charts.treemap(svc.map_pickrate_treemap(agent_filtered), path=["map", "agent"], values="pick_rate")
            st.plotly_chart(style_chart(fig), use_container_width=True)
else:
    st.info("No data for selected filters.")

with st.expander("Filtered data & download"):
    st.caption(
        "Real Valorant competitive stats scraped from blitz.gg, published by "
        "github.com/IronicNinja/valorant-stats. Aggregate snapshot, not individual "
        "match history — no calendar-time dimension, so rank tier stands in as the "
        "trend axis. See data/fetch_gaming_data.py."
    )
    st.dataframe(agent_filtered.reset_index(drop=True))
    csv = agent_filtered.to_csv(index=False).encode("utf-8")
    st.download_button("Download filtered data as CSV", csv, "filtered_gaming.csv", "text/csv")
