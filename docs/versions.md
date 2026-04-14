# Version History

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