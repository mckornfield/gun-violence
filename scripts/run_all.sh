#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PYTHON="${ROOT_DIR}/.venv/bin/python"
NB_DIR="${ROOT_DIR}/notebooks"

NOTEBOOKS=(
    01_data_collection
    02_gun_homicide_map
    03_gini_correlation
    04_drug_correlation
    05_population_correlation
    06_gun_ownership_correlation
    07_gun_control_correlation
    08_us_data_collection
    09_us_gun_homicide_map
    10_us_gini_correlation
    11_us_drug_correlation
    12_us_population_correlation
    13_us_poverty_correlation
    14_us_income_correlation
    15_us_gun_ownership_correlation
    16_us_gun_control_correlation
    17_us_mass_shooting_data
    18_us_mass_shooting_map
    19_us_mass_shooting_gini
    20_us_mass_shooting_drug
    21_us_mass_shooting_population
    22_us_mass_shooting_poverty
    23_us_mass_shooting_income
    24_us_mass_shooting_gun_ownership
    25_us_mass_shooting_gun_control
    26_us_mental_illness_homicide
    27_us_mass_shooting_mental_illness
)

echo "=== Running all notebooks in place ==="
for nb in "${NOTEBOOKS[@]}"; do
    nb_file="${NB_DIR}/${nb}.ipynb"
    echo "  Running ${nb}.ipynb ..."
    "$PYTHON" -m papermill "$nb_file" "$nb_file" --cwd "$NB_DIR" 2>&1 | tail -1
done

echo ""
echo "=== Generating HTML report ==="
"$PYTHON" "${SCRIPT_DIR}/generate_html.py"

echo ""
echo "Done."
