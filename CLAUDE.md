# Project: Gun Violence Country-Level Analysis

## Overview
Analyzes correlations between gun homicide rates and socioeconomic indicators (Gini coefficient, drug offenses, population) across countries worldwide. Produces choropleth maps and scatter plots with trend lines.

## Architecture
- `src/data_utils.py` — Data fetching utilities: World Bank API (population, Gini), UNODC data (gun homicides, drug offenses), embedded fallbacks
- `notebooks/` — Jupyter notebooks (01-05) that produce analysis outputs
- `scripts/generate_html.py` — Generates a combined HTML report from notebook outputs

## Notebook Pipeline
Notebooks must run in order (later ones depend on CSVs from earlier ones):
1. `01_data_collection` — Fetch & merge all datasets → `data/processed/merged_country_data.csv`
2. `02_gun_homicide_map` — Choropleth map of gun homicide rates + top/bottom 20 bar charts
3. `03_gini_correlation` — Scatter: gun homicide vs Gini coefficient (with regression)
4. `04_drug_correlation` — Scatter: gun homicide vs drug offense rate (with regression)
5. `05_population_correlation` — Scatter: gun homicide vs population (with regression)

## Data Sources
- **World Bank API** — Free, no key needed. Population (`SP.POP.TOTL`), Gini (`SI.POV.GINI`)
- **UNODC** — Gun homicide rates, drug offense rates (embedded fallback data)
- All datasets joined on ISO alpha-3 country codes

## Running Notebooks
```bash
.venv/bin/python -m papermill notebooks/01_data_collection.ipynb /dev/null --cwd notebooks
```

## Generating the HTML Report
After running notebooks, regenerate `docs/report.html`:
```bash
.venv/bin/python scripts/generate_html.py
```

## Environment
- Python 3.9 virtualenv at `.venv/`
- No API keys required
- Key dependencies: pandas, numpy, matplotlib, plotly, scipy, papermill
