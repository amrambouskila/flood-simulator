# Version History

## v0.2.1

### CI fix: `docker-build` unblocked (2026-08-27)

- **`aquasecurity/trivy-action@0.28.0` never existed.** Since the security wiring landed, `docker-build` failed at *Set up job* on every run -- `Unable to resolve action 'aquasecurity/trivy-action@0.28.0', unable to find version '0.28.0'` -- so the image was never built and the Trivy gate never ran. That repository publishes only `v`-prefixed tags (`v0.36.0` ... `v0.28.0`); the one unprefixed tag in its entire history is a stray `0.35.0`. Now pinned to `aquasecurity/trivy-action@v0.36.0` (latest release), which still accepts every input the job passes: `image-ref`, `severity`, `exit-code`, `ignore-unfixed`. Note for anyone tightening this to a SHA later: `refs/tags/v0.36.0` resolves to the *annotated tag object* `a9c7b0f0`, not a commit -- a SHA pin must use the commit `ed142fd0`, or it fails to resolve exactly the way `@0.28.0` did.
- **The gate was verified locally before the change shipped**, not assumed, and it passes *only* because of `.trivyignore` -- which was proven by A/B, not inferred. Same fresh `docker build --no-cache --pull` image, same Trivy `v0.70.0` (the version `v0.36.0` installs by default), same job flags (`--severity HIGH,CRITICAL --exit-code 1 --ignore-unfixed`) and Trivy's default scanner set (`vuln,secret`); the only variable is the working directory:
  - cwd = repo root, `.trivyignore` present -> `Python: 0`, **exit 0**
  - cwd = empty dir, no `.trivyignore` -> `Python: 2`, **exit 1** -- HIGH `msgpack` 1.1.2 (`GHSA-6v7p-g79w-8964`) and `setuptools` 70.3.0 (`CVE-2025-47273`), both declared in pip's vendored CycloneDX SBOM `pip/_vendor/bom.cdx.json`, which is why neither shows up in `pip list`.
  CI gets the first case: `actions/checkout` puts `.trivyignore` at `$GITHUB_WORKSPACE`, a composite action's `run:` steps default to that directory, and the action's `entrypoint.sh` sets `TRIVY_IGNOREFILE` only when the `trivyignores` input is supplied -- which this job does not -- so Trivy falls back to `.trivyignore` in the cwd. That discovery is implicit; passing `trivyignores: .trivyignore` explicitly would make it impossible to break silently.
- **Nothing else in the pipeline needed changing.** Every other action reference resolves, `actionlint` is clean on both workflows, and this job's `cache-from`/`cache-to: type=gha` block is byte-identical to the last fully green run (`28038478577`), so the GHA cache backend is already proven here. `lint`, `sast`, `test` and `build` were already green; `docker-build` was the only red job.
- Trivy `v0.70.0` pulls its DB from `mirror.gcr.io/aquasec/trivy-db:2`, so the well-known `ghcr.io` `TOOMANYREQUESTS` rate-limit flake does not apply to this pin.
- Pin corrected in the `<security>` section (11a) of `CLAUDE.md` and `AGENTS.md`.

### CI hardening + dependency remediation (2026-08-24)

- **Semgrep invocation corrected.** The job used `semgrep ci` with `--severity` and `--error`, which that subcommand does not accept — it exits 2 with a usage error before scanning. Switched to `semgrep scan`, which supports both.
- **Release workflow hardened against script injection.** `${{ inputs.bump }}` and `${{ steps.bump.outputs.new_version }}` were interpolated directly into `run:` blocks, where the value becomes shell code. Both now pass through `env:` and are read as quoted shell variables. The input is `type: choice`, so this was not exploitable today — it is the pattern that breaks the moment the input type changes.
- **Base-image security patches in the Dockerfile.** The Debian slim bases ship a `util-linux` that Trivy flags HIGH (CVE-2026-53612..53615, fixed upstream in 2.41.5). Measured directly: `python:3.13-slim` carries 38 fixable HIGH/CRITICAL, `3.12-slim` 36, `3.11-slim` 38, while `nginx:alpine` is clean. These come from the base layer, so an `apt-get upgrade` step is required even where nothing else installs them.
- **`.trivyignore` added** for two findings with no in-image remediation: `CVE-2025-47273` (setuptools 70.3.0) and `GHSA-6v7p-g79w-8964` (msgpack 1.1.2). Both come from pip's vendored manifest in the base image, not from project dependencies — and setuptools 70.3.0 is not even installed (`find` finds nothing; the image ships 84.x). Upgrading pip does not rewrite that manifest. Each entry carries its justification inline.
- **Dockerfile `missing-user` suppressed with written justification**, per global CLAUDE.md section 9 (non-root is not required for personal local-dev containers). The nginx images additionally cannot run as non-root without the unprivileged image and a port change. Revisit before any deployment beyond localhost.


- Container Streamlit port set symmetric to the published host port: the Docker image now serves on `5250` internally (`Dockerfile` `--server.port`/`EXPOSE`/`ENV PORT`) and `docker-compose.yml` maps `${PORT:-5250}:5250`. Host port and all behavior unchanged; eliminates the shared internal `8501` so concurrent multi-app runs never collide on the container port. Workspace `PORT_ASSIGNMENTS.md` updated.

### Security documentation

- `<security>` section (11a) added to `CLAUDE.md`/`AGENTS.md`: `sast` CI stage requirement (Semgrep + CodeQL + `pip-audit` + `gitleaks`; Trivy in `docker-build`; ruff `S` rules in `lint`), input-boundary inventory for every Phase 1 boundary (Streamlit widgets, Streamlit server, CLI args, `input()` prompts, file exports, `PORT`), injection-class defenses per boundary, Phase 2 planned boundaries, and a **Security check** item in the completion checklist
- Master plan: Security section with the pipeline diagram (`lint -> sast -> test -> ...`) and the two SAST gate lines added to every phase gate list
- `docs/status.md`: Security state and next security tasks (rewritten into Wired / Pending once the wiring landed)

### Security wiring

- `.github/workflows/ci.yml`: new `sast` job (`needs: lint`, `permissions: security-events: write`) running CodeQL `python`, `pipx run semgrep scan --config auto --config p/owasp-top-ten --config p/python --config p/docker --severity ERROR --error` with SARIF upload plus a fail-on-findings step, `gitleaks/gitleaks-action@v2`, and `pipx run pip-audit -r requirements.txt`. `test` now carries `needs: sast`. `docker-build` builds with `load: true` as `flood-simulator:ci` and runs `aquasecurity/trivy-action@v0.36.0` (`HIGH,CRITICAL`, `exit-code: 1`, `ignore-unfixed: true`).
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