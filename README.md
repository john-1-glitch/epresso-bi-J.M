# E-Presso BI Analyst

## What this application does

E-Presso BI Analyst is an interactive business intelligence dashboard and tool-based AI analytical assistant built for E-Presso retail managers. It opens preloaded with the company's sales, store, category, product, and survey datasets so every KPI, chart, and table works immediately on load. Any replacement file uploaded in the sidebar automatically overrides the default table and recalculates every number on screen without touching the code. A built-in analytical assistant answers plain-English business questions (such as *"Which sales channel experienced the greatest revenue growth?"*) by invoking approved Python functions and showing the exact calculation log behind every answer.

## Live app

**[epreapp-bi-jm-7ysc8gurgjgzaxkaez96kq.streamlit.app](https://epreapp-bi-jm-7ysc8gurgjgzaxkaez96kq.streamlit.app/)**

The app may take a moment to wake up if nobody has used it recently. It opens preloaded with the default E-Presso dataset from `data/raw/`, and any file you upload in the sidebar immediately takes priority over the default for that table.

## How to use it

By default, the app loads the original course files from `data/raw/` automatically. To test modified or updated data (such as the `+$1,000` test), upload a replacement file into the corresponding sidebar slot—uploaded files always take priority, and the sidebar's **Active sources** list shows whether each table is using its `Default` or `Uploaded` file:

| Upload box | Default file in `data/raw/` | Notes |
|---|---|---|
| Sales | `Support_EX_B_Sales.accdb` | Reads Sales, Categories, and Products from the Access database; if you upload a modified `Sales.csv` alone, Categories and Products still fall back to the default Access database automatically |
| Stores | `Support_EX_B_Stores.csv` | Tab-separated; the app auto-detects the delimiter |
| Survey Results (optional) | `Support_EX_B_Survey.xlsx` | Automatically locates the "Survey Results" sheet and promotes row 3 to the header |

CSV or Excel exports also work, one per table (for example `Sales.csv`, `Categories.csv`, and `Products.csv` exported with `scripts/export_access.py`). In a workbook or database, the app selects the sheet or table containing the required columns, names any missing required column cleanly instead of crashing, and recalculates everything dynamically when rows, stores, categories, or years change.

The interface is organized into four top-level views in a sleek, modern dark-mode layout:
1. **`01 // COMMAND DASHBOARD` (Start Page):** Interactive `Year`, `Channel`, `Store`, and `Category` filters (all built dynamically from the loaded data), four KPI telemetry cards (`Revenue in Selection`, `Website Channel`, `Period Trajectory`, and `Active Stores`), and four interactive Plotly visualizations (`01 // Channel Trajectory`, `02 // Product Category Telemetry`, `03 // Monthly Seasonality & Cumulative Curve`, and `04 // Top Performing Stores in Selection`), with expandable table views.
2. **`02 // ANALYTICAL AGENT`:** Conversational assistant (up to 15 questions per session) with a prominent **`Answered by: Gemini`** or **`Answered by: Rules`** badge on the top line of every reply and an expandable **Tool-call log**.
3. **`03 // REVENUE & MERGE AUDIT`:** Total revenue summary, interactive year-by-year revenue cards (plus table view), and the `check_merge()` verification audit for every table join.
4. **`04 // DATA & QUALITY`:** Table grain statements, automated data-quality checks, and an interactive table profiler (rows, columns, duplicates, missing values, and data types).

## Data model

Every lookup table joins to Sales many-to-one on a unique key, so no join can duplicate or drop revenue.

| Table | One row = | Key | Rows | Contains revenue? |
|---|---|---|---|---|
| Sales | one product at one store in one month | `Sales ID` | 25,200 | Yes |
| Stores | one store (the website counts as store SH00) | `ID` | 21 | No |
| Categories | one product category | `Category ID` | 5 | No |
| Products | one product | `Product ID` | 20 | No |
| Survey Results | one store's survey in one year | `Survey ID` | 105 | No |

The Sales row count confirms its grain: 21 stores × 20 products × 60 months = 25,200 rows. Sales joins to Stores on `Store ID`, to Categories on `Category ID`, and to Products on `Product ID`. Each join runs through `check_merge()`, which compares rows and revenue before and after and counts unmatched keys. On the real data, all three joins keep 25,200 rows and $42,174,440, with no unmatched keys.

Survey Results is deliberately not joined to Sales. It is one row per store per year, so joining it would repeat each satisfaction score on 240 sales rows. Full profile: [`docs/data_profile.md`](docs/data_profile.md).

## Metric definitions

**Revenue** is the sum of the `Revenue` column in the Sales table for the rows in scope. Rows with blank or non-numeric revenue are left out of the sum and counted in the Data Quality section; no row is ever deleted. **Share** is a group's revenue divided by the revenue of everything in the current scope. **Channel** is the store's `StoreType`: "Website" for online sales and "Brick & Mortar" for the 20 physical stores.

Revenue is not profit. The data has no costs, discounts, or margins, so nothing in this app describes profitability.

## Assistant

I built **Option A, a live language-model agent** using Google Gemini with function calling, with the rules-based assistant (Option B) as its automatic fallback. Every answer displays a top-line badge (`Answered by: Gemini` or `Answered by: Rules`) as well as the specific model details at the bottom.

- **Gemini mode (when `GEMINI_API_KEY` is set):** Gemini reads the question and chooses one approved function and its arguments through function calling in `VALIDATED` mode, which constrains it to the listed functions and their schemas (with `thinking_budget=0` for fast ~2–3 second responses). Our code runs the function on the loaded data. Gemini then writes Findings, Interpretation, and Next steps from the tool result. Before the app shows that text, `unsupported_numbers()` checks every number in it against the tool result (allowing for rounding, thousands, millions, and percentages); if any number cannot be traced, the app shows the deterministic standard answer instead and explains why. Gemini never sees the raw dataset.
- **Backup model:** The free tier allows about 20 requests per model per day. On a `429` (quota), `503` (overload), or timeout error, `_with_backup()` automatically retries once on `gemini-3.5-flash-lite`.
- **Rules-based mode (no key, or Gemini still fails):** Keyword rules choose the function and a deterministic template writes the answer from the result, displaying a notice explaining the switch.

| Tool | What it calculates | Arguments |
|---|---|---|
| `total_revenue` | Revenue in scope and its share of all revenue | year, channel, store |
| `revenue_by_year` | Revenue for each year, the best and worst year, and the change from first to last year | channel, store |
| `monthly_revenue_share` | Revenue and share for each calendar month, with the strongest and weakest month | year, channel, store |
| `revenue_by_category` | Revenue and share for each product category | year, channel, store |
| `revenue_by_channel` | Revenue and share for Website vs Brick & Mortar | year, store |
| `top_stores` | The n stores with the most revenue, with shares | year, channel, n |
| `revenue_change_by_store` | Each store's change between two years, the largest % decline and growth, or a plain statement that no store declined | start_year, end_year, channel |
| `revenue_change_by_channel` | Each channel's change between two years and which grew the most | start_year, end_year, store |
| `satisfaction_vs_revenue` | Correlation between store-year revenue and survey satisfaction, excluding store-years without a score | year |
| `data_quality_report` | Rows, duplicates, and missing values | none |

Every tool checks its arguments against the loaded data and returns a clear error for an unknown year, channel, or store, or for a city that matches two stores; it never guesses. Every result follows the same contract: `tool`, `value`, `definition`, `scope`, `rows_used`, and `caveats`. Each answer starts with its scope and notes that it uses the full loaded dataset (if dashboard filters are active, the Assistant tab reminds the user that sidebar filters do not apply to chat). Then come Findings, Interpretation, Next steps, and an expandable tool-call log showing the function, arguments, raw JSON result, and model used. Sessions are limited to 15 questions.

**Limits it enforces:** Profit, margin, forecast, and customer-level questions are refused before any model is called, with the reason and a list of supported topics. "Why" and "does X cause Y" questions return the relevant evidence plus a clear statement that the data shows association, not causation. "Should we..." decision questions return the evidence, state *"No recommendation is supported by this data"*, and list the missing information a real decision would require (operating expenses, store profitability, lease obligations, staffing, customer behavior). Scope, caveats, and these limits are enforced by Python code, not left to the model.

**What it is not allowed to do:** Run or write code, use `eval()` or `exec()`, write free-form SQL or pandas, mutate the loaded data, or state a number our functions did not calculate.

## Validation

Full evidence: [`docs/validation.md`](docs/validation.md) (Power BI comparison table, independent check, and `$1,000` test record with before/after screenshots) and [`docs/agent_tests.md`](docs/agent_tests.md) (five required agent tests plus documented fixes and retests).

**Power BI comparison.** All five required measures plus revenue by category match our Power BI report (`Fleischnamnn_Mey_NP_EX_B_EPresso.pbix`) exactly: total $42,174,440, Website $27,218,880, Brick & Mortar $14,955,560, every year, and every month's share (December is 25.61%). All 25,200 sales rows are identical row by row. One modeling difference is documented in [`docs/powerbi_reconciliation.md`](docs/powerbi_reconciliation.md): Power BI links Sales to Stores through the survey table, whereas this app joins Sales to Stores directly.

**Independent check.** [`scripts/independent_check.py`](scripts/independent_check.py) recalculates every measure with plain pandas and none of the app's code, producing identical results.

**$1,000 test.** Adding $1,000 to Sales row `S0020250101` and uploading the modified file in the sidebar raised Total Revenue from $42,174,440.00 to $42,175,440.00 and Website revenue from $27,218,880.00 to $27,219,880.00 immediately—with no code changes and no restart—because `@st.cache_data` is keyed on the uploaded file bytes. Before and after screenshots are embedded in [`docs/validation.md`](docs/validation.md).

**Automated tests.** 91 unit tests in `tests/` run on a hand-verifiable six-row synthetic dataset. They cover revenue totals, merge checks (including duplicate store key fan-out and unmatched keys), missing columns, Excel header promotion, Access upload, filters, all 10 assistant tools, the dispatcher, both routers, the number verifier, backup-model retry, and rules fallback.

## Limitations

- **Revenue is not profit.** There are no costs or margins, so the app cannot say which stores or products are most profitable.
- **No causes.** The data shows what happened and what moves together, not why.
- **Monthly totals only.** Sales are monthly totals per store and product, with no customer, transaction, or daily detail.
- **Channel is a mapping.** Channel comes from `StoreType` ("Website" for store `SH00` vs. "Brick & Mortar" for stores `SH01`–`SH20`).
- **Satisfaction is thin evidence.** It is one annual score per physical store (the website is not surveyed), and correlation with revenue is weak (`r = 0.235`).
- **Gemini free-tier quota.** Free-tier access allows ~20 requests per model per day (2 calls per question). When quota is exhausted, the app automatically switches to the backup model and then the rules-based assistant.

## Files

| File / Folder | Purpose |
|---|---|
| `streamlit_app.py` | Sleek modern dark-mode UI, preloaded data + upload override, interactive filters, 4 KPIs, 4 Plotly charts, and chat interface |
| `analytics.py` | Loading (CSV, Excel, Access), cleaning, `check_merge()`, dashboard metrics, and 10 `ToolResult` functions (no Streamlit code) |
| `agent.py` | Tool registry, `run_tool()` dispatcher, rules router, Gemini `VALIDATED` function-calling router + explanation, backup retry, and number guard |
| `.streamlit/config.toml` | Dark-mode theme palette and typography settings |
| `data/raw/` | Preloaded default E-Presso files (`Support_EX_B_Sales.accdb`, `Support_EX_B_Stores.csv`, `Support_EX_B_Survey.xlsx`) |
| `tests/` | 91 `pytest` unit tests on hand-checkable synthetic data and mocked LLM responses |
| `scripts/export_access.py` | Exports the Access database tables to CSV |
| `scripts/independent_check.py` | Independent recalculation of the 5 validation measures using plain pandas |
| `docs/` | Data profile, Power BI reconciliation, validation evidence (with `docs/screenshots/`), agent tests, project reflection, and team contribution statement |
| `requirements.txt` | Python packages required by the hosted app |

## Run it

- **Hosted:** Deployed at [epreapp-bi-jm-7ysc8gurgjgzaxkaez96kq.streamlit.app](https://epreapp-bi-jm-7ysc8gurgjgzaxkaez96kq.streamlit.app/) from `main` with main file `streamlit_app.py`.
- **Locally (optional):** `pip install -r requirements-dev.txt`, then `streamlit run streamlit_app.py`. Run the test suite with `pytest`.

## Secrets

Never commit API keys. Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` (gitignored) and set `GEMINI_API_KEY`. On Streamlit Community Cloud, paste `GEMINI_API_KEY = "your-key"` into **App settings → Secrets**. Without a key, the app automatically runs the rules-based assistant.
