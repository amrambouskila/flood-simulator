---
name: validation-protocol
description: Proactively applied when writing or modifying tests; enforces real assertions, reference published values, and no-mocking rules
---

# Validation Protocol

## When This Applies
- When creating or modifying any test file in `tests/`
- When adding assertions to existing tests
- When reviewing test coverage

## Rules

### Use `assert_allclose`, never `==` for floats
```python
# WRONG
assert model.calculate_age(0.5) == 5730

# RIGHT
np.testing.assert_allclose(model.calculate_age(0.5), 5730.0, rtol=1e-10)
```

Every numerical assertion must use `np.testing.assert_allclose` with explicit `atol` or `rtol` parameters. Document why the chosen tolerance is appropriate.

### Reference published values
At least one test per model must validate against a known analytical solution or published value:

- **StandardModel:** `calculate_age(0.5) == 5730` (definition of half-life)
- **StandardModel:** `predict_ratio(5730) == 0.5` (inverse of above)
- **RadiometricSystem:** zero initial daughter + zero acceleration -> `apparent_age == CURRENT_YEAR` (normal decay)
- **RadiometricSystem:** epoch evolution conserves mass at every step
- **U-Pb with default params:** apparent age in the range 4-5 billion years (matching Earth's accepted radiometric age)
- **C-14 half-life:** 5,730 years (standard accepted value, Godwin 1962)

### No mocking of physics
Never mock:
- `np.exp`, `np.log`, or any mathematical function
- Decay constant calculations
- Epoch evolution logic
- Any method on StandardModel, FloodAdjustedModel, or RadiometricSystem

Mocking is only acceptable for:
- File I/O in export tests
- Streamlit widgets in UI tests (if ever written)
- External API calls (none exist currently)

### Parametrize across isotope systems
Tests that apply to all isotope systems must use `@pytest.mark.parametrize`:
```python
@pytest.mark.parametrize("system_key", ["U-Pb", "K-Ar", "Rb-Sr"])
def test_mass_conservation(system_key):
    ...
```

### Test structure
- One test file per source module: `tests/test_models.py`, `tests/test_simulation.py`
- Test functions named `test_<what_is_being_tested>`
- Group related tests in classes: `class TestStandardModel:`, `class TestFloodAdjustedModel:`
- Document the physical meaning of each assertion in a brief comment

### Coverage
- Target: 100% on `models.py` core computation methods
- Use `pytest --cov=. --cov-report=term-missing` to identify gaps
- `pragma: no cover` only on genuinely untestable code (e.g., `if __name__ == "__main__":`) with a comment explaining why