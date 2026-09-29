# Transitioning to Sustainable Aviation Fuels: The Philippines

Estimates the **energy, land and investment** needed to replace the Philippines' current jet fuel demand with **e-kerosene**. The fuel is made from CO₂ captured directly from the air (DAC) and hydrogen from solar or wind power.

🌐 **Live demo:** https://billrizecondor.github.io/saf_projects_me3/ · 📄 [Paper (PDF)](<Energy Storage Paper - Condor.pdf>) · 📊 [Spreadsheet model](<SAF Calculations.xlsx>)

Course: Energy Storage, BME 2025.

## Key results

| | Solar route | Wind route |
|---|---:|---:|
| Continuous power for fuel production | 1,665 MW | 1,665 MW |
| Installed capacity needed | 8,323 MW | 5,548 MW |
| Share of the 2040 renewables goal (20 GW) | 42% | 28% |
| Land footprint | 9,566 ha | 188,645 ha |
| Panels / turbines | 18–23 million panels | 1,850–2,775 turbines |
| CAPEX, 2030 technology prices | €4.8B | €7.9B |
| CAPEX, 2050 technology prices | €3.4B | €6.0B |

- The fuel to replace is 33,700 barrels of jet fuel a day (165,130 L/h).
- Solar needs only about **5% of wind's land**, because turbines need wide spacing.
- **Falling DAC and renewable costs** are critical: plant CAPEX drives the final fuel price.

## Live demo

The [interactive demo](https://billrizecondor.github.io/saf_projects_me3/) includes:
- a calculator where you change fuel demand, energy per litre, capacity factors and cost year, and every result updates
- charts comparing the capacity needed with national renewables targets, and investment by route
- a to-scale land footprint comparison with Metro Manila
- the Python model, loaded directly from this repo

## Code

`analysis/saf_model.py` is a line-by-line Python version of `SAF Calculations.xlsx`. It checks its results against the spreadsheet's calculated values and writes the defaults used by the demo.

```bash
pip install openpyxl
python analysis/saf_model.py
```

## Main sources

Seymour et al. (2024) · Sens et al. (2022) · Bolinger et al. (2022) · Grim et al. (2022) · Rojas-Michaga et al. (2023) · NREL
