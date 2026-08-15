"""Shared page styling + chart helpers, used by every dashboard page so
each one fits on a single screen without scrolling (see SESSION_LOG.md)."""
import streamlit as st

CHART_HEIGHT = 230


def apply_page_style():
    """Trim Streamlit's default padding/margins. Call once per page, right
    after st.set_page_config()."""
    st.markdown(
        """
        <style>
        div.block-container {padding-top: 0.9rem; padding-bottom: 1rem;}
        h1 {font-size: 1.9rem; margin-bottom: 0.1rem;}
        [data-testid="stMetricValue"] {font-size: 1.4rem;}
        </style>
        """,
        unsafe_allow_html=True,
    )


def style_chart(fig, height: int = CHART_HEIGHT):
    """Apply the compact layout every chart on these dashboards shares."""
    fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=height)
    return fig
