# What I Built — Analytics Hub

A reflective write-up of this project: what it is, what data powers it,
the actual prompts used to build it end-to-end with Claude, the
iterations/trial-and-error along the way, and what stood out about the
workflow. For the blow-by-blow technical log (every command run, every
verification step), see [`SESSION_LOG.md`](SESSION_LOG.md).

## Project overview

**Analytics Hub** is a 9-dashboard Streamlit app — Revenue, Cost, Capex,
Opex, Climate, Gaming, Real Estate, Logistics, and Job Market — built
incrementally across a single long session, starting from a one-file,
one-chart sales dashboard and ending as a modular multi-domain app with
real public data behind 5 of its 9 dashboards.

**Architecture.** It's a *modular monolith*: one Streamlit process
(`streamlit run app/Home.py`), not networked microservices, with clean
separation enforced in code instead of over the network:

- `app/pages/` — presentation only, one file per dashboard
- `app/services/` — data loading, filtering, and business logic, one
  module per domain; pages never read a CSV directly
- `app/common/` — shared styling (`styling.py`) and shared chart
  builders (`charts.py`: heatmap, treemap, Pareto, stacked area) reused
  across every dashboard instead of duplicated per page
- `data/` — one CSV per dataset, plus a `generate_*`/`fetch_*` script
  per dataset documenting exactly where it came from

**Design constraints that shaped the build:**
- Every dashboard has an **Overview** tab and an **Insights** tab, both
  required to fit on a 1440×900 screen with zero scrolling — verified
  mechanically (`scrollHeight === clientHeight`) after every change, not
  eyeballed.
- Every real dataset's dashboard is explicit in its own UI about what
  the source data does *not* contain (no fabricated columns to fill
  gaps — see Learnings below).

**Repo:** https://github.com/neehall/week-1-project (public)

## Datasets used

| Dashboard | Dataset | Real or synthetic | Source |
|---|---|---|---|
| Revenue | Sample sales transactions | Illustrative sample data | Pre-existing in the starter project |
| Cost / Capex / Opex | Generated cost/capex/opex records | Synthetic, deterministic (fixed seed) | `data/generate_synthetic_data.py` |
| Climate | Daily AQI, 20 US metro counties, 2023–2024 | **Real** | [US EPA AirData](https://aqs.epa.gov/aqsweb/airdata/download_files.html) (public domain) |
| Gaming | Valorant agent/map competitive stats | **Real** | [valorant-stats](https://github.com/IronicNinja/valorant-stats) (scraped from blitz.gg) |
| Real Estate | Home Value Index, 20 US cities, 2020–2026 | **Real** | [Zillow Research ZHVI](https://www.zillow.com/research/data/) |
| Logistics | Health-commodity shipment records, 2006–2015 | **Real** | [USAID SCMS Delivery History](https://github.com/jrcinco/supply-chain-shipment-price-data) |
| Job Market | Salary survey responses | **Real** | [Ask a Manager 2019 survey](https://github.com/kmamykin/askamanager_salary_survey) |

Each real dataset required actually evaluating multiple candidate
sources, not taking the first search result — see Iterations below.

## Prompts used (vibe coding log)

The actual prompts driving this build, in order. Follow-up "yes"
prompts approved the immediately preceding proposal/plan.

1. `debug`
2. `yes` *(apply the two bugs found)*
3. `yes` *(verify the fixes)*
4. `deploy this to github`
5. `streamlit run app.py is not running from the terminal, fix it`
6. `yes` *(commit the README fix)*
7. `streamlit run app.py is not running from the terminal, fix it` *(recurred — root cause wasn't fully fixed the first time)*
8. `yes` *(commit run.sh)*
9. `what command do i need to give in the terminal to run streamlit`
10. `capture the entire history of the prompts, the screenshots from the beginning to capture all the progress and update the doc at [Google Doc URL]`
11. `also start taking screen shots of the sales dashboard(http://localhost:8501/) from now, i want to capture all the history`
12. `commit this to github`
13. `i want to improve the layout of the dashboard, so that all the visualizations fit into 1 screen`
14. `yes keep capturing all prompts and screenshots based on iterations`
15. `i want to create multiple dashboards now ie revenue, cost, capex, opex. go through the same process and use microservices and modular architecture`
16. *(answered 2 clarifying questions: modular monolith vs. true microservices → modular monolith; synthetic vs. real data for the 3 new domains → synthetic)*
17. `commit this to github`
18. `add more interesting visualizations to each of the dashboards`
19. `yes`
20. `i want to now build Climate/environment dashboard — pull a public CSV of city-level weather or air quality data (AQI, temperature trends) and visualize pollution spikes, seasonal patterns, or year-over-year change. E-sports/gaming analytics tracker... Real estate market explorer... Supply chain/logistics dashboard... Job market/hiring trends analyzer...` *(all 5 remaining dashboard ideas given at once)*
21. *(answered 3 clarifying questions: same app vs. separate suite → same app; real vs. synthetic data → real where available; build all 5 at once vs. one at a time → one at a time)*
22. `yes` *(build Climate)*
23. `yes` *(commit Climate)*
24. `yes` *(build Gaming)*
25. `build all the remaining dashboards sequentially, no need for my approval` *(sent mid-turn — switched the workflow from checkpoint-per-dashboard to autonomous)*
26. `yes` *(commit Real Estate)* — from this point, Real Estate, Logistics, and Job Market were each built, verified, and committed back-to-back without further prompts, per instruction #25
27. `how do i make all of this public via github`
28. `yes polish the readme`
29. `add a file detailing what you built. Include: project overview, datasets used, prompts you used during vibe coding, iterations you tried, and any learnings or observations from the workflow.` *(this file)*

## Iterations I tried

**Layout: three passes before "fits on one screen" actually held.**
First pass used a 2×2 chart grid at 300px chart height — looked right in
isolation, but a real headless-browser screenshot at 1440×900 showed the
pie chart and bottom row clipped (`scrollHeight` 1192 vs. 900px
available). Second pass dropped chart height to 230px and trimmed
Streamlit's default CSS padding — fixed it, confirmed by the same
screenshot check now reading exactly `900 === 900`. This became the
standing pattern for every dashboard after.

**Home page navigation: category rows → flat grid.** Once multiple
domains existed, I first grouped dashboard cards under section headers
("Finance", "Climate & Environment", ...) — one full-width row per
category. That broke the moment a category had only one dashboard
(Gaming): the near-empty row still cost a full row of height, pushing
Home 37px past the fold. Replaced it with a flat wrapping 4-column grid
where each card carries its own category as an inline tag instead —
scaled cleanly through 4 more dashboards afterward with no further
layout surgery needed.

**Home KPI row: grew from 4 columns to two rows of 5.** Kept adding one
KPI metric per new dashboard in a single `st.columns(n)` row. That
worked up to `n=8`; at `n=9` a single row is where I judged dollar-figure
metrics would get visually cramped, so I switched to two rows of 5
instead of letting the row silently degrade — a judgment call, not
something the one-screen-fit check would have caught on its own since
it only measures overflow, not readability.

**Data sourcing: real dead ends before real data.** Several first
choices for "real" data didn't pan out and needed a second pass:
- Oracle's Elixir (pro League of Legends match data) returned `403
  Forbidden` on fetch — bot-blocked or gated, not a plain public URL.
  Switched to Valorant stats from a different GitHub-hosted mirror.
- aqicn.org's COVID-19 air-quality platform required ToS acceptance and
  a token, and its files were 100+MB/year — switched to US EPA AirData's
  plain, curlable, ~1.6MB/year daily-AQI files instead.
- Zillow's plain city-level ZHVI file existed, but I found the
  *bedroom-count-segmented* version only after specifically searching
  for it — it was the direct match for the "filter by bedrooms" ask
  rather than a fallback.

**Gaming dashboard: two real bugs found only by screenshotting the
actual rendered Insights tab**, not just confirming the page loaded:
1. The Insights tab's heatmap and treemap rendered completely blank.
   Root cause: the Map filter defaulted to the `"All Maps"` aggregate
   row, but those two charts explicitly excluded `"All Maps"` (they
   need per-map breakdowns) — so the default filter state produced an
   empty dataframe for exactly the two charts that needed map-level
   data. Fixed by defaulting to the individual maps instead.
2. A 6-agent line-chart legend overflowed the chart's right edge.
   Fixed with a horizontal top-aligned legend (a pattern then reused on
   Opex and elsewhere).

Neither bug was visible from the terminal log or a "page loaded
successfully" check — only from actually looking at the rendered chart.

**Climate dashboard: a CSS fix that looked right but wasn't.** Added a
`st.caption()` line under the title, which pushed the page 25–28px past
the one-screen fold. First attempt: a CSS negative-margin rule to pull
the caption up. Re-measuring after the change showed the overflow
hadn't actually closed — margin collapse doesn't work that way inside
Streamlit's flex layout. Reverted it and instead moved the caption into
the already-collapsed "Filtered data & download" expander, where it
costs no vertical space at all. The lesson mattered enough to repeat
below.

## Learnings & observations

**"It launched" and "it works" are different claims, and only headless
verification catches the gap.** Nearly every real bug in this session
(two layout overflows, two Gaming chart bugs) was invisible from a
server log or an HTTP 200 — they only showed up in an actual screenshot
of the rendered page, and in one case only after clicking into a
specific tab. The habit that paid off repeatedly: launch it, drive it
with headless Chromium, screenshot it, and look at the screenshot,
every time — not just after the first build of a page, but after
*every* change to it, including ones that seemed purely additive (like
adding one caption line).

**A fix isn't verified until it's re-measured, not just re-read.** The
Climate CSS negative-margin attempt read as correct — negative margins
do pull elements up in normal CSS. It didn't work inside this specific
layout, and the only way to know was to re-run the same `scrollHeight`
measurement after making the change, not to trust that the edit looked
plausible.

**Being explicit about what real data *doesn't* contain built more
trust than it cost in completeness.** Every one of the 5 real-data
dashboards is missing something the original ask implied it might have
(Climate: no temperature; Gaming: no match-by-match time series; Real
Estate: no per-listing price/address; Logistics: no warehouse/inventory
levels; Job Market: no skills field). The alternative — quietly filling
each gap with a plausible-looking synthetic column sitting next to real
ones — would have been actively misleading, since a reader can't tell
real from fabricated once they're mixed in the same table. Flagging
each gap in-app and in the README, and building the dashboard around
what the real data *does* support instead, was slower but kept every
number in the app honestly attributable to its source.

**A small shared-abstraction layer paid for itself fast.** `common/
charts.py` (heatmap, treemap, Pareto, stacked area) was written once
for the Revenue/Cost/Capex/Opex Insights-tab pass and then reused
as-is by Climate, Gaming, Real Estate, Logistics, and Job Market — five
more dashboards without touching that file again. The `services/` +
`pages/` split similarly meant each new dashboard was "write one data
module, write one presentation module," not "figure out the whole
pattern again."

**A hard constraint (one screen, no scroll) was a better design forcing
function than an aesthetic guideline would have been**, because it was
checkable by a script instead of by eye. "Make it look clean" invites
disagreement; "`scrollHeight === clientHeight` at 1440×900" is a yes/no
question a screenshot can answer, and it caught real regressions
(Climate's caption, Gaming's default filter) that a purely visual pass
might have waved through as "close enough."

**Instruction to "build sequentially without approval" changed the
right unit of checkpointing, not the need for it.** Once told to
proceed autonomously, each dashboard still went through the same
sequence — build, verify with real screenshots, fix what broke, commit
with a detailed message — just without pausing between them for a
go-ahead. The verification rigor didn't relax; only the approval
cadence did.
