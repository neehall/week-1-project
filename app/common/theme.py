"""v2 design system: a validated color palette (from this workspace's
dataviz skill reference palette — reused unchanged, not invented here)
applied consistently across every dashboard, plus the chart chrome
(surfaces, ink, gridlines) that makes charts read as one system
instead of nine different default-Plotly dashboards.

Fixed-order categorical hues — never cycle these, never reassign by
rank (a filter that changes which categories are visible must not
repaint the survivors' colors)."""

CATEGORICAL = [
    "#2a78d6",  # 1 blue
    "#eb6834",  # 2 orange
    "#1baf7a",  # 3 aqua
    "#eda100",  # 4 yellow
    "#e87ba4",  # 5 magenta
    "#008300",  # 6 green
    "#4a3aa7",  # 7 violet
    "#e34948",  # 8 red
]

# Sequential (magnitude: heatmaps) — one hue, light -> dark.
SEQUENTIAL_BLUE = [
    "#cde2fb", "#b7d3f6", "#9ec5f4", "#86b6ef", "#6da7ec",
    "#5598e7", "#3987e5", "#2a78d6", "#256abf", "#1c5cab",
    "#184f95", "#104281", "#0d366b",
]

# Diverging pair (polarity: waterfall increasing/decreasing).
DIVERGING_UP = "#2a78d6"    # blue
DIVERGING_DOWN = "#e34948"  # red

# Status palette — reserved for state (KPI deltas, gauge thresholds),
# never reused as a categorical series color.
STATUS = {
    "good": "#0ca30c",
    "warning": "#fab219",
    "serious": "#ec835a",
    "critical": "#d03b3b",
}

# Chart chrome (light mode — these dashboards don't yet support a dark
# theme toggle, so this is the one surface they render on).
SURFACE = "#fcfcfb"
PAGE_PLANE = "#f9f9f7"
INK_PRIMARY = "#0b0b0b"
INK_SECONDARY = "#52514e"
INK_MUTED = "#898781"
GRIDLINE = "#e1e0d9"
BASELINE = "#c3c2b7"

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
