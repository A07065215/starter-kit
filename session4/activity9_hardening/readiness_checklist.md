# Client-readiness checklist (Activity 9)

Score each item: done / partly / no. Swap checklists with another team and try to break their deployed app.

## Code and tests
- [ ] At least 2 pytest tests for a loader or core calculation
- [ ] 1 AppTest that opens the app and asserts `not at.exception`
- [ ] CI workflow added; latest run is green
- [ ] No notebook-style 300-line `app.py`: loaders and components are separate modules

## Security and configuration
- [ ] No keys, passwords or tokens in the repo (`git log -p | grep -i key`)
- [ ] `.streamlit/secrets.toml` is gitignored; `secrets.toml.example` documents the names
- [ ] `requirements.txt` has pinned or lower-bounded versions; a clean install works
- [ ] Database / API credentials are read-only where possible

## Robustness
- [ ] Empty filter selection shows a message, not a crash
- [ ] Data source down: friendly error, no traceback
- [ ] Heavy loads are cached; first page load under ~5 s on the deployed app
- [ ] Inputs are validated (ranges, types) before they reach a model or query

## Honest communication
- [ ] Assumptions and limits are written on the page (data period, model, known gaps)
- [ ] Forecasts and recommendations show uncertainty or a baseline comparison
- [ ] README explains how to run, update data and retrain
