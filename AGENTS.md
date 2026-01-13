# Repository Guidelines

## Project Structure & Module Organization
- `collectors/` gathers source data (X, YouTube, charts).
- `analyzers/` computes the Signal Index (`influence_score.py`).
- `data/` stores generated CSVs (for example `data/x_data.csv`, `data/rankings.csv`).
- `artists.json` is the human-editable artist list.
- `config.py` contains settings and artist helpers.
- Entry points: `update_data.py`, `update_charts.py`, `dashboard.py`.

## Build, Test, and Development Commands
- Install deps: `pip install -r requirements.txt`.
- Configure secrets: `cp .env.example .env` then add API keys.
- Collect daily data: `python update_data.py` (writes CSVs to `data/`).
- Collect chart data: `python update_charts.py` (writes `data/chart_data.csv`).
- Run the UI: `streamlit run dashboard.py` (use `--server.port 8502` if 8501 is busy).

## Coding Style & Naming Conventions
- Python, 4-space indentation, PEP 8-style layout.
- Use `snake_case` for functions/variables and `UPPER_SNAKE_CASE` for constants.
- Keep modules focused by layer: collectors fetch, analyzers compute.
- No formatter or linter is configured; match existing style in the file you touch.

## Testing Guidelines
- No automated test suite is currently configured.
- Manual check: run `python update_data.py` and confirm CSVs update, then open the dashboard.
- If you add tests, document how to run them here and keep names like `test_*.py`.

## Commit & Pull Request Guidelines
- Recent commits use sentence-style summaries (example: `Add multi-source chart data collection...`).
- Automated updates use `🤖 Automated data update - YYYY-MM-DD HH:MM`.
- PRs should describe what changed, list any new data files, and include screenshots for UI changes.
- Never commit `.env`; it contains secrets.

## Security & Configuration Tips
- Store API keys only in `.env` and keep it out of git.
- `data/` is generated output; avoid manual edits unless you are correcting data sources.
