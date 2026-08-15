# Analytics Hub (Streamlit)

Multiple dashboards — **Revenue**, **Cost**, **Capex**, **Opex**, **Climate**
(more planned) — built as a modular monolith: one Streamlit app, cleanly
separated by domain.

```
app/
  Home.py                 # landing page: combined KPIs + navigation
  pages/
    1_Revenue.py           # presentation only, per domain
    2_Cost.py
    3_Capex.py
    4_Opex.py
    5_Climate.py
  services/
    revenue_service.py     # data loading + filtering + business logic
    cost_service.py
    capex_service.py
    opex_service.py
    climate_service.py
  common/
    styling.py             # shared page/chart styling helpers
    charts.py               # shared chart builders (heatmap, treemap, pareto, stacked area)
data/
  sales_data.csv           # revenue — illustrative sample data
  cost_data.csv            # synthetic
  capex_data.csv           # synthetic
  opex_data.csv            # synthetic
  climate_aqi.csv          # REAL — US EPA AirData (public domain), 20 US metros, 2023-2024
  generate_synthetic_data.py
  fetch_climate_data.py
```

Pages never read a CSV directly — they always go through their
service module. Shared layout/chart-building lives in `common/`, so
every dashboard fits on one screen without scrolling (see
`SESSION_LOG.md` for how that was verified), and every dashboard gets
an **Overview** tab plus a more analytical **Insights** tab (trend
decomposition, heatmaps, treemaps, Pareto/80-20 charts).

This is **not** networked microservices — no separate processes/ports
per domain — it's a modular monolith: one Streamlit process, one
`./run.sh`, with clean domain boundaries in code instead of over the
network. Simpler to run and debug locally while still being cleanly
separated.

## Data provenance

- **Revenue** — illustrative sample data (`data/sales_data.csv`, not real transactions).
- **Cost / Capex / Opex** — synthetic, deterministically generated (`data/generate_synthetic_data.py`).
- **Climate** — **real** public data: daily AQI for 20 US metro counties,
  2023–2024, from [US EPA AirData](https://aqs.epa.gov/aqsweb/airdata/download_files.html)
  (public domain). No temperature column — EPA AirData doesn't publish
  one, so the dashboard focuses on pollution spikes, seasonal patterns,
  and year-over-year AQI change instead. See `data/fetch_climate_data.py`.

## Prerequisites

- Python 3.8+

## Install & run

```bash
python3 -m venv .venv
source .venv/bin/activate   # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app/Home.py
```

If a `.venv` already exists in this folder, just activate it
(`source .venv/bin/activate`) before running — running with your
system/Anaconda Python instead of the venv is why `streamlit run ...`
may fail with "command not found". The venv must be activated in
*every new terminal window/tab*.

Or use the convenience launcher, which activates the venv for you:

```bash
./run.sh
```

## Regenerating data

Synthetic Cost/Capex/Opex data (deterministic, fixed random seed):

```bash
python3 data/generate_synthetic_data.py
```

Real Climate AQI data (requires network access to aqs.epa.gov):

```bash
python3 data/fetch_climate_data.py
```
