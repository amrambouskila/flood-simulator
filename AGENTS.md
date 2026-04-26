# Flood-Adjusted Radiometric Dating Simulator (FAC14) - AGENTS.md

> **MANDATORY WORKFLOW: READ THIS ENTIRE FILE BEFORE EVERY CHANGE.** Every time. No skimming, no assuming prior-session context carries over -- it does not.
>
> **Why:** This project spans multiple sessions and months of development. Skipping the re-read produces decisions that contradict the architecture, duplicate existing patterns, break data contracts, or introduce tech debt that compounds.
>
> **The workflow, every time:**
> 1. Read this entire file in full.
> 2. Read the master plan document: `docs/FLOOD_SIMULATOR_MASTER_PLAN.md`.
> 3. Read `docs/status.md` -- current state / what was just built.
> 4. Read `docs/versions.md` -- recent version history.
> 5. Read the source files you plan to modify -- understand existing patterns first.
> 6. Then implement, following the rules and contracts defined here.

---

## 0. Critical Context

This is a **Torah-science research tool**, not a debunking tool and not an apologetics gimmick. The simulation must be **mathematically rigorous** -- every formula is standard radiometric dating math, every parameter has physical meaning, and every output is reproducible given the inputs.

The core thesis: standard radiometric dating relies on two assumptions -- (1) decay rates have always been constant, and (2) initial daughter isotope concentrations were zero. If either assumption is wrong, the calculated ages are wrong. This simulator lets users explore what happens when those assumptions are relaxed in ways consistent with the Torah's account of Creation and the Flood.

**What this project is NOT:**
- Not a standalone microservice in a larger system -- it is a self-contained simulation tool
- Not a data pipeline or API -- it is an interactive Streamlit application
- Not a production web app (yet) -- Phase 1 is Streamlit; Phase 2 would upgrade to FastAPI + React

**Mathematical rigor is non-negotiable.** Every formula in `models.py` must be traceable to standard nuclear physics equations. The flood-adjusted model changes the *inputs* to those equations (initial conditions, acceleration factors), not the equations themselves.

---

## 1. Project Identity

- **Name:** Flood-Adjusted Radiometric Dating Simulator (FAC14)
- **Location:** `flood-simulator/`
- **Master plan:** `docs/FLOOD_SIMULATOR_MASTER_PLAN.md`
- **Current phase:** Phase 1 -- Streamlit interactive app (complete and functional)
- **Stack:** Python 3.13, Streamlit, NumPy, Plotly, matplotlib, pandas
- **Entry point:** `app.py` (Streamlit) and `fac14_main.py` (CLI)

---

## 2. Phase Constraints

### Phase 1 (Current): Streamlit Interactive App
**Status:** Complete and functional. All core features working.

**In scope:**
- Interactive Streamlit UI with sidebar parameter controls
- C-14 dating simulation (pre-flood atmosphere, flood event, post-flood recovery)
- Long-age radiometric dating (U-Pb, K-Ar, Rb-Sr) with epoch-by-epoch decay tracking
- Plotly interactive charts (6 tabs: Big Picture, Long-Age Isotopes, C-14 Age Comparison, C-14 Ratio, Initial C-14, The Math)
- CLI entry point for batch simulations
- Docker containerization (single service)
- Launcher scripts (macOS + Windows)

**Explicitly deferred to Phase 2:**
- FastAPI backend with proper API endpoints
- React + TypeScript frontend replacing Streamlit
- Database persistence (PostgreSQL)
- WebSocket streaming for real-time parameter updates
- Additional isotope systems beyond U-Pb, K-Ar, Rb-Sr

**Explicitly deferred to Phase 3:**
- Geological column modeling (sedimentary layer simulation)
- Isochron diagram generation
- Multi-sample concordance analysis
- Export to publication-ready figures

**Do NOT add backend API endpoints, database models, or React components in Phase 1.**

---

## 3. Architecture & Code Rules

### Python conventions
- **`from __future__ import annotations`** at the top of every module (not yet applied to existing files -- add when modifying them)
- Full type annotations on every function signature
- `snake_case` for modules, functions, variables; `PascalCase` for classes; `UPPER_SNAKE_CASE` for constants
- ruff for linting: `line-length = 120`, rules: `["E", "F", "I", "N", "UP", "ANN"]`
- No `Any` type without explicit justification
- No bare `except:` clauses -- always catch specific exception types
- No dead code, no commented-out blocks, no unused imports

### File organization
- One concept per file. Each class, utility function, and model gets its own file.
- Current state: `models.py` contains multiple classes (StandardModel, FloodAdjustedModel, RadiometricSystem, LongAgeRadiometricSuite) plus constants. This is acceptable for Phase 1 but should be split if the file grows beyond its current size.
- `simulation.py` contains the `CarbonSimulation` class (CLI-oriented, references an older `create_model` API that no longer exists in `models.py`). This file needs cleanup if the CLI path is maintained.
- `visualization.py` contains matplotlib and Plotly helper functions for the CLI path.
- `app.py` is the Streamlit frontend -- it imports directly from `models.py`.

### Constants and data-driven values
- All physical constants live in `models.py` at module level: `CARBON_14_HALF_LIFE`, `LAMBDA`, `ISOTOPE_SYSTEMS`, etc.
- Torah timeline constants: `FLOOD_YEAR`, `CURRENT_YEAR`, `YEARS_SINCE_FLOOD`, `CREATION_WEEK_YEARS`, `FLOOD_YEAR_YEARS`
- Isotope system data (half-lives, decay constants) live in the `ISOTOPE_SYSTEMS` dict
- Default parameter values live as class attributes on `FloodAdjustedModel` and `LongAgeRadiometricSuite`
- **No magic numbers in computation logic.** Every numerical constant must be named and documented.

### Domain variable naming
Use domain-standard names from nuclear physics:
- `P` -- parent isotope amount (normalized)
- `D` -- daughter isotope amount (normalized)
- `lam` or `lambda_` -- decay constant (lambda is a Python keyword)
- `t` or `dt` -- time / time interval
- `R` or `R_0` -- C-14/C-12 ratio (current / initial)
- `A` -- acceleration factor

### Comments
- Default to no comments. Code should be self-explanatory via naming.
- Write a comment only when the *why* is non-obvious: a hidden constraint, a subtle invariant, a domain-specific assumption.
- Never write comments that restate what the code does.

---

## 4. Containerization

### Current Docker setup
- **Dockerfile:** `python:3.13-slim`, installs from `requirements.txt`, copies `models.py` and `app.py`, runs Streamlit on port 8501
- **docker-compose.yml:** Single service `fac14`, port `${PORT:-8501}`, `restart: unless-stopped`
- **No healthcheck** -- appropriate for a single-service Streamlit app
- **No volumes** -- no persistent data in Phase 1
- **No depends_on** -- single service

### Launcher scripts
- `fac14_service.sh` (macOS/Linux) and `fac14_service.bat` (Windows)
- Implement the `[k]/[q]/[r]` shutdown/restart loop
- Note: current launchers use `[r]` as "full reset & restart" (down + remove volumes + remove images + rebuild). This is closer to the `[v]` behavior in the canonical template. The `[r]` in the canonical template is a lightweight restart (down + up --build). Consider aligning in a future cleanup.
- Auto-opens browser on start and restart

### Dockerfile gaps
- `Dockerfile` only copies `models.py` and `app.py`. If other files are needed at runtime (e.g., `visualization.py`), the COPY directive must be updated.
- No `.dockerignore` file exists yet.

---

## 5. CI/CD

### Pipeline (`.gitlab-ci.yml`)
Required stages:
1. **lint** -- `ruff check .` (fail on any error)
2. **test** -- `pytest --cov` (fail on any test failure)
3. **coverage** -- 100% coverage gate on core logic (`models.py`, `simulation.py`)
4. **build** -- verify Python package builds cleanly
5. **docker-build** -- `docker build .` to verify Dockerfile integrity

### Not yet implemented
- No `.gitlab-ci.yml` exists yet
- No `pyproject.toml` with ruff/pytest config yet
- No test suite exists yet
- These are infrastructure gaps to fill

---

## 6. Environment Configuration

### `.env` structure
```
PORT=8501                    # Streamlit server port
```

Single environment variable. No secrets, no database credentials, no API keys in Phase 1.

### Port configuration
- Streamlit: `${PORT:-8501}` (in docker-compose.yml and launcher scripts)

---

## 7. Domain Model & Data Contracts

### Core models (all in `models.py`)

#### `StandardModel`
Standard C-14 dating model. Assumes constant atmospheric C-14 and constant decay rate.
- `calculate_age(c14_ratio: float) -> float` -- standard age calculation: `t = -ln(ratio) / lambda`
- `predict_ratio(age: float) -> float` -- standard prediction: `ratio = e^(-lambda * t)`

#### `FloodAdjustedModel`
C-14 model accounting for flood effects on atmospheric C-14.

Parameters (all settable as instance attributes):
| Parameter | Type | Default | Units | Description |
|-----------|------|---------|-------|-------------|
| `pre_flood_c14_ratio` | float | 0.30 | fraction | Pre-flood atmospheric C-14 relative to today |
| `water_vapor_canopy` | float | 0.70 | fraction | Cosmic ray shielding from water vapor canopy |
| `magnetic_field_factor` | float | 2.0 | multiple | Pre-flood magnetic field strength vs today |
| `flood_temperature_c` | float | 100.0 | degrees C | Flood water temperature |
| `water_depth_feet` | float | 90000.0 | feet | Maximum flood water depth |
| `post_flood_equilibrium_years` | int | 2000 | years | Time for C-14 to reach modern equilibrium |
| `volcanic_activity_factor` | float | 1.5 | multiple | Post-flood volcanic CO2 dilution factor |
| `ocean_reservoir_factor` | float | 0.60 | fraction | Ocean C-14 absorption factor |
| `burial_depth_m` | float | 0.0 | meters | Sample burial depth |

Key methods:
- `effective_initial_c14(true_age) -> float` -- actual C-14 ratio when organism died
- `predict_measured_ratio(true_age) -> float` -- C-14 ratio measured today
- `standard_date_for_true_age(true_age) -> float` -- what standard dating reports
- `generate_comparison_data(max_true_age, steps) -> dict` -- arrays for plotting

#### `RadiometricSystem`
Single parent-daughter isotope system tracked through biblical epochs.

Constructor parameters:
- `system_key: str` -- key into `ISOTOPE_SYSTEMS` dict ('U-Pb', 'K-Ar', 'Rb-Sr')
- `initial_daughter_ratio: float` -- D/P ratio at Creation (default 0.0)
- `creation_acceleration_log10: float` -- log10 of decay acceleration during Creation Week (default 11.0)
- `flood_acceleration_log10: float` -- log10 of decay acceleration during Flood year (default 0.0)

Key methods:
- `apparent_age() -> float` -- what standard dating would report
- `daughter_parent_ratio() -> float` -- current D/P ratio
- `get_epoch_breakdown() -> list[dict]` -- per-epoch P and D values

#### `LongAgeRadiometricSuite`
Groups all long-age isotope systems with shared acceleration settings.
- `apparent_ages() -> dict[str, float]` -- apparent age for each system
- `summary_table() -> list[dict]` -- formatted summary for display

### Constants
| Constant | Value | Units | Source |
|----------|-------|-------|--------|
| `CARBON_14_HALF_LIFE` | 5730 | years | Standard accepted value |
| `LAMBDA` | ln(2)/5730 | per year | Derived |
| `FLOOD_YEAR` | 1656 | years from Creation | Hebrew calendar |
| `CURRENT_YEAR` | 5787 | years | Current Hebrew year |
| `YEARS_SINCE_FLOOD` | 4131 | years | Derived |
| `CREATION_WEEK_YEARS` | 6/365.25 | years | 6 days |
| `FLOOD_YEAR_YEARS` | 1.0 | years | ~365 days |

### Isotope systems data
| System | Parent | Daughter | Half-life (years) |
|--------|--------|----------|--------------------|
| U-Pb | U-238 | Pb-206 | 4.468 x 10^9 |
| K-Ar | K-40 | Ar-40 | 1.248 x 10^9 |
| Rb-Sr | Rb-87 | Sr-87 | 48.8 x 10^9 |

---

## 8. Required Calculations / Formulas

### C-14 Standard Dating
```
t = -ln(R_measured) / lambda
```
Where `lambda = ln(2) / 5730` and `R_measured` is the normalized C-14/C-12 ratio.

### C-14 Full Equation (with initial ratio)
```
t = -ln(R_measured / R_0) / lambda
```
If `R_0 < 1.0`, the overestimation is exactly `-ln(R_0) / lambda` years.

### Flood-Adjusted C-14 Ratio at Death
For pre-flood organisms:
```
R_0 = pre_flood_c14_ratio * cosmic_ray_shielding
cosmic_ray_shielding = (1 / magnetic_field_factor) * (1 - water_vapor_canopy)
```

For post-flood organisms (exponential buildup):
```
tau = post_flood_equilibrium_years / 3.0
R_0 = (1 - (1 - pre_flood_c14_ratio) * exp(-years_after_flood / tau)) * volcanic_dilution * ocean_reservoir
```

### Long-Age Radiometric Dating (Standard)
```
t_apparent = (1 / lambda) * ln(1 + D/P)
```
Where `lambda = ln(2) / half_life`, `D` = daughter amount, `P` = parent amount.

### Epoch Evolution (per epoch)
Starting with `P_0 = 1.0` and `D_0 = initial_daughter_ratio`:
```
P_after = P_before * exp(-A * lambda * dt)
D_after = D_before + (P_before - P_after)
```
Where `A` = acceleration factor and `dt` = epoch duration.

### Epochs
1. **Creation Week:** dt = 6/365.25 years, A = 10^(creation_accel_log10)
2. **Pre-Flood:** dt = FLOOD_YEAR - CREATION_WEEK_YEARS, A = 1
3. **Flood Year:** dt = 1 year, A = 10^(flood_accel_log10)
4. **Post-Flood:** dt = YEARS_SINCE_FLOOD, A = 1

---

## 9. Directory Structure

```
flood-simulator/
├── AGENTS.md                     # This file -- AI operational schema
├── README.md                     # Human-facing project overview
├── app.py                        # Streamlit frontend (main entry point)
├── models.py                     # All domain models, constants, and isotope data
├── simulation.py                 # CarbonSimulation class (CLI-oriented)
├── visualization.py              # matplotlib + Plotly helpers for CLI
├── fac14_main.py                 # CLI entry point
├── requirements.txt              # Python dependencies
├── Dockerfile                    # python:3.13-slim + Streamlit
├── docker-compose.yml            # Single service: fac14 on port 8501
├── fac14_service.sh              # macOS/Linux launcher
├── fac14_service.bat             # Windows launcher
├── .gitignore                    # Standard Python + Docker + Claude ignores
├── .gitlab-ci.yml                # CI/CD pipeline
├── .env                          # Local env vars (gitignored)
├── .codex/
│   ├── settings.json             # Hooks (SessionStart, PreToolUse, PostToolUse, PreCompact, Stop)
│   ├── commands/                 # Slash commands
│   │   ├── scaffold.md
│   │   ├── review.md
│   │   ├── pre-commit.md
│   │   ├── validate.md
│   │   └── phase-status.md
│   └── skills/                   # Proactive protocol skills
│       ├── phase-awareness/SKILL.md
│       ├── data-driven-check/SKILL.md
│       └── validation-protocol/SKILL.md
├── docs/
│   ├── FLOOD_SIMULATOR_MASTER_PLAN.md  # Authoritative project specification
│   ├── status.md                       # Current project state
│   └── versions.md                     # Semver changelog
└── tests/                              # Test suite (to be created)
    ├── test_models.py
    └── test_simulation.py
```

---

## 10. Local Commands

### Docker (primary)
```bash
# Start
./fac14_service.sh          # macOS/Linux
fac14_service.bat            # Windows

# Opens http://localhost:8501 automatically
# Menu: [k] stop, [q] stop + remove images, [r] full reset & restart
```

### Local (without Docker)
```bash
pip install -r requirements.txt

# Streamlit app
streamlit run app.py

# CLI
python fac14_main.py --age 5000 --model flood --plot
python fac14_main.py --help
```

### Lint
```bash
ruff check .
ruff format --check .
```

### Test
```bash
pytest --cov=. --cov-report=term-missing
```

---

## 11. Testing Requirements

- **Framework:** pytest with pytest-cov
- **Coverage target:** 100% on core logic (models.py computation methods)
- **Test location:** `tests/` directory, mirroring source structure
- **Numerical comparisons:** Use `np.testing.assert_allclose(actual, expected, atol=..., rtol=...)` with documented tolerances. Never `==` for floats.
- **Reference values:** At least one test per model must validate against a known analytical solution:
  - `StandardModel.calculate_age(0.5)` must equal exactly one half-life (5730 years)
  - `StandardModel.predict_ratio(5730)` must equal 0.5
  - `RadiometricSystem` with zero initial daughter and zero acceleration must produce `apparent_age == CURRENT_YEAR`
  - Epoch evolution must conserve parent + daughter (mass conservation)
- **No mocking of physics calculations.** Test against real computations.
- **Parametrize** tests for multiple isotope systems using `@pytest.mark.parametrize`
- **No test suite exists yet.** This is a gap to fill.

---

## 12. Change Policy & Documentation

### When to update docs
- **`docs/status.md`**: After every significant change (new feature, bug fix, architecture decision)
- **`docs/versions.md`**: After every change that would constitute a version bump
- **`AGENTS.md`**: When domain models change, when phase transitions occur, when architectural decisions are made

### Versioning
- Source of truth: not yet in a `pyproject.toml` -- version is tracked in `docs/versions.md` only for now
- Current version: v0.1.0 (initial Streamlit app)
- Follow semver: patch for fixes, minor for features, major for breaking changes

### Hands off git
I manage all git operations myself. You do not run any git command that changes state. Read-only git is fine (`git status`, `git diff`, `git log`, `git show`, `git blame`). When you finish a task, report what files changed, suggest a commit message, and stop.

---

## 13. Output & Completion Expectations

At the end of every non-trivial task, run through this checklist:

1. **Summary** -- one or two sentences: what changed and why.
2. **Reuse check** -- confirm you searched for existing utilities before writing new ones.
3. **Tech-debt check** -- no shortcuts, no hacks, no duplicated logic, no `Any`, no dead code.
4. **File-organization check** -- one concept per file, no god files created.
5. **Data-contract check** -- no typed interfaces changed without approval.
6. **Math check** -- all formulas traceable to standard radiometric dating equations, all units documented.
7. **Docs check** -- list every `docs/` file updated.
8. **Test check** -- list tests added or updated.
9. **Forward-compatibility check** -- does this work align with Phase 2 (FastAPI + React)?
10. **Git state** -- report files changed, suggest commit message.

---

## 14. Closing Reminder

Re-read this file before the next change. Every rule here exists because it has been needed. The simulation must be mathematically correct, the code must be clean, and the documentation must be current. No exceptions.