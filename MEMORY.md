# MEMORY.md — E-Presso BI Analyst (epresso-bi-J.M)

*Last updated: 2026-11-13. Keep this file strictly under 200 lines. Auto-update after every major milestone.*

## Repo & Environment
- **Local path:** `/Users/jonathanCheckmark/Documents/ClaudeOS/MSU/epresso-bi-J.M`
- **GitHub remote:** `https://github.com/john-1-glitch/epresso-bi-J.M.git` (branch `main`, macOS Keychain configured)
- **Workflow:** Push to `origin/main` after every completed stage.
- **Test runner:** `"../Data analytics/.venv/bin/python" -m pytest -v`
- **Source reference repo:** `../Data analytics/` (V1 working project)

## Milestone Status
- [x] **Repo & GitHub Setup:** Initialized local repo, merged starter template history from `origin/main`, Keychain auth working.
- [x] **Stage A — Core Analytics & Validation (`508d3fa`):** Copied `analytics.py`, `scripts/export_access.py`, `scripts/independent_check.py`, `tests/test_epresso.py`. Verified **24/24 tests passing** (`test_epresso.py` + `test_analytics.py`) and pushed to `origin/main`.
- [x] **Stage B — AI Agent & Guardrails (`67d1e95`):** Copied `agent.py`, `tests/test_tools.py`, `tests/test_llm.py`. Verified **91/91 tests passing** across the full suite and pushed to `origin/main`.
- [x] **Stage C — Streamlit UI (code pushed):** Copied `streamlit_app.py` and added a short `Answered by: Gemini` / `Answered by: Rules` label at the top of each assistant reply. Ready to deploy on `share.streamlit.io` (with `GEMINI_API_KEY` in Secrets) and run the `$1,000` modified-data test.
- [ ] **Stage D — Documentation & Submission:** Finalize `README.md` and `docs/` (`data_profile.md`, `powerbi_reconciliation.md`, `validation.md`, `agent_tests.md`, rewrite `reflection_draft.md` in own words, complete `team_contribution.md`).

## Key Decisions
- **High-level understanding only:** Keep explanations concise and high-level (no line-by-line code defense walkthroughs).
- **Root file placement:** Keep `analytics.py`, `agent.py`, `streamlit_app.py`, and `requirements.txt` at repo root for Python imports and Streamlit Cloud.
