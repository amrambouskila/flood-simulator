---
name: scaffold
description: Guide scaffolding of new modules or project infrastructure
---

# Scaffold New Module

Before anything else:
1. Read `AGENTS.md` in full.
2. Read `docs/FLOOD_SIMULATOR_MASTER_PLAN.md` for architecture and phase constraints.
3. Confirm the task scope: what module or component is being scaffolded?

## Steps

1. **Check phase constraints.** Verify the requested module belongs in the current phase (Phase 1: Streamlit app). Do NOT scaffold FastAPI routes, React components, or database models — those are Phase 2+.

2. **Search before creating.** Grep the codebase for existing modules, classes, or utilities that might already cover the requested functionality. Report findings.

3. **Create directory structure.** Follow the project skeleton in AGENTS.md Section 9. Every new Python module gets:
   - The module file with `from __future__ import annotations` at the top
   - Type annotations on all function signatures
   - Docstring with one-line description
   - A corresponding test file in `tests/`

4. **Signatures only.** During scaffolding, write function/method signatures with type annotations and docstrings, but do NOT implement logic. Use `raise NotImplementedError` as the body. This ensures the interface is reviewed before implementation begins.

5. **Constants.** Any new physical constants or domain parameters go in `models.py` at module level, NOT in the new module. Import them.

6. **Report.** List all files created with one-line descriptions. Do NOT commit.