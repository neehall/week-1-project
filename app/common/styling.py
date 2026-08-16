"""Shared page styling + chart helpers, used by every dashboard page so
each one fits on a single screen without scrolling (see SESSION_LOG.md).

v2 additionally applies the shared design system from theme.py — a
validated color palette and consistent chart/page chrome — so all 9
dashboards read as one system instead of nine different
default-Plotly-blue dashboards. See BUILD_WRITEUP.txt / SESSION_LOG.md
for what changed and why."""
import streamlit as st

from . import theme

CHART_HEIGHT = 205  # v2: trimmed from 230 to absorb the new KPI/chart card padding+borders


def apply_page_style():
    """Trim Streamlit's default padding/margins and apply the v2 theme
    (page plane, KPI cards). Call once per page, right after
    st.set_page_config()."""
    st.markdown(
        f"""
        <style>
        div.block-container {{padding-top: 0.7rem; padding-bottom: 1rem;}}
        h1 {{font-size: 1.9rem; margin-bottom: 0.1rem; color: {theme.INK_PRIMARY};}}

        .stApp {{background-color: {theme.PAGE_PLANE};}}

        /* KPI cards: st.metric wrapped in a bordered, elevated card
        instead of bare text-on-background, matching the KPI-card
        pattern used across modern BI dashboards. Padding trimmed so
        pages with 2 rows of KPI cards (e.g. Home) still fit one
        screen without scrolling. */
        [data-testid="stMetric"] {{
            background-color: {theme.SURFACE};
            border: 1px solid {theme.GRIDLINE};
            border-radius: 8px;
            padding: 0.4rem 0.9rem 0.35rem 0.9rem;
            box-shadow: 0 1px 2px rgba(11,11,11,0.06);
        }}
        [data-testid="stMetricValue"] {{font-size: 1.4rem; color: {theme.INK_PRIMARY};}}
        [data-testid="stMetricLabel"] {{color: {theme.INK_SECONDARY};}}

        /* Chart containers get the same card treatment as KPIs, so a
        chart's title/card reads as one unit rather than floating on
        the page plane. */
        [data-testid="stPlotlyChart"] {{
            background-color: {theme.SURFACE};
            border: 1px solid {theme.GRIDLINE};
            border-radius: 8px;
            padding: 0.4rem;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def style_chart(fig, height: int = CHART_HEIGHT):
    """Apply the compact layout + v2 chart chrome every chart on these
    dashboards shares."""
    fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=height)
    return theme.apply_chart_chrome(fig)


def kpi_metric(col, label: str, value: str, icon: str = "", delta=None, delta_color: str = "normal"):
    """st.metric with an icon prefix — the KPI-card-with-icon pattern
    used throughout modern BI dashboards, without needing a custom
    component. `delta`/`delta_color` pass straight through to
    st.metric for period-over-period trend arrows."""
    label_text = f"{icon}  {label}" if icon else label
    col.metric(label_text, value, delta=delta, delta_color=delta_color)
