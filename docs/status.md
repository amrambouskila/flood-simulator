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
- Test suite added: `tests/test_models.py`, 57 tests, 100% statement + branch coverage on `models.py`
- `pyproject.toml` added with pytest and coverage config (scoped to `models`)
- GitHub Actions CI `test` job now delegates coverage source/threshold to `pyproject.toml`

### What's Next
- Add `from __future__ import annotations` to all modules
- Clean up `simulation.py` (imports a stale `create_model` symbol; currently fails at import time and is not wired into coverage)
- Add ruff config and full type annotations (`ANN` rule) once source files adopt `__future__` annotations
- Consider splitting `models.py` if it grows further
- Phase 2 planning: FastAPI backend + React frontend (not started)