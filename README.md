# Gun Violence Country-Level Analysis

Analyzes correlations between gun homicide rates and socioeconomic/policy indicators across countries worldwide. Produces interactive choropleth maps, scatter plots with trend lines, and statistical summaries.

## Analyses

| Notebook | Description |
|----------|-------------|
| 01 — Data Collection | Fetches and merges all datasets into a single CSV |
| 02 — Gun Homicide Map | Choropleth map of gun homicide rates + top/bottom 20 bar charts |
| 03 — Gini Correlation | Gun homicide rate vs income inequality (Gini coefficient) |
| 04 — Drug Correlation | Gun homicide rate vs drug offense rate |
| 05 — Population Correlation | Gun homicide rate vs population |
| 06 — Gun Ownership Correlation | Gun homicide rate vs civilian gun ownership rate |
| 07 — Gun Control Correlation | Gun homicide rate vs gun control strictness |

## Data Sources

| Dataset | Source | Coverage | Notes |
|---------|--------|----------|-------|
| Gun homicide rate (per 100K) | [UNODC Global Study on Homicide](https://dataunodc.un.org/) | ~161 countries | Most recent available, ~2020-2022; year varies by country |
| Population | [World Bank API](https://data.worldbank.org/indicator/SP.POP.TOTL) (`SP.POP.TOTL`) | ~169 countries | 2022 estimates |
| Gini coefficient | [World Bank API](https://data.worldbank.org/indicator/SI.POV.GINI) (`SI.POV.GINI`) | ~152 countries | Latest available 2018-2022; coverage is patchy |
| Drug offense rate (per 100K) | [UNODC crime statistics](https://dataunodc.un.org/) | ~121 countries | ~2020; reporting standards vary significantly by country |
| Gun ownership (firearms per 100 persons) | [Small Arms Survey 2017](https://www.smallarmssurvey.org/database/global-firearms-holdings) | ~155 countries | 2017 estimates (latest comprehensive global dataset) |
| Gun control strictness (1-5 scale) | Custom ordinal scale | ~155 countries | See caveat below |

## Caveats

- **Gun homicide data** from UNODC — the reporting year varies by country (~2020-2022). Some countries have limited forensic capacity, so figures may undercount.
- **Gini coefficient** coverage is patchy (~100-150 countries depending on year). Many developing nations lack recent household survey data.
- **Small Arms Survey** data is from **2017**, the latest comprehensive global estimate of civilian firearm holdings. Actual numbers may have shifted since then.
- **Gun control strictness** is a **custom ordinal scale** (1=Very Permissive to 5=Very Strict), NOT from an established index. It is inherently subjective and simplified — real-world gun regulation involves dozens of dimensions (licensing, background checks, carry laws, assault weapon restrictions, etc.) that cannot be fully captured in a single number.
- **Drug offense data** reflects *reported/detected* offenses, not actual drug activity. Countries with aggressive enforcement (e.g., Nordics, Australia) report high rates; countries with less enforcement capacity report low rates.
- **Correlation does not imply causation.** These analyses show statistical associations only. Confounding variables (poverty, conflict, institutional capacity, culture) are not controlled for.

## How to Run

Requires Python 3.9+ with a virtualenv at `.venv/`.

```bash
# Install dependencies
.venv/bin/pip install pandas numpy matplotlib plotly scipy papermill

# Run all notebooks in order
for nb in 01_data_collection 02_gun_homicide_map 03_gini_correlation \
          04_drug_correlation 05_population_correlation \
          06_gun_ownership_correlation 07_gun_control_correlation; do
    .venv/bin/python -m papermill "notebooks/${nb}.ipynb" /dev/null --cwd notebooks
done

# Generate combined HTML report
.venv/bin/python scripts/generate_html.py
```

The report is written to `docs/report.html`.
