---
name: phase-awareness
description: Proactively applied at session start and before any implementation work; orients Codex to the current phase and its explicit scope constraints
---

# Phase Awareness Protocol

## When This Applies
- At the start of every session
- Before implementing any new feature or modification
- When a request might cross phase boundaries

## Current Phase: Phase 1 -- Streamlit Interactive App (COMPLETE)

### In Scope
- Bug fixes to existing Streamlit app
- Test suite creation for existing code
- Infrastructure improvements (linting, CI/CD, documentation)
- Performance improvements to existing calculations
- New visualization tabs or chart improvements within Streamlit
- Parameter range adjustments

### Out of Scope (Phase 2+)
- FastAPI backend endpoints
- React or TypeScript frontend code
- PostgreSQL database schemas or migrations
- WebSocket streaming
- Pydantic request/response models (beyond what models.py already has)
- User authentication or multi-tenancy
- Additional isotope systems beyond U-Pb, K-Ar, Rb-Sr

### Out of Scope (Phase 3+)
- Geological column modeling
- Isochron diagram generation
- Concordia diagrams
- Publication-ready SVG/PDF export
- Batch parameter sweep automation

## Protocol
1. Before implementing, check: does this belong in Phase 1?
2. If the request crosses phase boundaries, stop and flag it to the user.
3. If the request is ambiguous, ask: "This sounds like it might be Phase 2 scope. Confirm?"
4. Forward-compatibility is fine -- writing Phase 1 code that won't break Phase 2 is good. But don't implement Phase 2 features "just to get ahead."