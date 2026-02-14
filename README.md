# Gun Violence Analysis — Country-Level & US County-Level

Analyzes correlations between gun homicide rates and socioeconomic/policy indicators across countries worldwide and across ~100 of the largest US counties. Produces interactive choropleth maps, scatter plots with trend lines, and statistical summaries.

## Analyses

### Country-Level (Notebooks 01-07)

| Notebook | Description |
|----------|-------------|
| 01 — Data Collection | Fetches and merges all datasets into a single CSV |
| 02 — Gun Homicide Map | Choropleth map of gun homicide rates + top/bottom 20 bar charts |
| 03 — Gini Correlation | Gun homicide rate vs income inequality (Gini coefficient) |
| 04 — Drug Correlation | Gun homicide rate vs drug offense rate |
| 05 — Population Correlation | Gun homicide rate vs population |
| 06 — Gun Ownership Correlation | Gun homicide rate vs civilian gun ownership rate |
| 07 — Gun Control Correlation | Gun homicide rate vs gun control strictness |

### US County-Level (Notebooks 08-16)

| Notebook | Description |
|----------|-------------|
| 08 — US Data Collection | Merges all US county datasets into a single CSV (~100 counties) |
| 09 — US Gun Homicide Map | County choropleth + top/bottom 20 bar charts |
| 10 — US Gini Correlation | Gun homicide rate vs Gini coefficient |
| 11 — US Drug Correlation | Gun homicide rate vs drug offense rate |
| 12 — US Population Correlation | Gun homicide rate vs population (log-log) |
| 13 — US Poverty Correlation | Gun homicide rate vs poverty rate |
| 14 — US Income Correlation | Gun homicide rate vs median household income |
| 15 — US Gun Ownership Correlation | Gun homicide rate vs gun ownership % (state proxy) |
| 16 — US Gun Control Correlation | Gun homicide rate vs Giffords gun law grade (state proxy) |

### US County Mass Shooting Analysis (Notebooks 17-25)

| Notebook | Description |
|----------|-------------|
| 17 — US Mass Shooting Data | Loads GVA data, computes per-capita rate, merges with county indicators |
| 18 — US Mass Shooting Map | County choropleth + top/bottom 20 bar charts |
| 19 — Mass Shooting vs Gini | Mass shooting rate vs Gini coefficient |
| 20 — Mass Shooting vs Drugs | Mass shooting rate vs drug offense rate |
| 21 — Mass Shooting vs Population | Mass shooting rate vs population (log-log) |
| 22 — Mass Shooting vs Poverty | Mass shooting rate vs poverty rate |
| 23 — Mass Shooting vs Income | Mass shooting rate vs median household income |
| 24 — Mass Shooting vs Gun Ownership | Mass shooting rate vs gun ownership % (state proxy) |
| 25 — Mass Shooting vs Gun Control | Mass shooting rate vs Giffords gun law grade (state proxy) |

### Mental Illness Correlation (Notebooks 26-27)

| Notebook | Description |
|----------|-------------|
| 26 — Gun Homicide vs Mental Illness | Gun homicide rate vs mental illness prevalence (state proxy) |
| 27 — Mass Shooting vs Mental Illness | Mass shooting rate vs mental illness prevalence (state proxy) |

## Data Sources

### Country-Level

| Dataset | Source | Coverage | Notes |
|---------|--------|----------|-------|
| Gun homicide rate (per 100K) | [UNODC Global Study on Homicide](https://dataunodc.un.org/) | ~161 countries | Most recent available, ~2020-2022; year varies by country |
| Population | [World Bank API](https://data.worldbank.org/indicator/SP.POP.TOTL) (`SP.POP.TOTL`) | ~169 countries | 2022 estimates |
| Gini coefficient | [World Bank API](https://data.worldbank.org/indicator/SI.POV.GINI) (`SI.POV.GINI`) | ~152 countries | Latest available 2018-2022; coverage is patchy |
| Drug offense rate (per 100K) | [UNODC crime statistics](https://dataunodc.un.org/) | ~121 countries | ~2020; reporting standards vary significantly by country |
| Gun ownership (firearms per 100 persons) | [Small Arms Survey 2017](https://www.smallarmssurvey.org/database/global-firearms-holdings) | ~155 countries | 2017 estimates (latest comprehensive global dataset) |
| Gun control strictness (1-5 scale) | Custom ordinal scale informed by [GunPolicy.org](https://www.gunpolicy.org/) and [Library of Congress reports](https://www.loc.gov/collections/legal-reports/) | ~155 countries | See caveat below |

### US County-Level

| Dataset | Source | Coverage | Notes |
|---------|--------|----------|-------|
| Gun homicide rate (per 100K) | [CDC WONDER](https://wonder.cdc.gov/) | ~100 counties | ~2020-2022 average |
| Population | [Census ACS 2022](https://data.census.gov/) | ~100 counties | 2022 estimates |
| Gini coefficient | [Census ACS 2022](https://data.census.gov/) | ~100 counties | County-level income inequality |
| Drug offense rate (per 100K) | [FBI UCR](https://crime-data-explorer.fr.cloud.gov/) | ~100 counties | ~2020; reporting varies by agency |
| Poverty rate (%) | [Census ACS 2022](https://data.census.gov/) | ~100 counties | Percent below poverty line |
| Median household income | [Census ACS 2022](https://data.census.gov/) | ~100 counties | 2022 dollars |
| Gun ownership (% households) | [RAND Corporation](https://www.rand.org/pubs/tools/TLA243-2-v2.html) | State-level proxy | Applied to all counties in each state |
| Gun law grade | [Giffords Law Center](https://giffords.org/lawcenter/resources/scorecard/) | State-level proxy | 2023 scorecard; A+=12 to F=0 numeric scale |
| Mass shooting incidents | [Gun Violence Archive](https://www.gunviolencearchive.org/) | ~100 counties | 2019-2023; definition: 4+ people shot (not including shooter) |
| Mental illness prevalence (AMI %) | [SAMHSA NSDUH](https://www.samhsa.gov/data/nsduh) | State-level proxy | 2021-2022; "Any Mental Illness" among adults 18+ |

## Caveats

- **Gun homicide data** from UNODC — the reporting year varies by country (~2020-2022). Some countries have limited forensic capacity, so figures may undercount.
- **Gini coefficient** coverage is patchy (~100-150 countries depending on year). Many developing nations lack recent household survey data.
- **Small Arms Survey** data is from **2017**, the latest comprehensive global estimate of civilian firearm holdings. Actual numbers may have shifted since then.
- **Gun control strictness** is a **custom ordinal scale** (1=Very Permissive to 5=Very Strict), NOT from an established index. Ratings are informed by country profiles on [GunPolicy.org](https://www.gunpolicy.org/) (Sydney School of Public Health) and [Library of Congress firearms legislation reports](https://www.loc.gov/collections/legal-reports/), considering: whether civilian ownership is a right vs privilege vs prohibited, licensing/permit requirements, background checks, category restrictions (handguns, semi-auto, full-auto), carry laws, and registration requirements. It is inherently subjective and simplified — real-world gun regulation involves dozens of dimensions that cannot be fully captured in a single number.
- **Drug offense data** reflects *reported/detected* offenses, not actual drug activity. Countries with aggressive enforcement (e.g., Nordics, Australia) report high rates; countries with less enforcement capacity report low rates.
- **Correlation does not imply causation.** These analyses show statistical associations only. Confounding variables (poverty, conflict, institutional capacity, culture) are not controlled for.

### US County-Level Caveats

- **State-level proxies:** Gun ownership (RAND) and gun law grades (Giffords) are state-level data applied to all counties in each state. Multiple counties share the same x-value, creating visible clustering in scatter plots.
- **County boundaries ≠ city boundaries.** County-level data includes suburban and rural areas around major cities, which may dilute or amplify urban violence patterns.
- **CDC suppression.** CDC WONDER suppresses counts below 10 for privacy. Some smaller counties may have unreliable or missing gun homicide data.
- **FBI UCR reporting.** Drug offense rates depend on agency participation in the Uniform Crime Reporting program. Not all agencies report consistently.
- **Mental illness as state proxy.** AMI prevalence is a state-level estimate (SAMHSA NSDUH). It measures *any* mental illness (including mild anxiety/depression), not severe mental illness specifically. County-level variation within states is not captured.
- **Mass shooting small-count volatility.** Mass shootings (4+ people shot) are rare events. Even aggregated over 5 years (2019-2023), many counties have very low counts (1-4 incidents), making per-capita rates subject to substantial volatility. A single additional incident can drastically change a small county's rate.

## How to Run

Requires Python 3.9+ with a virtualenv at `.venv/`.

```bash
# Install dependencies
.venv/bin/pip install pandas numpy matplotlib plotly scipy papermill

# Run all notebooks in place and generate the HTML report
./scripts/run_all.sh
```

Or run individual steps:

```bash
# Run a single notebook
.venv/bin/python -m papermill notebooks/01_data_collection.ipynb notebooks/01_data_collection.ipynb --cwd notebooks

# Generate report from already-executed notebooks
.venv/bin/python scripts/generate_html.py
```

The report is written to `docs/report.html`.
