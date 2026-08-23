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
- Project infrastructure scaffolded: CLAUDE.md, master plan, docs/, .claude/ hooks and commands, .gitignore, `.github/workflows/ci.yml`
- Test suite added: `tests/test_models.py`, 57 tests, 100% statement + branch coverage on `models.py`
- `pyproject.toml` added with pytest and coverage config (scoped to `models`)
- GitHub Actions CI `test` job now delegates coverage source/threshold to `pyproject.toml`
- Container Streamlit port made symmetric with the host port (`5250` inside the container; `docker-compose.yml` maps `${PORT:-5250}:5250`). Behavior unchanged; removes the shared internal `8501` so every Streamlit app in the workspace exposes a distinct container port.

### Security
- Requirements documented: `CLAUDE.md` `<security>` (section 11a) holds the `sast` stage spec, the input-boundary inventory with injection classes and defenses, and the local scan command set; master plan carries the Security section and per-phase SAST gate lines
- Wired: `sast` job in `.github/workflows/ci.yml` (`needs: lint`; `test` carries `needs: sast`) running CodeQL `python`, `pipx run semgrep scan` with SARIF upload + fail-on-findings, `gitleaks/gitleaks-action@v2`, and `pipx run pip-audit -r requirements.txt`; Trivy (`HIGH,CRITICAL`, `exit-code: 1`) against `flood-simulator:ci` in `docker-build`, which now builds with `load: true`; ruff `S` in the lint select (`pyproject.toml` gained its first `[tool.ruff]` block) with `S101` ignored under `tests/` -- `ruff check .` clean, 57 tests pass
- Still pending: the fleet-standard `I`/`N`/`UP`/`ANN` ruff rules are NOT enabled -- turning them on surfaces 161 pre-existing import-order/annotation violations, tracked as its own task below; `.semgrep/` project rules.

### What's Next
- Add `from __future__ import annotations` to all modules
- Clean up `simulation.py` (imports a stale `create_model` symbol; currently fails at import time and is not wired into coverage)
- Add ruff config and full type annotations (`ANN` rule) once source files adopt `__future__` annotations
- Consider splitting `models.py` if it grows further
- Phase 2 planning: FastAPI backend + React frontend (not started)