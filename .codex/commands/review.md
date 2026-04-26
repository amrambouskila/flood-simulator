---
name: review
description: Review changed code against project standards; produce checklist report without fixing anything
---

# Code Review

Before anything else:
1. Read `AGENTS.md` in full.
2. Read `docs/FLOOD_SIMULATOR_MASTER_PLAN.md` for architecture decisions.
3. Run `git diff` to see all changed files.

## Review Protocol

For every changed file, read it in full and evaluate against this checklist. Report findings as a table with file:line references and severity (CRITICAL / SHOULD-FIX / MINOR).

### Checklist

1. **Type annotations** — Every function/method has full type annotations? No `Any` without justification?
2. **`from __future__ import annotations`** — Present at top of every modified Python module?
3. **No dead code** — No commented-out blocks, unused imports, unused variables, unused functions?
4. **No magic numbers** — Every numerical constant named and documented? Domain constants imported from `models.py`?
5. **Domain variable names** — Using standard names (P, D, lam, R, A, dt) per AGENTS.md Section 3?
6. **Mathematical correctness** — Formulas match standard radiometric dating equations in AGENTS.md Section 8?
7. **Unit documentation** — Units documented on every physical quantity (in variable name, docstring, or comment)?
8. **File organization** — One concept per file? No god files expanded?
9. **Data contracts** — No changes to model interfaces without documented approval?
10. **Error handling** — Specific exception types? No bare `except:`? No swallowed exceptions?
11. **Naming** — snake_case functions/variables, PascalCase classes, UPPER_SNAKE_CASE constants?
12. **No TODO without task** — Any TODO/FIXME comments have linked tasks?
13. **Test coverage** — If logic was added, does a corresponding test exist?
14. **Epoch conservation** — If `_evolve()` or epoch code was modified, does parent + daughter still sum correctly?

### Output Format

```
## Review: <filename>

| # | Check | Status | Notes |
|---|-------|--------|-------|
| 1 | Type annotations | PASS/FAIL | file:line details |
...

### Verdict: PASS / NEEDS WORK
```

**Do NOT fix anything automatically.** Report only. The user decides what to act on.