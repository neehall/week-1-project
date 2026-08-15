# Finance Dashboards (Streamlit)

Four dashboards — **Revenue**, **Cost**, **Capex**, **Opex** — built as a
modular monolith: one Streamlit app, cleanly separated by domain.

```
app/
  Home.py                 # landing page: combined KPIs + navigation
  pages/
    1_Revenue.py           # presentation only, per domain
    2_Cost.py
    3_Capex.py
    4_Opex.py
  services/
    revenue_service.py     # data loading + filtering + business logic
    cost_service.py
    capex_service.py
    opex_service.py
  common/
    styling.py             # shared page/chart styling helpers
data/
  sales_data.csv           # revenue
  cost_data.csv            # synthetic
  capex_data.csv           # synthetic
  opex_data.csv            # synthetic
  generate_synthetic_data.py
```

Pages never read a CSV directly — they always go through their
service module. Shared layout/styling lives in `common/`, so every
dashboard fits on one screen without scrolling (see `SESSION_LOG.md`
for how that was verified).

This is **not** networked microservices — no separate processes/ports
per domain — it's a modular monolith: one Streamlit process, one
`./run.sh`, with clean domain boundaries in code instead of over the
network. Simpler to run and debug locally while still being cleanly
separated.

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

## Regenerating synthetic data

`cost_data.csv`, `capex_data.csv`, and `opex_data.csv` are synthetic,
generated deterministically (fixed random seed) from `sales_data.csv`'s
date range and regions:

```bash
python3 data/generate_synthetic_data.py
```
