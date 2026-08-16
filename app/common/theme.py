"""v2 design system: a validated color palette (from this workspace's
dataviz skill reference palette — reused unchanged, not invented here)
applied consistently across every dashboard, plus the chart chrome
(surfaces, ink, gridlines) that makes charts read as one system
instead of nine different default-Plotly dashboards.

Dark mode: these are the palette's own dark-surface steps (the same
eight categorical hues, stepped for a dark background, not a separate
palette), matching .streamlit/config.toml's `base = "dark"`. Every
color below is the dark variant — there's no light/dark switch here
because the app is fixed to dark theme (see SESSION_LOG.md).

Fixed-order categorical hues — never cycle these, never reassign by
rank (a filter that changes which categories are visible must not
repaint the survivors' colors)."""

CATEGORICAL = [
    "#3987e5",  # 1 blue
    "#d95926",  # 2 orange
    "#199e70",  # 3 aqua
    "#c98500",  # 4 yellow
    "#d55181",  # 5 magenta
    "#008300",  # 6 green
    "#9085e9",  # 7 violet
    "#e66767",  # 8 red
]

# Sequential (magnitude: heatmaps) — one hue, dim -> bright, calibrated
# so the low end still reads against the dark surface instead of
# vanishing into it.
SEQUENTIAL_BLUE = [
    "#0d366b", "#104281", "#184f95", "#1c5cab", "#256abf",
    "#2a78d6", "#3987e5", "#5598e7", "#6da7ec", "#86b6ef",
    "#9ec5f4", "#b7d3f6", "#cde2fb",
]

# Diverging pair (polarity: waterfall increasing/decreasing).
DIVERGING_UP = "#3987e5"    # blue
DIVERGING_DOWN = "#e66767"  # red

# Status palette — reserved for state (KPI deltas, gauge thresholds),
# never reused as a categorical series color. Same four steps as light
# mode: the palette's dark-surface contrast was already validated for
# both.
STATUS = {
    "good": "#0ca30c",
    "warning": "#fab219",
    "serious": "#ec835a",
    "critical": "#d03b3b",
}

# Chart chrome (dark mode).
SURFACE = "#1a1a19"
PAGE_PLANE = "#0d0d0d"
INK_PRIMARY = "#ffffff"
INK_SECONDARY = "#c3c2b7"
INK_MUTED = "#898781"
GRIDLINE = "#2c2c2a"
BASELINE = "#383835"
CARD_SHADOW = "rgba(255,255,255,0.06)"

FONT_FAMILY = "system-ui, -apple-system, 'Segoe UI', sans-serif"


def apply_chart_chrome(fig):
    """Shared chart chrome: surface, ink, gridlines, font — applied on
    top of style_chart()'s sizing so every chart on every dashboard
    reads as one visual system."""
    fig.update_layout(
        paper_bgcolor=SURFACE,
        plot_bgcolor=SURFACE,
        font=dict(family=FONT_FAMILY, color=INK_SECONDARY, size=12),
        # No title_font here: chart titles are the st.markdown() header
        # above each chart, not Plotly's own title — setting title_font
        # without title.text renders a literal "undefined" in this
        # Plotly.js version.
        colorway=CATEGORICAL,
    )
    fig.update_xaxes(gridcolor=GRIDLINE, linecolor=BASELINE, tickfont=dict(color=INK_MUTED))
    fig.update_yaxes(gridcolor=GRIDLINE, linecolor=BASELINE, tickfont=dict(color=INK_MUTED))
    return fig
