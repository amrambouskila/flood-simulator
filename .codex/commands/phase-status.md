---
name: phase-status
description: Assess progress against phase roadmap; produce status table and next-action list
---

# Phase Status Assessment

Before anything else:
1. Read `AGENTS.md` in full.
2. Read `docs/FLOOD_SIMULATOR_MASTER_PLAN.md` — especially the Phase Breakdown (Section 3).
3. Read `docs/status.md` for current state.
4. Read `docs/versions.md` for recent version history.

## Assessment Protocol

### Phase 1 Gate Criteria

Evaluate each gate criterion from the master plan:

| Gate Criterion | Status | Evidence |
|---------------|--------|----------|
| All 6 tabs render correctly with default parameters | ? | Check app.py tab definitions |
| U-Pb apparent age reaches ~4.5 Gyr with defaults | ? | Run/verify RadiometricSystem calculation |
| C-14 flood-era sample dates to ~30,000+ years | ? | Run/verify FloodAdjustedModel calculation |
| Docker container builds and runs cleanly | ? | Check Dockerfile + docker-compose.yml |
| Both launcher scripts functional | ? | Check fac14_service.sh and .bat exist and are complete |

### Infrastructure Status

| Item | Status | Notes |
|------|--------|-------|
| AGENTS.md | ? | Exists and complete? |
| Master plan | ? | Exists at docs/FLOOD_SIMULATOR_MASTER_PLAN.md? |
| docs/status.md | ? | Current and accurate? |
| docs/versions.md | ? | Has at least v0.1.0? |
| .gitignore | ? | Exists with standard ignores? |
| .gitlab-ci.yml | ? | Exists with lint/test/build/docker-build stages? |
| .codex/settings.json | ? | Full hooks (SessionStart, PreToolUse, PostToolUse, PreCompact, Stop)? |
| .codex/commands/ | ? | All 5 commands present? |
| .agents/skills/ | ? | All 3 skills present? |
| Test suite | ? | Exists in tests/? Coverage level? |
| pyproject.toml | ? | ruff + pytest config? |

### Code Quality

| Item | Status | Notes |
|------|--------|-------|
| Type annotations on all functions | ? | Check models.py, app.py |
| `from __future__ import annotations` | ? | Present in all .py files? |
| No dead code | ? | Grep for commented-out blocks, unused imports |
| No magic numbers | ? | All constants named? |
| ruff clean | ? | Would `ruff check .` pass? |

### Next Actions

Based on the assessment, list the top 5 highest-priority actions needed, ordered by impact.

## Output Format

Report the tables above filled in, plus a summary:

```
## Phase 1 Status: COMPLETE / IN PROGRESS / BLOCKED
## Infrastructure: X/Y items complete
## Code Quality: X/Y items passing
## Top Priority: <single most important next action>
```