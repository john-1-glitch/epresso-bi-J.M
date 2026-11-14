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
- [x] **Sleek Modern Dark-Mode UI & Final Submission Docs:** Redesigned `streamlit_app.py` in a sleek modern dark-mode layout (carbon-black grid background, live status header, full-width 4-column top nav, smooth transitions, 4 KPIs + 4 interactive charts on the start page). Embedded before/after `+$1,000` screenshots in `docs/validation.md` and all 5 agent test + tool-call log screenshots in `docs/agent_tests.md`. Finalized `docs/reflection_draft.md`, `docs/team_contribution.md`, and `README.md`, and set `thinking_budget=0` + `45s` timeout so Gemini answers in ~2s. All deliverables complete.

## Key Decisions
- **High-level understanding only:** Keep explanations concise and high-level (no line-by-line code defense walkthroughs).
- **Root file placement:** Keep `analytics.py`, `agent.py`, `streamlit_app.py`, and `requirements.txt` at repo root for Python imports and Streamlit Cloud.
