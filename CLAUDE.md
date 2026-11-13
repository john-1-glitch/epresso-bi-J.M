# CLAUDE.md — E-Presso BI Analyst (epresso-bi-J.M)

## Project Goal
Build and deploy a hosted Streamlit BI dashboard + tool-based AI analytical assistant for the E-Presso dataset (MSU Data Science / Analytics project, 70 points, due 2026-11-15 11:59 PM).

## Working Style & Continuity Rules
- **Keep both `CLAUDE.md` and `MEMORY.md` strictly under 200 lines.** Trim or summarize older details rather than growing past 200 lines.
- **Auto-update `MEMORY.md` after every major milestone** (Stage A, B, C, D, deployment, validation) so any agent can immediately resume work without losing context.
- **Super high-level explanations only:** Explain *what* each component does at a high level, not line-by-line code walkthroughs.
- **Staged commits & pushes:** Build and test one stage at a time, commit locally, and push to `origin/main` after each stage passes.
- **Reuse before rebuilding:** Pull proven components from `../Data analytics/` rather than rewriting from scratch.

## Folder Layout (Keep Core Python Files at Root)
- `streamlit_app.py` — Streamlit UI, sidebar filters, charts, and chat interface.
- `analytics.py` — Data loading (`.accdb`, `.csv`, `.xlsx`), cleaning, `check_merge()`, metrics, and 10 `ToolResult` functions (no Streamlit code).
- `agent.py` — Tool registry, `run_tool()` dispatcher, Gemini function calling + rules-based fallback, and number verification.
- `tests/` — Pytest suite on synthetic data (`../Data analytics/.venv/bin/python -m pytest`).
- `scripts/` — `export_access.py` and `independent_check.py`.
- `docs/` — Grain table, data profile, Power BI reconciliation, validation, agent tests, reflection, and team contribution.
- `data/raw/` — Unmodified source files (not committed if large/local, or kept local).
- `.streamlit/secrets.toml` — Local API keys (gitignored; never commit keys).

## Non-Negotiable Assignment Rules
1. **No hardcoding:** Filter options, KPIs, and chart values must come from loaded data.
2. **Merge safety:** Wrap every join in `check_merge()` so rows (25,200) and revenue ($42,174,440) never duplicate or drop. Survey Results is NOT joined to Sales (different grain).
3. **Cache key:** `@st.cache_data` must key on uploaded file bytes so the `+$1,000` test updates without a restart.
4. **Assistant guardrails:** Fixed tool set only (no `eval()`, `exec()`, LangChain pandas agent, PandasAI, or free-form SQL/pandas). State scope, distinguish Findings vs. Interpretation vs. Next steps, refuse profit/forecast claims, note correlation != causation, limit ~15 questions/session, and show a tool-call log.
