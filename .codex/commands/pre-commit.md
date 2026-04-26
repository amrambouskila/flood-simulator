---
name: pre-commit
description: Read-only audit before committing; report READY/NOT READY verdict
---

# Pre-Commit Audit

Before anything else:
1. Read `AGENTS.md` in full.
2. Read `docs/FLOOD_SIMULATOR_MASTER_PLAN.md`.
3. Run `git status` and `git diff` to identify all changes.

**This command must NEVER stage or commit anything.** It only reports. The user runs git commands.

## Audit Steps (run sequentially)

### 1. Lint Check
Run `ruff check .` mentally (or note if ruff config exists). Report any lint issues found by reading the changed files.

### 2. Code Review
Run the `/review` checklist against all changed files. Summarize findings by severity.

### 3. Mathematical Validation
For any changes to `models.py`, `simulation.py`, or computation code:
- Verify formulas against AGENTS.md Section 8
- Check that epoch evolution conserves mass (P_consumed = P_before - P_after, D_gained = P_consumed)
- Verify constant values against published reference data
- Check unit consistency across calculations

### 4. Documentation Check
Verify these files are updated as needed:
- `docs/status.md` — reflects current state after the changes?
- `docs/versions.md` — has an entry for the changes if they warrant a version bump?
- `AGENTS.md` — updated if domain models or architecture changed?

### 5. Interface Integrity
- Have any public method signatures in `models.py` changed? If so, is `app.py` updated to match?
- Have any constants changed value? If so, are all references consistent?
- Have slider ranges changed? If so, does AGENTS.md Section 7 match?

### 6. Test Status
- Do tests exist for modified code?
- Would the changes break existing tests?

## Verdict Table

```
| Audit Step              | Status      | Details |
|-------------------------|-------------|---------|
| Lint                    | PASS / FAIL | ...     |
| Code Review             | PASS / FAIL | ...     |
| Mathematical Validation | PASS / FAIL | ...     |
| Documentation           | PASS / FAIL | ...     |
| Interface Integrity     | PASS / FAIL | ...     |
| Test Status             | PASS / FAIL | ...     |

## VERDICT: READY TO COMMIT / NOT READY
```

If NOT READY, list the specific items that must be addressed before committing.