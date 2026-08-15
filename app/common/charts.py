"""Shared, reusable chart builders used across all four dashboards'
"Insights" tabs, so each domain's page just supplies shaped data
instead of re-implementing the same chart type four times."""
import plotly.express as px
import plotly.graph_objects as go


def stacked_area(df, x, y, color=None):
    """Trend over time, optionally decomposed by a category dimension."""
    return px.area(df, x=x, y=y, color=color)


def heatmap(df, x, y, z):
    """Magnitude across two categorical dimensions (e.g. region x month)."""
    pivot = df.pivot_table(index=y, columns=x, values=z, aggfunc="sum", fill_value=0)
    return px.imshow(pivot, aspect="auto", color_continuous_scale="Blues", labels=dict(color=z))


def treemap(df, path, values):
    """Hierarchical share of total — reads proportions better than a pie
    once there's more than ~5 categories."""
    return px.treemap(df, path=path, values=values)


def pareto(df, category_col, value_col, top_n=12):
    """Classic 80/20 view: bars for value, line for cumulative % of total."""
    d = (
        df.groupby(category_col)[value_col]
        .sum()
        .sort_values(ascending=False)
        .head(top_n)
        .reset_index()
    )
    d["cum_pct"] = d[value_col].cumsum() / d[value_col].sum() * 100

    fig = go.Figure()
    fig.add_bar(x=d[category_col], y=d[value_col], name=value_col)
    fig.add_trace(
        go.Scatter(
            x=d[category_col],
            y=d["cum_pct"],
            name="Cumulative %",
            yaxis="y2",
            mode="lines+markers",
        )
    )
    fig.update_layout(
        yaxis2=dict(overlaying="y", side="right", range=[0, 105], title="Cumulative %"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    )
    return fig
