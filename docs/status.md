# Project Status

## Current Phase: Phase 1 -- Streamlit Interactive App (Complete)

### What's Built
- Full Streamlit UI with 14 sidebar parameter controls and 6 interactive tabs
- C-14 dating simulation: pre-flood atmosphere modeling, flood event effects, post-flood C-14 recovery curve
- Long-age radiometric dating: U-Pb, K-Ar, Rb-Sr with epoch-by-epoch decay tracking through Creation Week, pre-flood, Flood year, and post-flood periods
- Plotly interactive charts for all visualizations
- Headline metrics showing true age vs apparent age for all systems
- "The Math" tab with full LaTeX equations and worked examples at current settings
- CLI entry point (`fac14_main.py`) for batch simulations with matplotlib output
- Docker containerization (single service, python:3.13-slim)
- Launcher scripts for macOS (`fac14_service.sh`) and Windows (`fac14_service.bat`)

### Recent Additions
- Project infrastructure scaffolded: CLAUDE.md, master plan, docs/, .claude/ hooks and commands, .gitignore, .gitlab-ci.yml

### What's Next
- Add test suite (pytest + pytest-cov) for `models.py` core calculations
- Add `pyproject.toml` with ruff and pytest configuration
- Add `from __future__ import annotations` to all modules
- Clean up `simulation.py` (references stale `create_model` API)
- Consider splitting `models.py` if it grows further
- Phase 2 planning: FastAPI backend + React frontend (not started)