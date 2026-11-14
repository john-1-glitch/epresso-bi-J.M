# MEMORY.md — E-Presso BI Analyst (epresso-bi-J.M)

*Last updated: 2026-11-13. Keep this file strictly under 200 lines. Auto-update after every major milestone.*

## Repo & Environment
- **Local path:** `/Users/jonathanCheckmark/Documents/ClaudeOS/MSU/epresso-bi-J.M`
- **GitHub remote:** `https://github.com/john-1-glitch/epresso-bi-J.M.git` (branch `main`, macOS Keychain configured)
- **Live app URL:** `https://epreapp-bi-jm-7ysc8gurgjgzaxkaez96kq.streamlit.app/`
- **Workflow:** Push to `origin/main` after every completed stage.
- **Test runner:** `"../Data analytics/.venv/bin/python" -m pytest -v`
- **Source reference repo:** `../Data analytics/` (V1 working project)

## Milestone Status
- [x] **Repo & GitHub Setup:** Initialized local repo, merged starter template history from `origin/main`, Keychain auth working.
- [x] **Stage A — Core Analytics & Validation (`508d3fa`):** Copied `analytics.py`, `scripts/export_access.py`, `scripts/independent_check.py`, `tests/test_epresso.py`. Verified **24/24 tests passing** (`test_epresso.py` + `test_analytics.py`) and pushed to `origin/main`.
- [x] **Stage B — AI Agent & Guardrails (`67d1e95`):** Copied `agent.py`, `tests/test_tools.py`, `tests/test_llm.py`. Verified **91/91 tests passing** across the full suite and pushed to `origin/main`.
- [x] **Stage C — Streamlit UI (`710263e`):** Copied `streamlit_app.py` with short `Answered by: Gemini` / `Answered by: Rules` label. Deployed on `share.streamlit.io` with `GEMINI_API_KEY` in Secrets and verified file upload works.
- [x] **Stage D — Documentation (`3c8124c`):** Added `README.md` (with live URL) and `docs/`.
- [x] **UI & Preload Upgrade:** Added Apple-inspired Liquid Glass theme (white `#FFFFFF` background, dark green `#14532D` accent via `.streamlit/config.toml` + CSS) and default data auto-loading from `data/raw/` with uploaded-file priority. Remaining: test `Sales_PLUS_1000_TEST.csv` on the live URL, rewrite `reflection_draft.md` in own words, and fill in `team_contribution.md`.

## Key Decisions
- **High-level understanding only:** Keep explanations concise and high-level (no line-by-line code defense walkthroughs).
- **Root file placement:** Keep `analytics.py`, `agent.py`, `streamlit_app.py`, and `requirements.txt` at repo root for Python imports and Streamlit Cloud.
