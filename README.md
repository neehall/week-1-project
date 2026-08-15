# Sales Dashboard (Streamlit)

Small Streamlit dashboard to explore `sales_data.csv`.

Prerequisites

- Python 3.8+

Install dependencies and run locally:

```bash
python3 -m venv .venv
source .venv/bin/activate   # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

If a `.venv` already exists in this folder, just activate it (`source .venv/bin/activate`) before running `streamlit run app.py` — running it with your system/Anaconda Python instead of the venv is why `streamlit run app.py` may fail with "command not found".

Place `sales_data.csv` in the same folder as `app.py` before running.
