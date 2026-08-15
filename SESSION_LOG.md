# Session Log — Sales Dashboard (Week 1 Project)

> Note: No screenshots were captured during this session — none were taken, so none are included here. This log covers the prompt-by-prompt history and what was done at each step, for you to copy into the Google Doc.

---

## 1. Prompt: "debug"

Request was ambiguous (just the word "debug", no target specified). Asked a clarifying question; user selected **"Something in this project."**

Reviewed the project structure:
- `app.py` — Streamlit sales dashboard
- `requirements.txt` — streamlit, pandas, plotly
- `sales_data.csv` — 2,200 rows of sales data, no missing values
- `README.md` — setup instructions

Ran the app headlessly (`streamlit run app.py --server.headless true`) to confirm it started without errors, then reviewed the code closely and found two real bugs:

**Bug 1 — Date range filter crash**
`st.sidebar.date_input("Order date range", [min_date, max_date])` returns a single date (not a 2-tuple) while the user has only picked one of the two dates. The code immediately did `date_range[1]`, which throws `IndexError: tuple index out of range` in that state — a well-known Streamlit gotcha.

**Bug 2 — "Avg Discount" showed `nan%`**
When filters produced zero rows, `df_filtered["discount"].mean()` returns `NaN`. The code tried `avg_discount or 0` to guard against this, but `NaN` is *truthy* in Python (`bool(float('nan')) == True`), so the `or 0` fallback silently did nothing and the KPI displayed `nan%`.

## 2. Prompt: "yes" (apply the fixes)

Applied both fixes to `app.py`:
- Added a guard: `if len(date_range) != 2: st.info(...); st.stop()` before using `date_range[0]`/`date_range[1]`.
- Replaced the `or 0` fallback with an explicit `pd.isna()` check: `avg_discount = 0 if pd.isna(avg_discount) else avg_discount`.

Verified with `python3 -m py_compile app.py` (syntax OK).

## 3. Prompt: "yes" (verify it works)

Relaunched the app headlessly and confirmed HTTP 200 with no errors. Also directly simulated both bug scenarios in a standalone Python script to confirm the fixes:
- A single-date selection (`len(date_range) == 1`) is now caught gracefully instead of crashing.
- An empty-filter dataframe now formats Avg Discount as `0.0%` instead of `nan%`.

## 4. Prompt: "deploy this to github"

- No `gh` CLI or Homebrew was available in the environment, so downloaded a portable `gh` v2.97.0 binary (macOS arm64) into the scratchpad directory.
- Started `gh auth login` (device flow); printed a one-time code (`5826-EB76`) and the URL `https://github.com/login/device` for the user to authorize.
- After the user authorized in their browser, confirmed login as GitHub user **neehall**.
- Initialized git in the project folder, added a `.gitignore` (excluding `.venv/`, `.DS_Store`, `.claude/`, `__pycache__/`), configured local git identity, and made the initial commit.
- Asked the user for repo name/visibility; user chose **`week-1-project`, public**.
- Created and pushed the repo: **https://github.com/neehall/week-1-project**

## 5. Prompt: "streamlit run app.py is not running from the terminal, fix it" (first time)

Diagnosed that the user's terminal's default Python is Anaconda's (3.6.3), which doesn't have Streamlit installed and isn't on `PATH` — Streamlit was only installed inside the project's `.venv`. Confirmed activating the venv (`source .venv/bin/activate`) fixes it. Updated `README.md` with clearer setup instructions (creating/activating a venv, and a note explaining the "command not found" cause). Committed and pushed this README update (commit `54f21b3`).

## 6. Prompt: "streamlit run app.py is not running from the terminal, fix it" (second time)

Asked the user for the exact error; user confirmed it was `"command not found"` — confirming the venv wasn't activated in that particular terminal session (activation doesn't persist across new terminal windows/tabs).

Created a convenience launcher script, `run.sh`, that activates the venv and runs Streamlit in one step. Initial test run caught a bug in the script itself — it didn't forward CLI arguments — which surfaced Streamlit's one-time "welcome email" prompt (only shown before `~/.streamlit/credentials.toml` exists) hanging the test. Fixed `run.sh` to forward `"$@"`, and pre-created `~/.streamlit/credentials.toml` with a blank email to suppress that prompt permanently. Verified end-to-end with a headless run (HTTP 200, no prompts/errors).

## 7. Prompt: "yes" (commit and push run.sh)

Updated `README.md` to document the `./run.sh` launcher and the "activate in every new terminal" caveat. Committed and pushed (commit `3085377`).

## 8. Prompt: "what command do i need to give in the terminal to run streamlit"

Answered directly:
```bash
cd "/Users/neehal/Desktop/Neehal/Gen AI Academy/Week 1 Project"
./run.sh
```

## 9. Prompt: capture history + screenshots, update Google Doc

No Google Docs integration is available in this environment (confirmed — the doc URL returned `401 Unauthorized` when fetched, since it requires authentication I don't have), and no screenshots were taken at any point in this session. Wrote this log instead, as a file the user can open and copy into the Google Doc manually.

## 10. Prompt: "commit this to github"

Committed and pushed `SESSION_LOG.md` (commit `62a92c1`).

## 11. Prompt: "start taking screenshots of the sales dashboard(http://localhost:8501/) from now, i want to capture all the history"

No screenshot/browser-automation tooling was available, so installed Playwright + headless Chromium into the scratchpad. Launched the dashboard via `./run.sh` on port 8501 (polling the port until it actually served, not a fixed `sleep`), drove headless Chromium to it, waited for the page to render, and captured a full-page screenshot — verified visually, not just "it launched."

Saved reusable driver at `screenshots/capture.js` for future captures. Screenshot:
- `screenshots/01_initial_dashboard.png` — original vertically-stacked layout (before the one-screen redesign below).

## 12. Prompt: "i want to improve the layout of the dashboard, so that all the visualizations fit into 1 screen"

Redesigned `app.py`'s chart layout:
- Replaced the vertical stack (Sales Over Time → Sales by Region → Sales by Category → Top Products table → Filtered Data table) with a 2×2 grid (`st.columns`), each chart capped to a fixed height with tightened Plotly margins.
- Changed "Top Products" from an `st.table` (unbounded height) to a compact horizontal bar chart.
- Moved the filtered-data table and CSV download button into a collapsed `st.expander`, so it no longer pushes charts off-screen by default.
- Added CSS to shrink Streamlit's default top padding and heading margins.

**Iteration 1** — first pass used a 300px chart height. Verified with a real headless-browser screenshot at a 1440×900 viewport (common laptop resolution): the pie chart and Top Products chart were visibly clipped at the bottom edge. Caught this by comparing the page's actual content height (`document.querySelector('[data-testid="stMain"]').scrollHeight`, 1192px) against the visible viewport (900px) — a 292px overflow.
- Screenshot: `screenshots/02_one_screen_attempt1_cutoff.png`

**Iteration 2** — reduced chart height to 230px and added the CSS padding/margin trims. Re-measured: `scrollHeight` now equals `clientHeight` (900px = 900px) — zero overflow. Confirmed visually with another screenshot: all 4 charts, KPIs, and the collapsed expander are fully visible with no clipping and no scrolling required.
- Screenshot: `screenshots/03_one_screen_final.png`

Going forward, every layout/feature iteration will get: (a) an entry in this log describing what changed and why, and (b) a screenshot in `screenshots/` proving the result, named to reflect the iteration.

## 13. Prompt: "i want to create multiple dashboards now ie revenue, cost, capex, opex. go through the same process and use microservices and modular architecture"

Asked two clarifying questions before building, since "microservices" is ambiguous and the answer changes the whole architecture:

1. **What should "microservices" mean here?** User chose **modular monolith** — one Streamlit multipage app with each dashboard as its own page/module and shared common utilities, over true networked microservices (separate FastAPI services per domain + HTTP calls) — simpler to run/debug locally while still cleanly separated by domain.
2. **Where should Cost/Capex/Opex data come from**, since only `sales_data.csv` (revenue-shaped) existed? User chose **generate synthetic data**, aligned to the same date range/regions as `sales_data.csv`.

**Restructured the project into a modular monolith:**
- `data/` — all CSVs moved here (`sales_data.csv` relocated from repo root), plus `generate_synthetic_data.py` (deterministic, fixed seed) which produces `cost_data.csv`, `capex_data.csv`, `opex_data.csv`.
- `app/services/` — one module per domain (`revenue_service.py`, `cost_service.py`, `capex_service.py`, `opex_service.py`), each owning that domain's data loading (`@st.cache_data`), filtering, and KPI/aggregation logic. Pages never read a CSV directly.
- `app/common/styling.py` — extracted the one-screen CSS/chart-height helpers from the original `app.py` so every page shares them instead of duplicating.
- `app/pages/1_Revenue.py` … `4_Opex.py` — Streamlit's native multipage convention; each is presentation-only, calling its service module and rendering the same proven 2×2 one-screen chart-grid layout.
- `app/Home.py` — new landing page: combined KPIs across all four domains, navigation cards (`st.page_link`) to each dashboard, and an "About this app" note on the architecture.
- Deleted the old root `app.py` (superseded by `app/Home.py` + pages). Updated `run.sh` to launch `app/Home.py`, and `requirements.txt` to add `numpy` (used by the data generator).

**Verified, not just launched:**
- Syntax-checked all 12 new/changed Python files (`py_compile`).
- Launched via `./run.sh`, confirmed clean startup (no errors in server log).
- Used the same one-screen-fit check as the earlier iteration (`stMain` `scrollHeight` vs `clientHeight`) plus real headless-browser screenshots at 1440×900 for all 5 pages: Home, Revenue, Cost, Capex, Opex. All five: zero overflow, and visually confirmed nothing is clipped except a minor legend-label crop on the Opex "Expense Type by Department" chart (cosmetic, doesn't cause page-level scrolling).
- Checked browser console on each dashboard page: the only errors were `_stcore/health` / `_stcore/host-config` 404s, which are Streamlit's own internal requests mis-resolving against the sub-page path on direct navigation — a known framework quirk unrelated to this app's code, confirmed benign.
- Screenshots: `screenshots/04_home.png`, `05_revenue.png`, `06_cost.png`, `07_capex.png`, `08_opex.png`.

Updated `README.md` to document the new structure, why it's a modular monolith rather than networked microservices, and how to regenerate the synthetic data.

## 14. Prompt: "add more interesting visualizations to each of the dashboards"

Rather than pile more bar charts onto the existing Overview grid (which would break the one-screen fit), added a second **Insights** tab (`st.tabs`) to each dashboard with genuinely different chart types chosen for what's analytically useful in that domain, not mechanically identical across all four:

- **`app/common/charts.py`** — new shared chart-builder module (`stacked_area`, `heatmap`, `treemap`, `pareto`) so the four new chart types are implemented once and reused, instead of each page reinventing them. Keeps the modular architecture consistent — a "presentation components" layer alongside the existing "data/business logic" (`services/`) and "styling" (`common/styling.py`) layers.
- **Revenue Insights:** Profit Margin by Category (bar — margin isn't the same story as sales volume), Sales Trend by Category (stacked area), Sales Heatmap Region×Month, Top Products Pareto (80/20).
- **Cost Insights:** Cost Trend by Category (stacked area), Cost Heatmap Region×Month, Cost Share Region>Category (treemap), Cost by Category Pareto.
- **Capex Insights:** Cumulative Capex Over Time (running total — the question capital planning actually asks, vs. the per-month spike view on Overview), Capex Heatmap Region×Asset Category (chosen over Region×Month since Capex is ~90 discrete projects, not a steady monthly flow — a month axis would mostly be empty cells), Capex Share Region>Asset (treemap), Top Projects Pareto.
- **Opex Insights:** Opex Trend by Expense Type (stacked area), Opex Heatmap Department×Expense Type, Opex Share Department>Expense Type (treemap), Opex by Expense Type Pareto.
- Added the corresponding data-shaping functions to each `services/*.py` module (e.g. `profit_margin_by_category`, `cost_trend_by_category`, `cumulative_capex_over_time`) — services still own all data logic, pages still only render.
- Also fixed the pre-existing minor legend clipping on the Opex Overview "Expense Type by Department" chart (moved legend to horizontal/top) while in that file.

**Verified, not just launched:**
- Syntax-checked all changed/new files.
- Launched via `./run.sh`; for each of the 4 dashboard pages, used headless Chromium to click into the Insights tab (not just load the default Overview tab) and re-measured `stMain` `scrollHeight` vs `clientHeight` — all four: zero overflow, same one-screen guarantee as Overview.
- Checked console errors on each Insights tab load — none (beyond the already-documented benign `_stcore` 404s on direct navigation).
- Re-screenshotted all 5 Overview pages too, to confirm the tab-wrapping refactor didn't break anything and to capture the Opex legend fix.
- Screenshots: `screenshots/09_revenue_insights.png`, `10_cost_insights.png`, `11_capex_insights.png`, `12_opex_insights.png` (Insights tabs); `04_home.png`–`08_opex.png` updated in place (Overview tabs, post-refactor).

## 15. Prompt: request to build 5 more dashboards (Climate, E-sports, Real Estate, Supply Chain, Job Market) — first of five, Climate

Before building, asked 3 clarifying questions since the answers reshape all 5 builds:
1. **App structure** — user chose to add these as more pages in the existing app (not a separate suite). Renamed `Home.py`'s title from "Finance Dashboards" to **"Analytics Hub"**, and restructured the landing page into labeled sections ("Finance", "Climate & Environment", ...) so it scales past 4 dashboards.
2. **Data source** — user chose **real public data where reasonably available**, synthetic as fallback (same standard as Cost/Capex/Opex).
3. **Build order** — user chose **one dashboard at a time with a checkpoint**, starting with Climate.

**Sourcing real data:** searched for a public city-level AQI/weather CSV. Evaluated and rejected: aqicn.org's COVID19 platform (100+MB/year files, requires ToS-gated access token, not a plain public URL) and EPA's annual county summary files (too coarse — annual, not daily). Settled on **US EPA AirData's daily-AQI-by-county files** (`https://aqs.epa.gov/aqsweb/airdata/daily_aqi_by_county_{year}.zip`) — confirmed genuinely public (plain `curl`, no auth), ~1.6MB/year zipped, daily granularity. Downloaded 2023 + 2024 (26MB CSV each, full US), filtered to a curated list of 20 well-known metro counties (Los Angeles, Chicago, Houston, Phoenix, etc.) to keep the repo file small (774KB) — real government data, not sampled/fabricated. **No temperature column exists in this dataset** (EPA AirData is AQI-only) — flagged this explicitly rather than quietly filling it with synthetic numbers next to real ones, which would misrepresent the real data as more complete than it is. Saved the fetch+filter logic as `data/fetch_climate_data.py` (reproducible, same convention as `generate_synthetic_data.py`) and added `requests` to `requirements.txt`.

**Built `climate_service.py` + `pages/5_Climate.py`:**
- KPIs: Avg AQI, Worst City, % Unhealthy-or-worse days, YoY change (2023→2024).
- Overview tab: AQI over time, Avg AQI by city, AQI category distribution, Top pollution spike days (real dated events, e.g. actual worst-AQI day per city).
- Insights tab: Seasonal pattern (avg AQI by calendar month — surfaces the real summer ozone-season peak visible in the actual EPA data), Year-over-year AQI by city (grouped bar), City×Month heatmap, Category-share-by-defining-pollutant treemap.
- Reused `common/charts.py` (heatmap/treemap) rather than adding new one-off chart code.

**Verified, not just launched:**
- Syntax-checked all new/changed files.
- Launched via `./run.sh`; screenshotted Home, Climate Overview, and Climate Insights under headless Chromium.
- **Caught a real one-screen-fit regression**: Climate initially overflowed by 25–28px (`stMain` scrollHeight 925–928 vs clientHeight 900), traced to an `st.caption()` line under the title that the other dashboards don't have. First attempted a CSS negative-margin fix — re-measured and it didn't actually close the gap (margin collapse doesn't work that way inside Streamlit's flex layout), so reverted that and instead moved the provenance caption into the already-collapsed "Filtered data & download" expander, where it costs no vertical space. Re-verified all 6 pages (5 existing + Climate) at 1440×900 after the change — all exactly `scrollHeight === clientHeight`, zero overflow, zero console errors.
- Screenshots: `screenshots/13_home_updated.png`, `14_climate_overview.png`, `15_climate_insights.png`.

Updated `README.md` with the new structure, the data-provenance table (which dashboards are real vs. synthetic vs. illustrative), and the `fetch_climate_data.py` usage note.

User then said to build the remaining 4 dashboards (Gaming, Real Estate, Logistics, Job Market) sequentially without stopping for approval between each — proceeded accordingly.

## 16. Gaming dashboard (second of five, real Valorant stats)

**Sourcing real data:** searched for public match-history/player-stat CSVs. Oracle's Elixir (pro LoL match data) returned `403 Forbidden` on fetch — likely bot-blocked/Google-Drive-hosted, not a plain curlable URL. Found `github.com/IronicNinja/valorant-stats`: real, live-scraped (from blitz.gg) Valorant competitive stats, plain `raw.githubusercontent.com` CSVs, no auth. It's an **aggregate snapshot per agent/map/rank-tier**, not individual match-by-match history — no calendar-time dimension. Rather than fabricate dates next to real numbers, used **rank tier (Iron → Diamond, Riot's public competitive-tier enum)** as the trend axis instead — same honesty approach as Climate's missing-temperature call. Wrote `data/fetch_gaming_data.py` to pull and reshape `agents_data/{map}/agents_competitive_tier={tier}.csv` (K/D, win rate, pick rate, ACS, first blood %) and `map_data/maps_competitive_tier={tier}.csv` (play rate, attack/defense win %) across 7 maps × 18 tiers into `data/gaming_agent_stats.csv` (1,513 rows) and `data/gaming_map_stats.csv` (108 rows).

**Built `gaming_service.py` + `pages/6_Gaming.py`:** KPIs (Avg K/D, Avg Win Rate, Top Agent, Matches Analyzed); Overview tab (K/D by agent, win rate by agent, map attack-vs-defense win%, most-picked agents); Insights tab (win rate by rank tier for top 6 agents, K/D-vs-win-rate scatter, agent×map win-rate heatmap, map>agent pick-rate treemap).

**Restructured `Home.py`'s dashboard grid**, since the per-category-row layout (one full-width row per category) was about to break: adding a 1-dashboard "Gaming" row pushed Home 37px past the one-screen fold. Replaced it with a flat wrapping 4-column grid where every card carries its own category tag inline — scales to many more dashboards without adding rows for single-item categories.

**Verified, and caught two real bugs via screenshots (not just launch):**
1. **Blank heatmap and treemap on the Insights tab.** The Map filter defaulted to `["All Maps"]` (the pre-aggregated rollup row), but `heatmap_agent_map()`/`map_pickrate_treemap()` explicitly exclude `"All Maps"` rows (they need per-map breakdowns) — so with the default filter, both got an empty dataframe and rendered blank. Fixed by defaulting the Map filter to the individual maps instead, keeping "All Maps" available as an opt-in aggregate.
2. **Legend overflow** on the "Win Rate by Rank" line chart (6 agent names in a vertical legend overflowed the chart's right edge) — fixed with the same horizontal/top legend pattern already used on Opex.
- Re-verified all 7 pages × Overview/Insights at 1440×900 after both fixes — all `scrollHeight === clientHeight`, zero console errors — and re-screenshotted to confirm the previously-blank charts now show real data.
- Screenshots: `screenshots/13_home_updated.png` (Home, updated grid), `16_gaming_overview.png`, `17_gaming_insights.png`.

Updated `README.md` (structure, data provenance, `fetch_gaming_data.py` usage).

## 17. Real Estate dashboard (third of five, real Zillow ZHVI data)

**Sourcing real data:** Zillow Research publishes plain, public CSVs (no auth, no rate limit) at `files.zillowstatic.com/research/public_csvs/zhvi/`, including versions segmented by bedroom count (`City_zhvi_bdrmcnt_{1..5}_...csv`, ~10–72MB each) — a direct match for the user's "filters for bedrooms" ask. Wrote `data/fetch_realestate_data.py` to download all 5 bedroom-count files, filter to the same style of curated 20-city list as Climate/Gaming, melt the wide monthly columns (2000–2026) to long format, keep 2020-01 onward, and write `data/realestate_zhvi.csv` (7,795 rows, 602KB). Sanity-checked the real numbers: San Francisco priciest, Detroit most affordable, a visible COVID-era price surge in 2021–2022 — all match known reality.

**Honesty note, same pattern as Climate/Gaming:** ZHVI is Zillow's smoothed, seasonally-adjusted *estimate* for the 33rd–67th percentile home tier in each city — not an individual listing price or address. So there's no true per-property "price range" filter or map point available in real data. Handled this explicitly rather than papering over it:
- Added a price-range slider that filters on the real aggregate ZHVI value (a legitimate filter, just not a per-listing one).
- Built the requested map using `px.scatter_geo` (built-in USA basemap, no external tile server / no token needed) with **real, publicly-known city-centroid coordinates** (not from Zillow, and clearly not per-property) sized/colored by each city's average home value.
- Documented the distinction in the page's data-provenance caption and in `README.md`.

**Built `realestate_service.py` + `pages/7_RealEstate.py`:** KPIs (Avg Home Value, YoY Change, Priciest/Most Affordable City); Overview tab (price trend, avg by city, avg by bedroom count, city map); Insights tab (YoY change by city, price trend by bedroom count as a stacked area, city×bedroom heatmap, price distribution histogram — a new chart type not used on any other dashboard yet).

**Verified, not just launched:** syntax-checked all files; launched via `./run.sh`; checked all 8 pages (7 dashboards + Home) × Overview/Insights at 1440×900 under headless Chromium — all `scrollHeight === clientHeight`, zero real console errors (only the already-documented benign `_stcore` 404s, this time on the `/RealEstate` sub-path too — confirmed via the same response-inspection approach used for Cost/Gaming). Visually confirmed the map renders actual bubbles (not a blank/broken tile) and the stacked-area/heatmap/histogram all show distinct real data. Added the Real Estate card + 7th KPI to Home — confirmed it still fits at 1440×900 with room to spare for 2 more dashboards before the 4-column grid needs a new row.
- Screenshots: `screenshots/13_home_updated.png` (Home, 7 dashboards), `18_realestate_overview.png`, `19_realestate_insights.png`.

Updated `README.md` (structure, provenance, `fetch_realestate_data.py` usage, ~200MB one-time download note).

Next: Supply Chain/Logistics, Job Market — proceeding without further checkpoints per user's instruction.

---

## Current state of the project

- **Repo:** https://github.com/neehall/week-1-project (public)
- **Latest commit:** see `git log` — most recent work adds the Real Estate dashboard (real Zillow ZHVI data)
- **Bugs fixed:** date-range partial-selection crash; `nan%` avg discount on empty filter results; Gaming Insights blank heatmap/treemap from a bad default filter; Gaming/Opex legend overflow
- **Architecture:** modular monolith — `app/Home.py` ("Analytics Hub", flat wrapping dashboard grid) + `app/pages/` (presentation) + `app/services/` (data/business logic per domain) + `app/common/styling.py` (shared layout) + `app/common/charts.py` (shared chart builders)
- **Dashboards:** Revenue (illustrative sample data), Cost/Capex/Opex (synthetic, `data/generate_synthetic_data.py`), Climate (**real** EPA AQI data), Gaming (**real** Valorant stats), Real Estate (**real** Zillow ZHVI data, `data/fetch_realestate_data.py`) — each with an Overview tab and an Insights tab
- **Layout:** every tab on every dashboard fits on one screen (1440×900) with no scrolling
- **To run locally:** `./run.sh` from the project folder (launches `app/Home.py`)
- **Screenshots:** `screenshots/` — numbered in iteration order, each mapped to a log entry above
