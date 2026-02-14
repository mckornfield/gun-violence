# Project: Gun Violence Analysis (Country-Level & US County-Level)

## Overview
Analyzes correlations between gun homicide rates and socioeconomic indicators across countries worldwide and across ~100 of the largest US counties. Produces choropleth maps and scatter plots with trend lines.

## Architecture
- `src/data_utils.py` — Country-level data: World Bank API (population, Gini), UNODC data (gun homicides, drug offenses), embedded fallbacks
- `src/us_county_data.py` — US county-level embedded data (~100 counties) and getter functions. Joined on 5-digit FIPS codes.
- `notebooks/` — Jupyter notebooks (01-16) that produce analysis outputs
- `scripts/generate_html.py` — Generates a combined HTML report from notebook outputs

## Notebook Pipeline
Notebooks must run in order (later ones depend on CSVs from earlier ones):

### Country-Level (01-07)
1. `01_data_collection` — Fetch & merge all datasets → `data/processed/merged_country_data.csv`
2. `02_gun_homicide_map` — Choropleth map of gun homicide rates + top/bottom 20 bar charts
3. `03_gini_correlation` — Scatter: gun homicide vs Gini coefficient (with regression)
4. `04_drug_correlation` — Scatter: gun homicide vs drug offense rate (with regression)
5. `05_population_correlation` — Scatter: gun homicide vs population (with regression)
6. `06_gun_ownership_correlation` — Scatter + choropleth: gun homicide vs civilian gun ownership (with regression)
7. `07_gun_control_correlation` — Scatter + strip/box plot + choropleth: gun homicide vs gun control strictness (with regression)

### US County-Level (08-16)
8. `08_us_data_collection` — Merge all US county datasets → `data/processed/merged_us_county_data.csv`
9. `09_us_gun_homicide_map` — County choropleth + top/bottom 20 bar charts
10. `10_us_gini_correlation` — Scatter + choropleth: gun homicide vs Gini coefficient
11. `11_us_drug_correlation` — Scatter + choropleth: gun homicide vs drug offense rate
12. `12_us_population_correlation` — Scatter: gun homicide vs population (log-log)
13. `13_us_poverty_correlation` — Scatter + choropleth: gun homicide vs poverty rate
14. `14_us_income_correlation` — Scatter + choropleth: gun homicide vs median household income
15. `15_us_gun_ownership_correlation` — Scatter + choropleth: gun homicide vs gun ownership % (state proxy)
16. `16_us_gun_control_correlation` — Scatter + strip/box + choropleth: gun homicide vs Giffords grade (state proxy)

## Data Sources
- **World Bank API** — Free, no key needed. Population (`SP.POP.TOTL`), Gini (`SI.POV.GINI`)
- **UNODC** — Gun homicide rates, drug offense rates (embedded fallback data)
- **Small Arms Survey 2017** — Civilian firearm ownership per 100 persons (embedded)
- **Gun control strictness** — Custom ordinal scale 1-5 (embedded, see README for details)
- **Census ACS 2022** — US county population, Gini, poverty rate, median income
- **CDC WONDER** — US county gun homicide rates (~2020-2022)
- **FBI UCR** — US county drug offense rates (~2020)
- **RAND Corporation** — State-level gun ownership estimates (proxy for counties)
- **Giffords Law Center** — State gun law grades (2023, proxy for counties)
- Country datasets joined on ISO alpha-3 country codes
- US county datasets joined on 5-digit FIPS codes (zero-padded strings)

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
