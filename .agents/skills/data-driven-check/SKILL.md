---
name: data-driven-check
description: Proactively applied when writing any simulation or model code; flags hard-coded domain values that should come from constants or configuration
---

# Data-Driven Check Protocol

## When This Applies
- When editing `models.py`, `simulation.py`, `app.py`, or any new computation module
- When adding new physical constants, isotope data, or Torah timeline values
- When writing test assertions that reference physical values

## What to Check

### Hard-coded numbers that MUST be named constants
- Isotope half-lives (never write `4.468e9` inline -- use `ISOTOPE_SYSTEMS['U-Pb']['half_life']`)
- Decay constants (never compute `np.log(2) / 5730` inline -- use `LAMBDA`)
- Torah timeline dates (never write `1656` or `5787` inline -- use `FLOOD_YEAR`, `CURRENT_YEAR`)
- Default parameter values (must be class attributes or dict defaults, not inline literals)
- Slider min/max/step values in `app.py` (should reference constants or be documented in AGENTS.md)

### Acceptable inline numbers
- Mathematical constants: 0, 1, 2, `np.pi`, `np.e`
- Array dimensions and loop bounds
- Algorithm-specific coefficients (exponential decay formula structure)
- Display formatting (chart heights, font sizes, color hex values)
- Normalization values when the normalization is self-documenting (e.g., dividing by 1e9 to convert to Gyr)

### Where constants belong
| Type | Location |
|------|----------|
| Physical constants (half-lives, decay constants) | `models.py` module level or `ISOTOPE_SYSTEMS` dict |
| Torah timeline values | `models.py` module level (`FLOOD_YEAR`, `CURRENT_YEAR`, etc.) |
| Default model parameters | Class attributes on the relevant model class |
| Environment config (ports, URLs) | `.env` file, read via `os.environ` |

## Protocol
1. Before writing any numerical literal, ask: "Is this a domain value or a structural value?"
2. Domain values get named constants. Structural values (chart height, array size) can be inline.
3. If a constant exists anywhere in `models.py`, import it -- do not redefine.
4. If a new constant is needed, add it to `models.py` at module level with a comment explaining its source.
5. Flag any violation found in existing code as a SHOULD-FIX in the review.