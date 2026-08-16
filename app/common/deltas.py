"""Period-over-period comparison helper, used to drive st.metric's
built-in delta/trend-arrow display (the KPI-card-with-trend pattern
from modern BI dashboards) — one implementation, reused by every
dashboard's date-filtered KPIs instead of six copies of the same
date-arithmetic."""
import pandas as pd


def previous_period(start_date, end_date):
    """The immediately-preceding period of equal length, for comparing
    the current filtered range against."""
    span = end_date - start_date
    prev_end = start_date - pd.Timedelta(days=1)
    prev_start = prev_end - span
    return prev_start, prev_end


def pct_change(current: float, previous: float):
    """None when there's nothing to compare against (avoids a
    division-by-zero / misleading infinite % on a from-zero baseline)."""
    if previous in (0, None) or pd.isna(previous):
        return None
    return (current - previous) / previous * 100


def delta_str(pct):
    return f"{pct:+.1f}%" if pct is not None else None
