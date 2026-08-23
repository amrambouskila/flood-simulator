# Version History

## v0.2.1

- Container Streamlit port set symmetric to the published host port: the Docker image now serves on `5250` internally (`Dockerfile` `--server.port`/`EXPOSE`/`ENV PORT`) and `docker-compose.yml` maps `${PORT:-5250}:5250`. Host port and all behavior unchanged; eliminates the shared internal `8501` so concurrent multi-app runs never collide on the container port. Workspace `PORT_ASSIGNMENTS.md` updated.

### Security documentation

- `<security>` section (11a) added to `CLAUDE.md`/`AGENTS.md`: `sast` CI stage requirement (Semgrep + CodeQL + `pip-audit` + `gitleaks`; Trivy in `docker-build`; ruff `S` rules in `lint`), input-boundary inventory for every Phase 1 boundary (Streamlit widgets, Streamlit server, CLI args, `input()` prompts, file exports, `PORT`), injection-class defenses per boundary, Phase 2 planned boundaries, and a **Security check** item in the completion checklist
- Master plan: Security section with the pipeline diagram (`lint -> sast -> test -> ...`) and the two SAST gate lines added to every phase gate list
- `docs/status.md`: Security state and next security tasks (rewritten into Wired / Pending once the wiring landed)

### Security wiring

- `.github/workflows/ci.yml`: new `sast` job (`needs: lint`, `permissions: security-events: write`) running CodeQL `python`, `pipx run semgrep scan --config auto --config p/owasp-top-ten --config p/python --config p/docker --severity ERROR --error` with SARIF upload plus a fail-on-findings step, `gitleaks/gitleaks-action@v2`, and `pipx run pip-audit -r requirements.txt`. `test` now carries `needs: sast`. `docker-build` builds with `load: true` as `flood-simulator:ci` and runs `aquasecurity/trivy-action@0.28.0` (`HIGH,CRITICAL`, `exit-code: 1`, `ignore-unfixed: true`).
- `pyproject.toml`: gained its first `[tool.ruff]` block -- `line-length = 120`, `target-version = "py313"`, `select = ["E", "F", "S"]`, and `[tool.ruff.lint.per-file-ignores] "tests/**" = ["S101"]`. `ruff check .` is clean and the 57-test suite passes.
- **Deliberate scope limit:** the fleet-standard `I`/`N`/`UP`/`ANN` rules were left off. Enabling them reports 161 pre-existing import-order and missing-annotation violations across the Phase 1 modules; fixing those is a separate refactor, tracked in `docs/status.md`, and bundling it into the security change would have hidden the security diff.
- Pending: `.semgrep/` rules.
- `.codex/commands/pre-commit.md`: SAST audit step and verdict-table row; `.codex/commands/phase-status.md`: the two SAST gate rows and a `sast` entry in the expected pipeline stages
- CI-provider references corrected from `.gitlab-ci.yml` to `.github/workflows/ci.yml` (GitHub Actions is the only pipeline in the repo) in `CLAUDE.md`/`AGENTS.md`, `docs/status.md`, and `.codex/commands/phase-status.md`

## v0.2.0

- Test suite for `models.py`: 57 pytest cases covering `StandardModel`, `FloodAdjustedModel`, `RadiometricSystem`, `LongAgeRadiometricSuite`, `format_age`, and module constants
- Reference-value validation: one C-14 half-life recovers 5730 years; mass conservation (P + D) holds across all four epochs for every isotope system; zero-acceleration zero-initial-daughter configuration recovers the elapsed epoch time analytically
- 100% statement + branch coverage on `models.py`, enforced by `fail_under = 100` in `pyproject.toml`
- `pyproject.toml` added with pytest and coverage config; coverage source scoped to `models` (UI/CLI modules `app.py`, `fac14_main.py`, `visualization.py` excluded per CLAUDE.md §11)
- `.github/workflows/ci.yml` `test` job simplified to `pytest --cov --cov-report=term-missing --cov-report=xml:coverage.xml` (configuration driven by `pyproject.toml`)

## v0.1.0

Initial release of the Flood-Adjusted Radiometric Dating Simulator.

- Streamlit interactive app with 14 adjustable parameters and 6 visualization tabs
- C-14 dating simulation: pre-flood atmosphere, flood event, post-flood recovery
- Long-age radiometric dating: U-Pb (4.468 Gyr), K-Ar (1.248 Gyr), Rb-Sr (48.8 Gyr)
- Epoch-by-epoch decay tracking through Creation Week, pre-flood, Flood year, post-flood
- Headline metrics comparing true age (5,787 years) to apparent ages (billions of years)
- "The Math" tab with full LaTeX equations and worked examples
- CLI entry point (`fac14_main.py`) for batch simulations
- Docker containerization (python:3.13-slim, single service on port 8501)
- Launcher scripts for macOS and Windows with `[k]/[q]/[r]` shutdown menu