# Web Implementation Module: starter kit

Starter code, solutions and datasets for the 10 activities in the Session 1-4 decks.
Every activity folder has a **starter** (runs, with TODOs) and a **solution** (hand out after the activity).

## Setup (5 minutes, do it before Session 1)

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python make_data.py                # creates ./data (about 4 seconds, seeded: identical for everyone)
streamlit run session1/activity1_starter/app.py
```

Always run commands **from the kit root** (the folder with this README); the apps find `data/` relative to their own location.

## Map: activity, folder, what you get, what students build

| # | Session | Folder | Run | Students build |
|---|---|---|---|---|
| 1 | 1 | `session1/activity1_starter/` | `streamlit run session1/activity1_starter/app.py` | Filters, KPI cards, a second chart; then deploy to Streamlit Cloud |
| 2 | 1 | `session1/activity2_solution/` | `streamlit run session1/activity2_solution/app.py` | Refactor Activity 1 into `data/loaders.py`, `components/charts.py`, thin `app.py` (this folder is the answer, with `.gitignore`, theme and `secrets.toml.example`) |
| 3 | 2 | `session2/activity3_simulator/` | `starter.py` / `solution.py` | Safety stock and reorder point, saved scenarios in `session_state`, reset callback, stretch: 90-day stockout simulation |
| 4 | 2 | `session2/activity4_clinic/` | `slow_app.py` / `fast_app.py` | Find and fix the bottlenecks using the stage timings in the sidebar |
| 5 | 2 | `session2/activity5_live_data/` | `starter.py` / `solution.py` | `st.connection` to SQLite, a cached public-API call, friendly failure |
| 6 | 3 | `session3/activity6_forecast/` | `starter.py` / `solution.py` | Seasonal naive, ETS, rolling backtest scorecard, interval, takeaway |
| 7 | 3 | `session3/activity7_optimizer/` | `starter.py` / `solution.py` | LP with PuLP: objective, constraints, infeasibility message, cost-vs-service chart |
| 8 | 4 | `session4/activity8_assistant/` | `starter_app.py` / `solution_app.py` | Harden `run_sql`, show SQL, add test questions (`python session4/activity8_assistant/run_eval.py`) |
| 9 | 4 | `session4/activity9_hardening/` | `pytest -q` from the kit root | Tests (pytest + AppTest) and CI (`ci.yml` goes to `.github/workflows/`), plus `readiness_checklist.md` |
| 10 | 4 | `session4/activity10_demo_rubric.md` | n/a | Peer-scoring sheet for the 3-minute demo |

## Data dictionary (`data/`)

| File | Rows | Used in | Columns |
|---|---|---|---|
| `sales_daily.csv` | 35,088 | 1, 2, 3, 9 | date, sku, category, region, units, unit_price, revenue (2024-2025, 12 SKUs x 4 regions) |
| `orders_large.csv` | 500,000 | 4 | order_id, order_date, customer_id, sku, region, warehouse, qty, unit_price, status, ship_days |
| `weekly_demand.csv` | 1,248 | 6, 7 | week_start, sku, units, promo, price (156 weeks from 2023-01-02, 8 SKUs, trend + yearly seasonality + promo spikes) |
| `sku_params.csv` | 12 | 3, 7 | sku, category, unit_cost, unit_price, unit_volume_m3, min_order_qty, lead_time_days, on_hand |
| `supply.db` (SQLite) | 3 tables | 5, 8 | `skus`, `orders` (30,000-row sample), `inventory` (sku x warehouse, on_hand, reorder_point) |

## Instructor notes

- **Activity 1:** common blockers are a missing `requirements.txt`, a private repo, and the CSV path. In their own repo, the CSV sits next to `app.py` (see the comment in the starter).
- **Activity 3 formulas:** protection period T = lead time + review period; safety stock = z x sigma x sqrt(T); reorder point = mean x T + safety stock. With review period 0 this is the continuous-review version on the slide.
- **Activity 4:** the slow app takes about 9 s per interaction on a laptop-class machine (apply row by row about 4 s, date parsing about 1.6 s, customer loop about 2 s); the fast one about 0.1 s after the first load. Suggested fix order for debrief: cache, vectorize, groupby, parquet and category dtypes. `fast_app.py` writes `orders_large.parquet` next to the CSV on first run.
- **Activity 5:** the exchange-rate endpoint is `https://api.frankfurter.dev/v1/latest?base=USD&symbols=MXN`. Open it in a browser before class; if it changes, any free JSON API works. Part B of the solution shows the failure path when offline.
- **Activity 6:** on this data the ETS model usually beats seasonal naive (WAPE about 9-12%) and naive loses badly: a good moment to discuss why baselines matter. ETS needs at least 2 seasons of history, so the horizon slider stops at 12 weeks.
- **Activity 7:** with the default sliders (budget 60%, capacity 80%) the plan is budget-bound. Set the service floor to 1.0 and the budget to 20% to show the infeasibility message.
- **Activity 8:** works with no API key (keyword-based mock). To use a real model, add `ANTHROPIC_API_KEY = "..."` to `.streamlit/secrets.toml` (optional `ANTHROPIC_MODEL`). The eval runner exits non-zero on failures, so it can run in CI. The SQL guard blocks non-SELECT statements, multiple statements, forbidden keywords, long queries, and opens the database read-only.
- **Activity 9:** the tests target `session1/activity2_solution`. `tests/conftest.py` only exists because the app is nested in this kit; in a student repo the app is at the root.

## Version notes

- Streamlit 1.50 or newer (the code uses `width="stretch"`).
- PuLP is pinned below 4 in `requirements.txt`: PuLP 4 changed the variable and solver API, and the course code and slides use the classic one.
- Tested with Python 3.13, pandas 3.0, Streamlit 1.66, statsmodels 0.15, scikit-learn 1.9.
