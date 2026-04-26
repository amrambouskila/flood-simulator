---
name: validate
description: Validate simulation code for mathematical correctness and physical consistency
---

# Simulation Validation

Before anything else:
1. Read `AGENTS.md` in full — especially Section 8 (Required Calculations).
2. Read `docs/FLOOD_SIMULATOR_MASTER_PLAN.md` — especially Section 6 (Key Reference Values).
3. Read `models.py` in full.

## Validation Layers

### Layer 1: Structural Completeness
- All classes have complete type annotations
- All public methods have docstrings
- Constants are defined at module level, not inside methods
- No circular imports
- `from __future__ import annotations` present

### Layer 2: Numerical Correctness

#### C-14 Standard Model
- `StandardModel.calculate_age(0.5)` must equal `CARBON_14_HALF_LIFE` (5730 years)
- `StandardModel.predict_ratio(5730)` must equal 0.5
- `StandardModel.predict_ratio(0)` must equal 1.0
- `StandardModel.calculate_age(1.0)` must equal 0.0
- `calculate_age(predict_ratio(t)) == t` for any t (round-trip consistency)

#### C-14 Flood-Adjusted Model
- With all defaults, `standard_date_for_true_age(YEARS_SINCE_FLOOD)` should produce a significantly overestimated age (30,000+ years)
- `effective_initial_c14(0)` should return approximately the post-flood equilibrium value (near 1.0 for recent samples)
- `effective_initial_c14(CURRENT_YEAR)` should return the pre-flood value modified by cosmic ray shielding
- `predict_measured_ratio(true_age)` must always be positive and less than `effective_initial_c14(true_age)`

#### Long-Age Radiometric Systems
- With zero initial daughter and zero acceleration: `apparent_age` must equal `CURRENT_YEAR` (normal decay for 5,787 years)
- Epoch evolution must conserve mass: `P_consumed = P_before - P_after` and `D_gained = P_consumed` at every step
- With default settings (creation accel 10^11, initial D/P as per defaults): U-Pb apparent age should be ~4.5 billion years
- `daughter_parent_ratio()` must be non-negative
- `apparent_age()` must be non-negative

### Layer 3: Data-Driven Compliance
- All isotope half-lives match published values:
  - C-14: 5,730 years
  - U-238: 4.468 x 10^9 years
  - K-40: 1.248 x 10^9 years
  - Rb-87: 48.8 x 10^9 years
- Torah timeline constants:
  - Flood year: 1656 from Creation
  - Current year: 5787
  - Creation Week: 6 days
- Decay constants are derived correctly: `lambda = ln(2) / half_life`

### Layer 4: Performance
- `generate_comparison_data(steps=300)` should complete in under 1 second
- `LongAgeRadiometricSuite.apparent_ages()` should complete in under 100ms

### Layer 5: Reference Validation
Cross-check against known published radiometric dating results:
- Earth's accepted U-Pb age: ~4.54 billion years. With default parameters, simulator should produce a value in this range.
- Oldest known C-14 dates: ~50,000-60,000 years. Simulator should produce ages in this range for the oldest pre-flood samples.

## Output Format

```
| Validation Layer           | Status | Details |
|----------------------------|--------|---------|
| Structural Completeness    | PASS/FAIL | ... |
| Numerical Correctness      | PASS/FAIL | ... |
| Data-Driven Compliance     | PASS/FAIL | ... |
| Performance                | PASS/FAIL | ... |
| Reference Validation       | PASS/FAIL | ... |

## VERDICT: VALID / ISSUES FOUND
```

List every issue with file:line references. Do not auto-fix — report and let the user decide.