"""Shared, reusable chart builders used across every dashboard's
"Insights" tab (and, in v2, several Overview tabs too), so each
domain's page just supplies shaped data instead of re-implementing the
same chart type nine times.

v2: colors now come from the shared design-system palette in
theme.py (categorical hues in fixed order, one sequential hue for
magnitude, the diverging pair for polarity) instead of Plotly's
defaults, and the Pareto chart's dual-axis (two different y-scales in
one plot — the #1 chart-design anti-pattern per this workspace's
dataviz skill) has been redesigned to a single shared 0-100% axis."""
import plotly.express as px
import plotly.graph_objects as go

from . import theme


def stacked_area(df, x, y, color=None):
    """Trend over time, optionally decomposed by a category dimension."""
    return px.area(df, x=x, y=y, color=color, color_discrete_sequence=theme.CATEGORICAL)


def heatmap(df, x, y, z):
    """Magnitude across two categorical dimensions (e.g. region x month)."""
    pivot = df.pivot_table(index=y, columns=x, values=z, aggfunc="sum", fill_value=0)
    return px.imshow(pivot, aspect="auto", color_continuous_scale=theme.SEQUENTIAL_BLUE, labels=dict(color=z))


def treemap(df, path, values):
    """Hierarchical share of total — reads proportions better than a pie
    once there's more than ~5 categories."""
    return px.treemap(df, path=path, values=values, color_discrete_sequence=theme.CATEGORICAL)


def pareto(df, category_col, value_col, top_n=12):
    """Classic 80/20 view: bars for each category's share of total, line
    for cumulative share. Both series are already the same unit
    (percent of total, 0-100) so this shares one y-axis instead of the
    dual-axis (two different scales in one plot) the v1 version used —
    dual-axis is flagged as the #1 chart-design anti-pattern because a
    reader can't tell which trace belongs to which scale at a glance."""
    d = (
        df.groupby(category_col)[value_col]
        .sum()
        .sort_values(ascending=False)
        .head(top_n)
        .reset_index()
    )
    total = d[value_col].sum()
    d["pct_of_total"] = d[value_col] / total * 100
    d["cum_pct"] = d["pct_of_total"].cumsum()

    fig = go.Figure()
    fig.add_bar(x=d[category_col], y=d["pct_of_total"], name="% of total", marker_color=theme.CATEGORICAL[0])
    fig.add_trace(
        go.Scatter(
            x=d[category_col],
            y=d["cum_pct"],
            name="Cumulative %",
            mode="lines+markers",
            line=dict(color=theme.CATEGORICAL[1]),
        )
    )
    fig.update_layout(
        yaxis=dict(title="Percent of total", range=[0, 105]),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    )
    return fig


def gauge(value: float, max_value: float, title: str = "", target: float = None, suffix: str = ""):
    """Progress-to-target — a single headline number read against a
    range, the BI-dashboard pattern for "how are we doing vs. target"
    metrics (on-time rate, win rate, budget utilization, ...). No
    +delta mode: the target already shows as the threshold line on the
    gauge itself, and a second delta number beside the headline number
    overflowed this chart's compact card at 205px height."""
    steps = [
        {"range": [0, max_value * 0.5], "color": theme.SEQUENTIAL_BLUE[1]},
        {"range": [max_value * 0.5, max_value * 0.8], "color": theme.SEQUENTIAL_BLUE[4]},
        {"range": [max_value * 0.8, max_value], "color": theme.SEQUENTIAL_BLUE[7]},
    ]
    indicator_kwargs = dict(
        mode="gauge+number",
        value=value,
        number={"suffix": suffix, "font": {"color": theme.INK_PRIMARY, "size": 30}},
        gauge={
            "axis": {"range": [0, max_value], "tickcolor": theme.INK_MUTED},
            "bar": {"color": theme.CATEGORICAL[0]},
            "steps": steps,
            "threshold": {
                "line": {"color": theme.DIVERGING_DOWN, "width": 3},
                "thickness": 0.85,
                "value": target,
            } if target is not None else None,
            "bordercolor": theme.GRIDLINE,
        },
    )
    if title:
        indicator_kwargs["title"] = {"text": title, "font": {"color": theme.INK_SECONDARY, "size": 13}}
    fig = go.Figure(go.Indicator(**indicator_kwargs))
    return fig


def waterfall(categories, values, title: str = "", measure=None):
    """Compositional bridge — how a set of components adds up to a
    total (e.g. regions building up to total revenue). measure defaults
    to all "relative" bars plus a final "total" bar."""
    if measure is None:
        measure = ["relative"] * len(values) + ["total"]
        categories = list(categories) + ["Total"]
        values = list(values) + [sum(values)]
    fig = go.Figure(
        go.Waterfall(
            x=categories,
            y=values,
            measure=measure,
            increasing={"marker": {"color": theme.DIVERGING_UP}},
            decreasing={"marker": {"color": theme.DIVERGING_DOWN}},
            totals={"marker": {"color": theme.INK_MUTED}},
            connector={"line": {"color": theme.GRIDLINE}},
        )
    )
    if title:
        fig.update_layout(title=dict(text=title, font=dict(size=13, color=theme.INK_SECONDARY)))
    return fig
