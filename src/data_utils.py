"""Shared data-loading utilities for gun violence country-level analysis."""

import pandas as pd
import requests


# ---------------------------------------------------------------------------
# World Bank API
# ---------------------------------------------------------------------------

def fetch_world_bank_indicator(indicator: str, year: str = "2022") -> pd.DataFrame:
    """Fetch a World Bank indicator for all countries.

    Returns a DataFrame with columns: country_code, country_name, value.
    """
    url = (
        f"https://api.worldbank.org/v2/country/all/indicator/{indicator}"
        f"?format=json&per_page=300&date={year}"
    )
    try:
        resp = requests.get(url, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        if len(data) < 2 or data[1] is None:
            return pd.DataFrame(columns=["country_code", "country_name", "value"])

        rows = []
        for entry in data[1]:
            code = entry.get("country", {}).get("id", "")
            name = entry.get("country", {}).get("value", "")
            val = entry.get("value")
            if val is not None and len(code) == 3:
                rows.append({
                    "country_code": code,
                    "country_name": name,
                    "value": float(val),
                })
        return pd.DataFrame(rows)
    except Exception as e:
        print(f"World Bank API error for {indicator}: {e}")
        return pd.DataFrame(columns=["country_code", "country_name", "value"])


def fetch_population(year: str = "2022") -> pd.DataFrame:
    """Fetch population by country from World Bank API with embedded fallback.

    Returns DataFrame with columns: country_code, country_name, population.
    """
    df = fetch_world_bank_indicator("SP.POP.TOTL", year)
    if len(df) >= 100:
        df = df.rename(columns={"value": "population"})
        return df

    print("Using embedded population fallback data")
    rows = []
    for code, (name, pop) in _POPULATION_FALLBACK.items():
        rows.append({"country_code": code, "country_name": name, "population": pop})
    return pd.DataFrame(rows)


def fetch_gini(year_range: str = "2018:2022") -> pd.DataFrame:
    """Fetch latest Gini coefficient per country from World Bank API.

    Tries each year in the range (most recent first) and takes the latest
    available value per country.

    Returns DataFrame with columns: country_code, country_name, gini.
    """
    start, end = year_range.split(":")
    all_rows = []
    for year in range(int(end), int(start) - 1, -1):
        df = fetch_world_bank_indicator("SI.POV.GINI", str(year))
        if len(df) > 0:
            df["year"] = year
            all_rows.append(df)

    if all_rows:
        combined = pd.concat(all_rows, ignore_index=True)
        # Keep the most recent year per country
        combined = combined.sort_values("year", ascending=False)
        combined = combined.drop_duplicates(subset=["country_code"], keep="first")
        if len(combined) >= 50:
            combined = combined.rename(columns={"value": "gini"})
            return combined[["country_code", "country_name", "gini"]].reset_index(drop=True)

    print("Using embedded Gini fallback data")
    rows = []
    for code, (name, gini) in _GINI_FALLBACK.items():
        rows.append({"country_code": code, "country_name": name, "gini": gini})
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Gun Homicide Rates (UNODC)
# ---------------------------------------------------------------------------

def get_gun_homicide_rates() -> pd.DataFrame:
    """Get gun homicide rates per 100K by country.

    Uses embedded fallback data from UNODC Global Study on Homicide.

    Returns DataFrame with columns: country_code, country_name, gun_homicide_rate.
    """
    rows = []
    for code, (name, rate) in _GUN_HOMICIDE_FALLBACK.items():
        rows.append({
            "country_code": code,
            "country_name": name,
            "gun_homicide_rate": rate,
        })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Drug Offense Rates (UNODC)
# ---------------------------------------------------------------------------

def get_drug_offense_rates() -> pd.DataFrame:
    """Get drug offense rates per 100K by country.

    Uses embedded fallback data from UNODC crime statistics.

    Returns DataFrame with columns: country_code, country_name, drug_offense_rate.
    """
    rows = []
    for code, (name, rate) in _DRUG_OFFENSE_FALLBACK.items():
        rows.append({
            "country_code": code,
            "country_name": name,
            "drug_offense_rate": rate,
        })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Gun Ownership Rates (Small Arms Survey 2017)
# ---------------------------------------------------------------------------

def get_gun_ownership_rates() -> pd.DataFrame:
    """Get civilian firearm ownership rates per 100 persons by country.

    Uses embedded data from the Small Arms Survey 2017 estimates.

    Returns DataFrame with columns: country_code, country_name, guns_per_100.
    """
    rows = []
    for code, (name, rate) in _GUN_OWNERSHIP_FALLBACK.items():
        rows.append({
            "country_code": code,
            "country_name": name,
            "guns_per_100": rate,
        })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Gun Control Strictness (Custom ordinal scale)
# ---------------------------------------------------------------------------

def get_gun_control_strictness() -> pd.DataFrame:
    """Get gun control strictness rating by country.

    Custom ordinal scale 1-5 based on publicly available regulatory
    information from GunPolicy.org and Library of Congress country reports.

    Scale:
      1 = Very Permissive — few restrictions on ownership/carry (e.g. USA, Yemen)
      2 = Permissive — ownership common, modest licensing (e.g. Switzerland, Czech Republic)
      3 = Moderate — licensing required, some category restrictions (e.g. Canada, France)
      4 = Strict — ownership is a privilege, significant barriers (e.g. UK, Australia)
      5 = Very Strict — civilian ownership effectively prohibited (e.g. Japan, China)

    Returns DataFrame with columns: country_code, country_name, gun_control_strictness.
    """
    rows = []
    for code, (name, level) in _GUN_CONTROL_STRICTNESS_FALLBACK.items():
        rows.append({
            "country_code": code,
            "country_name": name,
            "gun_control_strictness": level,
        })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Region mapping for scatter plot coloring
# ---------------------------------------------------------------------------

def get_country_regions() -> pd.DataFrame:
    """Return a DataFrame mapping country_code to region/continent.

    Returns DataFrame with columns: country_code, region.
    """
    rows = []
    for code, region in _COUNTRY_REGIONS.items():
        rows.append({"country_code": code, "region": region})
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Embedded Fallback Data
# ---------------------------------------------------------------------------

# Population (2022 estimates, World Bank)
# Format: code -> (name, population)
_POPULATION_FALLBACK = {
    "AFG": ("Afghanistan", 41128771), "ALB": ("Albania", 2842321),
    "DZA": ("Algeria", 44903225), "AGO": ("Angola", 34503774),
    "ARG": ("Argentina", 46234830), "ARM": ("Armenia", 2780469),
    "AUS": ("Australia", 25978935), "AUT": ("Austria", 9041851),
    "AZE": ("Azerbaijan", 10093121), "BHS": ("Bahamas", 409984),
    "BHR": ("Bahrain", 1472233), "BGD": ("Bangladesh", 169356251),
    "BRB": ("Barbados", 281200), "BLR": ("Belarus", 9534954),
    "BEL": ("Belgium", 11584008), "BLZ": ("Belize", 405272),
    "BEN": ("Benin", 12996895), "BTN": ("Bhutan", 782455),
    "BOL": ("Bolivia", 12224110), "BIH": ("Bosnia and Herzegovina", 3233526),
    "BWA": ("Botswana", 2588423), "BRA": ("Brazil", 214326223),
    "BRN": ("Brunei", 445373), "BGR": ("Bulgaria", 6781953),
    "BFA": ("Burkina Faso", 22100683), "BDI": ("Burundi", 12551213),
    "KHM": ("Cambodia", 16767842), "CMR": ("Cameroon", 27198628),
    "CAN": ("Canada", 38929902), "CPV": ("Cabo Verde", 593149),
    "CAF": ("Central African Republic", 5579144),
    "TCD": ("Chad", 17179740), "CHL": ("Chile", 19603733),
    "CHN": ("China", 1412175000), "COL": ("Colombia", 51874024),
    "COM": ("Comoros", 821625), "COG": ("Congo", 5970424),
    "COD": ("DR Congo", 95894118), "CRI": ("Costa Rica", 5180829),
    "CIV": ("Cote d'Ivoire", 27478249), "HRV": ("Croatia", 3855600),
    "CUB": ("Cuba", 11212191), "CYP": ("Cyprus", 1251488),
    "CZE": ("Czech Republic", 10827529), "DNK": ("Denmark", 5903037),
    "DJI": ("Djibouti", 1105557), "DOM": ("Dominican Republic", 11228821),
    "ECU": ("Ecuador", 17797737), "EGY": ("Egypt", 109262178),
    "SLV": ("El Salvador", 6314167), "GNQ": ("Equatorial Guinea", 1634466),
    "ERI": ("Eritrea", 3620312), "EST": ("Estonia", 1348840),
    "SWZ": ("Eswatini", 1192271), "ETH": ("Ethiopia", 123379924),
    "FJI": ("Fiji", 929766), "FIN": ("Finland", 5556106),
    "FRA": ("France", 67935660), "GAB": ("Gabon", 2341179),
    "GMB": ("Gambia", 2639916), "GEO": ("Georgia", 3736400),
    "DEU": ("Germany", 83369843), "GHA": ("Ghana", 33475870),
    "GRC": ("Greece", 10384971), "GTM": ("Guatemala", 17602431),
    "GIN": ("Guinea", 13531906), "GNB": ("Guinea-Bissau", 2060721),
    "GUY": ("Guyana", 808726), "HTI": ("Haiti", 11584996),
    "HND": ("Honduras", 10278345), "HUN": ("Hungary", 9750149),
    "ISL": ("Iceland", 376248), "IND": ("India", 1417173173),
    "IDN": ("Indonesia", 275501339), "IRN": ("Iran", 87923432),
    "IRQ": ("Iraq", 43533592), "IRL": ("Ireland", 5127170),
    "ISR": ("Israel", 9557500), "ITA": ("Italy", 58940425),
    "JAM": ("Jamaica", 2827695), "JPN": ("Japan", 125124989),
    "JOR": ("Jordan", 11148278), "KAZ": ("Kazakhstan", 19397998),
    "KEN": ("Kenya", 54027487), "KWT": ("Kuwait", 4268873),
    "KGZ": ("Kyrgyzstan", 6747815), "LAO": ("Laos", 7529475),
    "LVA": ("Latvia", 1883008), "LBN": ("Lebanon", 5489739),
    "LSO": ("Lesotho", 2281454), "LBR": ("Liberia", 5302681),
    "LBY": ("Libya", 6812341), "LTU": ("Lithuania", 2831639),
    "LUX": ("Luxembourg", 660809), "MDG": ("Madagascar", 29611714),
    "MWI": ("Malawi", 19889742), "MYS": ("Malaysia", 33938221),
    "MLI": ("Mali", 22593590), "MLT": ("Malta", 531113),
    "MRT": ("Mauritania", 4614974), "MUS": ("Mauritius", 1265740),
    "MEX": ("Mexico", 127504125), "MDA": ("Moldova", 2615199),
    "MNG": ("Mongolia", 3398366), "MNE": ("Montenegro", 616177),
    "MAR": ("Morocco", 37457971), "MOZ": ("Mozambique", 32969518),
    "MMR": ("Myanmar", 54179306), "NAM": ("Namibia", 2567012),
    "NPL": ("Nepal", 30034989), "NLD": ("Netherlands", 17590672),
    "NZL": ("New Zealand", 5123200), "NIC": ("Nicaragua", 6948392),
    "NER": ("Niger", 25252722), "NGA": ("Nigeria", 218541212),
    "NOR": ("Norway", 5457127), "OMN": ("Oman", 4576298),
    "PAK": ("Pakistan", 231402117), "PAN": ("Panama", 4408581),
    "PNG": ("Papua New Guinea", 10142619), "PRY": ("Paraguay", 6780744),
    "PER": ("Peru", 33684208), "PHL": ("Philippines", 115559009),
    "POL": ("Poland", 36821749), "PRT": ("Portugal", 10352042),
    "QAT": ("Qatar", 2695122), "ROU": ("Romania", 19659267),
    "RUS": ("Russia", 144236933), "RWA": ("Rwanda", 13461888),
    "SAU": ("Saudi Arabia", 36408820), "SEN": ("Senegal", 17316449),
    "SRB": ("Serbia", 6664449), "SLE": ("Sierra Leone", 8420641),
    "SGP": ("Singapore", 5637022), "SVK": ("Slovakia", 5643453),
    "SVN": ("Slovenia", 2119675), "SOM": ("Somalia", 17597511),
    "ZAF": ("South Africa", 59893885), "KOR": ("South Korea", 51628117),
    "SSD": ("South Sudan", 10913164), "ESP": ("Spain", 47778340),
    "LKA": ("Sri Lanka", 22156000), "SDN": ("Sudan", 45657202),
    "SUR": ("Suriname", 612985), "SWE": ("Sweden", 10486941),
    "CHE": ("Switzerland", 8775760), "SYR": ("Syria", 22125249),
    "TWN": ("Taiwan", 23894394), "TJK": ("Tajikistan", 9952787),
    "TZA": ("Tanzania", 63588334), "THA": ("Thailand", 71697030),
    "TLS": ("Timor-Leste", 1341296), "TGO": ("Togo", 8848699),
    "TTO": ("Trinidad and Tobago", 1525663),
    "TUN": ("Tunisia", 12356117), "TUR": ("Turkey", 84775404),
    "TKM": ("Turkmenistan", 6341855), "UGA": ("Uganda", 45853778),
    "UKR": ("Ukraine", 43792855), "ARE": ("United Arab Emirates", 9441129),
    "GBR": ("United Kingdom", 67508936),
    "USA": ("United States", 333287557), "URY": ("Uruguay", 3422794),
    "UZB": ("Uzbekistan", 35163944), "VEN": ("Venezuela", 28301696),
    "VNM": ("Vietnam", 98186856), "YEM": ("Yemen", 33696614),
    "ZMB": ("Zambia", 19473125), "ZWE": ("Zimbabwe", 15993524),
}

# Gini coefficient (latest available, World Bank ~2018-2022)
# Format: code -> (name, gini)
_GINI_FALLBACK = {
    "ALB": ("Albania", 30.0), "DZA": ("Algeria", 27.6),
    "AGO": ("Angola", 51.3), "ARG": ("Argentina", 42.3),
    "ARM": ("Armenia", 29.9), "AUS": ("Australia", 34.3),
    "AUT": ("Austria", 30.5), "AZE": ("Azerbaijan", 26.6),
    "BGD": ("Bangladesh", 32.4), "BLR": ("Belarus", 25.3),
    "BEL": ("Belgium", 27.2), "BLZ": ("Belize", 53.3),
    "BEN": ("Benin", 37.8), "BTN": ("Bhutan", 37.4),
    "BOL": ("Bolivia", 43.6), "BIH": ("Bosnia and Herzegovina", 33.0),
    "BWA": ("Botswana", 53.3), "BRA": ("Brazil", 52.9),
    "BGR": ("Bulgaria", 40.3), "BFA": ("Burkina Faso", 47.3),
    "BDI": ("Burundi", 38.6), "KHM": ("Cambodia", 38.0),
    "CMR": ("Cameroon", 46.6), "CAN": ("Canada", 33.3),
    "CAF": ("Central African Republic", 56.2),
    "TCD": ("Chad", 37.5), "CHL": ("Chile", 44.9),
    "CHN": ("China", 38.2), "COL": ("Colombia", 51.5),
    "COM": ("Comoros", 45.3), "COG": ("Congo", 48.9),
    "COD": ("DR Congo", 42.1), "CRI": ("Costa Rica", 48.2),
    "CIV": ("Cote d'Ivoire", 37.2), "HRV": ("Croatia", 29.7),
    "CYP": ("Cyprus", 31.4), "CZE": ("Czech Republic", 25.3),
    "DNK": ("Denmark", 28.2), "DJI": ("Djibouti", 41.6),
    "DOM": ("Dominican Republic", 39.6), "ECU": ("Ecuador", 47.3),
    "EGY": ("Egypt", 31.5), "SLV": ("El Salvador", 38.8),
    "EST": ("Estonia", 30.4), "SWZ": ("Eswatini", 54.6),
    "ETH": ("Ethiopia", 35.0), "FJI": ("Fiji", 36.7),
    "FIN": ("Finland", 27.7), "FRA": ("France", 31.6),
    "GAB": ("Gabon", 38.0), "GMB": ("Gambia", 35.9),
    "GEO": ("Georgia", 34.5), "DEU": ("Germany", 31.7),
    "GHA": ("Ghana", 43.5), "GRC": ("Greece", 33.1),
    "GTM": ("Guatemala", 48.3), "GIN": ("Guinea", 29.6),
    "GNB": ("Guinea-Bissau", 50.7), "GUY": ("Guyana", 45.1),
    "HTI": ("Haiti", 41.1), "HND": ("Honduras", 48.2),
    "HUN": ("Hungary", 30.6), "ISL": ("Iceland", 26.1),
    "IND": ("India", 35.7), "IDN": ("Indonesia", 37.9),
    "IRN": ("Iran", 40.9), "IRQ": ("Iraq", 29.5),
    "IRL": ("Ireland", 30.6), "ISR": ("Israel", 39.0),
    "ITA": ("Italy", 35.2), "JAM": ("Jamaica", 35.0),
    "JPN": ("Japan", 32.9), "JOR": ("Jordan", 33.7),
    "KAZ": ("Kazakhstan", 29.2), "KEN": ("Kenya", 40.8),
    "KOR": ("South Korea", 31.4), "KGZ": ("Kyrgyzstan", 29.0),
    "LAO": ("Laos", 38.8), "LVA": ("Latvia", 35.1),
    "LBN": ("Lebanon", 31.8), "LSO": ("Lesotho", 44.9),
    "LBR": ("Liberia", 35.3), "LTU": ("Lithuania", 36.9),
    "LUX": ("Luxembourg", 35.4), "MDG": ("Madagascar", 42.6),
    "MWI": ("Malawi", 44.7), "MYS": ("Malaysia", 41.2),
    "MLI": ("Mali", 36.1), "MLT": ("Malta", 30.7),
    "MRT": ("Mauritania", 32.6), "MUS": ("Mauritius", 36.8),
    "MEX": ("Mexico", 45.4), "MDA": ("Moldova", 26.0),
    "MNG": ("Mongolia", 32.7), "MNE": ("Montenegro", 36.8),
    "MAR": ("Morocco", 39.5), "MOZ": ("Mozambique", 54.0),
    "MMR": ("Myanmar", 30.7), "NAM": ("Namibia", 59.1),
    "NPL": ("Nepal", 32.8), "NLD": ("Netherlands", 28.5),
    "NZL": ("New Zealand", 36.0), "NIC": ("Nicaragua", 46.2),
    "NER": ("Niger", 37.3), "NGA": ("Nigeria", 35.1),
    "NOR": ("Norway", 27.6), "PAK": ("Pakistan", 29.6),
    "PAN": ("Panama", 49.8), "PNG": ("Papua New Guinea", 41.9),
    "PRY": ("Paraguay", 45.1), "PER": ("Peru", 43.8),
    "PHL": ("Philippines", 42.3), "POL": ("Poland", 29.7),
    "PRT": ("Portugal", 33.6), "ROU": ("Romania", 34.8),
    "RUS": ("Russia", 36.0), "RWA": ("Rwanda", 43.7),
    "SAU": ("Saudi Arabia", 45.9), "SEN": ("Senegal", 40.3),
    "SRB": ("Serbia", 36.2), "SLE": ("Sierra Leone", 35.7),
    "SGP": ("Singapore", 45.9), "SVK": ("Slovakia", 25.2),
    "SVN": ("Slovenia", 24.6), "ZAF": ("South Africa", 63.0),
    "ESP": ("Spain", 33.0), "LKA": ("Sri Lanka", 37.7),
    "SDN": ("Sudan", 34.2), "SUR": ("Suriname", 57.9),
    "SWE": ("Sweden", 30.0), "CHE": ("Switzerland", 33.1),
    "TJK": ("Tajikistan", 34.0), "TZA": ("Tanzania", 40.5),
    "THA": ("Thailand", 34.9), "TLS": ("Timor-Leste", 28.7),
    "TGO": ("Togo", 43.1), "TTO": ("Trinidad and Tobago", 40.3),
    "TUN": ("Tunisia", 32.8), "TUR": ("Turkey", 41.9),
    "TKM": ("Turkmenistan", 40.8), "UGA": ("Uganda", 42.7),
    "UKR": ("Ukraine", 25.6), "ARE": ("United Arab Emirates", 32.5),
    "GBR": ("United Kingdom", 35.1), "USA": ("United States", 39.8),
    "URY": ("Uruguay", 40.2), "UZB": ("Uzbekistan", 35.3),
    "VEN": ("Venezuela", 44.8), "VNM": ("Vietnam", 36.8),
    "YEM": ("Yemen", 36.7), "ZMB": ("Zambia", 57.1),
    "ZWE": ("Zimbabwe", 50.3),
}

# Gun homicide rate per 100K (UNODC, most recent available ~2020-2022)
# Format: code -> (name, rate)
_GUN_HOMICIDE_FALLBACK = {
    "AFG": ("Afghanistan", 4.7), "ALB": ("Albania", 1.3),
    "DZA": ("Algeria", 0.5), "AGO": ("Angola", 4.8),
    "ARG": ("Argentina", 2.2), "ARM": ("Armenia", 0.4),
    "AUS": ("Australia", 0.15), "AUT": ("Austria", 0.15),
    "AZE": ("Azerbaijan", 0.6), "BHS": ("Bahamas", 24.5),
    "BHR": ("Bahrain", 0.1), "BGD": ("Bangladesh", 1.1),
    "BRB": ("Barbados", 7.4), "BLR": ("Belarus", 0.2),
    "BEL": ("Belgium", 0.3), "BLZ": ("Belize", 19.4),
    "BEN": ("Benin", 0.8), "BOL": ("Bolivia", 3.0),
    "BIH": ("Bosnia and Herzegovina", 0.6),
    "BWA": ("Botswana", 2.8), "BRA": ("Brazil", 21.9),
    "BGR": ("Bulgaria", 0.5), "BFA": ("Burkina Faso", 1.5),
    "BDI": ("Burundi", 2.1), "KHM": ("Cambodia", 0.8),
    "CMR": ("Cameroon", 2.9), "CAN": ("Canada", 0.75),
    "CAF": ("Central African Republic", 6.1),
    "TCD": ("Chad", 3.2), "CHL": ("Chile", 2.1),
    "CHN": ("China", 0.04), "COL": ("Colombia", 13.1),
    "COG": ("Congo", 4.7), "COD": ("DR Congo", 3.0),
    "CRI": ("Costa Rica", 6.3), "CIV": ("Cote d'Ivoire", 1.6),
    "HRV": ("Croatia", 0.3), "CUB": ("Cuba", 2.5),
    "CYP": ("Cyprus", 0.2), "CZE": ("Czech Republic", 0.12),
    "DNK": ("Denmark", 0.15), "DOM": ("Dominican Republic", 11.2),
    "ECU": ("Ecuador", 5.6), "EGY": ("Egypt", 0.4),
    "SLV": ("El Salvador", 17.5), "GNQ": ("Equatorial Guinea", 2.1),
    "ERI": ("Eritrea", 2.8), "EST": ("Estonia", 0.3),
    "SWZ": ("Eswatini", 6.3), "ETH": ("Ethiopia", 3.5),
    "FJI": ("Fiji", 0.5), "FIN": ("Finland", 0.2),
    "FRA": ("France", 0.3), "GAB": ("Gabon", 2.4),
    "GEO": ("Georgia", 0.8), "DEU": ("Germany", 0.06),
    "GHA": ("Ghana", 1.7), "GRC": ("Greece", 0.4),
    "GTM": ("Guatemala", 18.5), "GIN": ("Guinea", 2.6),
    "GNB": ("Guinea-Bissau", 3.4), "GUY": ("Guyana", 7.1),
    "HTI": ("Haiti", 12.0), "HND": ("Honduras", 26.7),
    "HUN": ("Hungary", 0.12), "ISL": ("Iceland", 0.0),
    "IND": ("India", 0.9), "IDN": ("Indonesia", 0.1),
    "IRN": ("Iran", 1.3), "IRQ": ("Iraq", 5.2),
    "IRL": ("Ireland", 0.2), "ISR": ("Israel", 0.7),
    "ITA": ("Italy", 0.35), "JAM": ("Jamaica", 30.7),
    "JPN": ("Japan", 0.01), "JOR": ("Jordan", 0.5),
    "KAZ": ("Kazakhstan", 0.5), "KEN": ("Kenya", 2.3),
    "KOR": ("South Korea", 0.02), "KWT": ("Kuwait", 0.4),
    "KGZ": ("Kyrgyzstan", 1.2), "LVA": ("Latvia", 0.5),
    "LBN": ("Lebanon", 3.0), "LSO": ("Lesotho", 3.1),
    "LBR": ("Liberia", 3.2), "LBY": ("Libya", 4.5),
    "LTU": ("Lithuania", 0.4), "LUX": ("Luxembourg", 0.1),
    "MDG": ("Madagascar", 1.4), "MWI": ("Malawi", 1.0),
    "MYS": ("Malaysia", 0.3), "MLI": ("Mali", 3.5),
    "MLT": ("Malta", 0.3), "MRT": ("Mauritania", 1.2),
    "MUS": ("Mauritius", 0.4), "MEX": ("Mexico", 16.3),
    "MDA": ("Moldova", 0.5), "MNG": ("Mongolia", 0.6),
    "MNE": ("Montenegro", 1.4), "MAR": ("Morocco", 0.3),
    "MOZ": ("Mozambique", 3.0), "MMR": ("Myanmar", 2.3),
    "NAM": ("Namibia", 5.2), "NPL": ("Nepal", 0.9),
    "NLD": ("Netherlands", 0.2), "NZL": ("New Zealand", 0.18),
    "NIC": ("Nicaragua", 5.3), "NER": ("Niger", 1.7),
    "NGA": ("Nigeria", 3.2), "NOR": ("Norway", 0.1),
    "OMN": ("Oman", 0.2), "PAK": ("Pakistan", 3.0),
    "PAN": ("Panama", 7.8), "PNG": ("Papua New Guinea", 5.6),
    "PRY": ("Paraguay", 5.5), "PER": ("Peru", 3.7),
    "PHL": ("Philippines", 5.4), "POL": ("Poland", 0.08),
    "PRT": ("Portugal", 0.3), "QAT": ("Qatar", 0.1),
    "ROU": ("Romania", 0.1), "RUS": ("Russia", 2.7),
    "RWA": ("Rwanda", 1.1), "SAU": ("Saudi Arabia", 0.6),
    "SEN": ("Senegal", 1.4), "SRB": ("Serbia", 0.5),
    "SLE": ("Sierra Leone", 1.8), "SGP": ("Singapore", 0.02),
    "SVK": ("Slovakia", 0.2), "SVN": ("Slovenia", 0.1),
    "SOM": ("Somalia", 5.6), "ZAF": ("South Africa", 10.2),
    "SSD": ("South Sudan", 6.5), "ESP": ("Spain", 0.12),
    "LKA": ("Sri Lanka", 1.4), "SDN": ("Sudan", 5.1),
    "SUR": ("Suriname", 5.1), "SWE": ("Sweden", 0.4),
    "CHE": ("Switzerland", 0.15), "SYR": ("Syria", 3.0),
    "TJK": ("Tajikistan", 0.5), "TZA": ("Tanzania", 2.3),
    "THA": ("Thailand", 2.5), "TLS": ("Timor-Leste", 1.0),
    "TGO": ("Togo", 2.3), "TTO": ("Trinidad and Tobago", 20.3),
    "TUN": ("Tunisia", 0.3), "TUR": ("Turkey", 1.8),
    "TKM": ("Turkmenistan", 1.0), "UGA": ("Uganda", 3.3),
    "UKR": ("Ukraine", 1.6), "ARE": ("United Arab Emirates", 0.3),
    "GBR": ("United Kingdom", 0.04), "USA": ("United States", 4.46),
    "URY": ("Uruguay", 3.5), "UZB": ("Uzbekistan", 0.5),
    "VEN": ("Venezuela", 33.3), "VNM": ("Vietnam", 0.5),
    "YEM": ("Yemen", 4.8), "ZMB": ("Zambia", 2.8),
    "ZWE": ("Zimbabwe", 2.5),
}

# Drug offense rate per 100K (UNODC crime statistics, ~2020)
# Format: code -> (name, rate)
_DRUG_OFFENSE_FALLBACK = {
    "ALB": ("Albania", 45.0), "DZA": ("Algeria", 85.0),
    "ARG": ("Argentina", 102.0), "ARM": ("Armenia", 38.0),
    "AUS": ("Australia", 605.0), "AUT": ("Austria", 340.0),
    "AZE": ("Azerbaijan", 42.0), "BHS": ("Bahamas", 310.0),
    "BGD": ("Bangladesh", 72.0), "BLR": ("Belarus", 120.0),
    "BEL": ("Belgium", 340.0), "BLZ": ("Belize", 195.0),
    "BEN": ("Benin", 12.0), "BOL": ("Bolivia", 65.0),
    "BIH": ("Bosnia and Herzegovina", 75.0),
    "BWA": ("Botswana", 210.0), "BRA": ("Brazil", 155.0),
    "BGR": ("Bulgaria", 105.0), "BFA": ("Burkina Faso", 8.0),
    "KHM": ("Cambodia", 48.0), "CMR": ("Cameroon", 15.0),
    "CAN": ("Canada", 280.0), "CHL": ("Chile", 210.0),
    "CHN": ("China", 35.0), "COL": ("Colombia", 120.0),
    "CRI": ("Costa Rica", 105.0), "HRV": ("Croatia", 165.0),
    "CYP": ("Cyprus", 185.0), "CZE": ("Czech Republic", 85.0),
    "DNK": ("Denmark", 380.0), "DOM": ("Dominican Republic", 52.0),
    "ECU": ("Ecuador", 68.0), "EGY": ("Egypt", 35.0),
    "SLV": ("El Salvador", 42.0), "EST": ("Estonia", 185.0),
    "ETH": ("Ethiopia", 15.0), "FIN": ("Finland", 420.0),
    "FRA": ("France", 290.0), "GEO": ("Georgia", 125.0),
    "DEU": ("Germany", 325.0), "GHA": ("Ghana", 28.0),
    "GRC": ("Greece", 125.0), "GTM": ("Guatemala", 35.0),
    "GUY": ("Guyana", 78.0), "HND": ("Honduras", 38.0),
    "HUN": ("Hungary", 55.0), "ISL": ("Iceland", 310.0),
    "IND": ("India", 18.0), "IDN": ("Indonesia", 38.0),
    "IRN": ("Iran", 450.0), "IRQ": ("Iraq", 22.0),
    "IRL": ("Ireland", 290.0), "ISR": ("Israel", 210.0),
    "ITA": ("Italy", 165.0), "JAM": ("Jamaica", 135.0),
    "JPN": ("Japan", 22.0), "JOR": ("Jordan", 42.0),
    "KAZ": ("Kazakhstan", 82.0), "KEN": ("Kenya", 48.0),
    "KOR": ("South Korea", 52.0), "KWT": ("Kuwait", 32.0),
    "KGZ": ("Kyrgyzstan", 55.0), "LVA": ("Latvia", 85.0),
    "LBN": ("Lebanon", 95.0), "LTU": ("Lithuania", 95.0),
    "LUX": ("Luxembourg", 385.0), "MYS": ("Malaysia", 115.0),
    "MLI": ("Mali", 10.0), "MLT": ("Malta", 155.0),
    "MUS": ("Mauritius", 145.0), "MEX": ("Mexico", 55.0),
    "MDA": ("Moldova", 65.0), "MNG": ("Mongolia", 42.0),
    "MNE": ("Montenegro", 115.0), "MAR": ("Morocco", 85.0),
    "MOZ": ("Mozambique", 18.0), "MMR": ("Myanmar", 175.0),
    "NAM": ("Namibia", 110.0), "NPL": ("Nepal", 22.0),
    "NLD": ("Netherlands", 165.0), "NZL": ("New Zealand", 455.0),
    "NIC": ("Nicaragua", 32.0), "NGA": ("Nigeria", 20.0),
    "NOR": ("Norway", 420.0), "PAK": ("Pakistan", 55.0),
    "PAN": ("Panama", 85.0), "PRY": ("Paraguay", 48.0),
    "PER": ("Peru", 72.0), "PHL": ("Philippines", 180.0),
    "POL": ("Poland", 85.0), "PRT": ("Portugal", 155.0),
    "QAT": ("Qatar", 28.0), "ROU": ("Romania", 35.0),
    "RUS": ("Russia", 155.0), "SAU": ("Saudi Arabia", 42.0),
    "SEN": ("Senegal", 22.0), "SRB": ("Serbia", 95.0),
    "SGP": ("Singapore", 45.0), "SVK": ("Slovakia", 48.0),
    "SVN": ("Slovenia", 135.0), "ZAF": ("South Africa", 195.0),
    "ESP": ("Spain", 145.0), "LKA": ("Sri Lanka", 185.0),
    "SUR": ("Suriname", 55.0), "SWE": ("Sweden", 395.0),
    "CHE": ("Switzerland", 470.0), "THA": ("Thailand", 345.0),
    "TTO": ("Trinidad and Tobago", 155.0),
    "TUN": ("Tunisia", 35.0), "TUR": ("Turkey", 185.0),
    "UGA": ("Uganda", 30.0), "UKR": ("Ukraine", 48.0),
    "ARE": ("United Arab Emirates", 72.0),
    "GBR": ("United Kingdom", 185.0),
    "USA": ("United States", 585.0), "URY": ("Uruguay", 115.0),
    "UZB": ("Uzbekistan", 32.0), "VEN": ("Venezuela", 42.0),
    "VNM": ("Vietnam", 28.0), "ZMB": ("Zambia", 32.0),
    "ZWE": ("Zimbabwe", 45.0),
}

# Country → Region mapping for scatter plot coloring
_COUNTRY_REGIONS = {
    # North America
    "USA": "North America", "CAN": "North America", "MEX": "North America",
    # Central America & Caribbean
    "GTM": "Central America & Caribbean", "BLZ": "Central America & Caribbean",
    "HND": "Central America & Caribbean", "SLV": "Central America & Caribbean",
    "NIC": "Central America & Caribbean", "CRI": "Central America & Caribbean",
    "PAN": "Central America & Caribbean", "CUB": "Central America & Caribbean",
    "JAM": "Central America & Caribbean", "HTI": "Central America & Caribbean",
    "DOM": "Central America & Caribbean", "TTO": "Central America & Caribbean",
    "BHS": "Central America & Caribbean", "BRB": "Central America & Caribbean",
    # South America
    "BRA": "South America", "ARG": "South America", "COL": "South America",
    "VEN": "South America", "PER": "South America", "CHL": "South America",
    "ECU": "South America", "BOL": "South America", "PRY": "South America",
    "URY": "South America", "GUY": "South America", "SUR": "South America",
    # Western Europe
    "GBR": "Western Europe", "FRA": "Western Europe", "DEU": "Western Europe",
    "ESP": "Western Europe", "ITA": "Western Europe", "PRT": "Western Europe",
    "NLD": "Western Europe", "BEL": "Western Europe", "CHE": "Western Europe",
    "AUT": "Western Europe", "IRL": "Western Europe", "LUX": "Western Europe",
    "DNK": "Western Europe", "NOR": "Western Europe", "SWE": "Western Europe",
    "FIN": "Western Europe", "ISL": "Western Europe", "MLT": "Western Europe",
    "CYP": "Western Europe", "GRC": "Western Europe",
    # Eastern Europe
    "RUS": "Eastern Europe", "UKR": "Eastern Europe", "POL": "Eastern Europe",
    "ROU": "Eastern Europe", "CZE": "Eastern Europe", "HUN": "Eastern Europe",
    "BGR": "Eastern Europe", "SRB": "Eastern Europe", "HRV": "Eastern Europe",
    "SVK": "Eastern Europe", "SVN": "Eastern Europe", "BIH": "Eastern Europe",
    "MNE": "Eastern Europe", "ALB": "Eastern Europe", "MDA": "Eastern Europe",
    "BLR": "Eastern Europe", "LTU": "Eastern Europe", "LVA": "Eastern Europe",
    "EST": "Eastern Europe", "GEO": "Eastern Europe", "ARM": "Eastern Europe",
    "AZE": "Eastern Europe",
    # Middle East & North Africa
    "SAU": "Middle East & N. Africa", "ARE": "Middle East & N. Africa",
    "ISR": "Middle East & N. Africa", "TUR": "Middle East & N. Africa",
    "IRN": "Middle East & N. Africa", "IRQ": "Middle East & N. Africa",
    "JOR": "Middle East & N. Africa", "LBN": "Middle East & N. Africa",
    "KWT": "Middle East & N. Africa", "QAT": "Middle East & N. Africa",
    "BHR": "Middle East & N. Africa", "OMN": "Middle East & N. Africa",
    "SYR": "Middle East & N. Africa", "YEM": "Middle East & N. Africa",
    "EGY": "Middle East & N. Africa", "LBY": "Middle East & N. Africa",
    "TUN": "Middle East & N. Africa", "DZA": "Middle East & N. Africa",
    "MAR": "Middle East & N. Africa",
    # Sub-Saharan Africa
    "NGA": "Sub-Saharan Africa", "ZAF": "Sub-Saharan Africa",
    "KEN": "Sub-Saharan Africa", "ETH": "Sub-Saharan Africa",
    "GHA": "Sub-Saharan Africa", "TZA": "Sub-Saharan Africa",
    "UGA": "Sub-Saharan Africa", "CMR": "Sub-Saharan Africa",
    "CIV": "Sub-Saharan Africa", "SEN": "Sub-Saharan Africa",
    "MLI": "Sub-Saharan Africa", "BFA": "Sub-Saharan Africa",
    "NER": "Sub-Saharan Africa", "TCD": "Sub-Saharan Africa",
    "SDN": "Sub-Saharan Africa", "SSD": "Sub-Saharan Africa",
    "SOM": "Sub-Saharan Africa", "COG": "Sub-Saharan Africa",
    "COD": "Sub-Saharan Africa", "MOZ": "Sub-Saharan Africa",
    "MDG": "Sub-Saharan Africa", "MWI": "Sub-Saharan Africa",
    "ZMB": "Sub-Saharan Africa", "ZWE": "Sub-Saharan Africa",
    "AGO": "Sub-Saharan Africa", "NAM": "Sub-Saharan Africa",
    "BWA": "Sub-Saharan Africa", "LSO": "Sub-Saharan Africa",
    "SWZ": "Sub-Saharan Africa", "RWA": "Sub-Saharan Africa",
    "BDI": "Sub-Saharan Africa", "BEN": "Sub-Saharan Africa",
    "TGO": "Sub-Saharan Africa", "SLE": "Sub-Saharan Africa",
    "LBR": "Sub-Saharan Africa", "GIN": "Sub-Saharan Africa",
    "GNB": "Sub-Saharan Africa", "GMB": "Sub-Saharan Africa",
    "GAB": "Sub-Saharan Africa", "GNQ": "Sub-Saharan Africa",
    "ERI": "Sub-Saharan Africa", "DJI": "Sub-Saharan Africa",
    "CPV": "Sub-Saharan Africa", "MUS": "Sub-Saharan Africa",
    "MRT": "Sub-Saharan Africa", "CAF": "Sub-Saharan Africa",
    "AFG": "Sub-Saharan Africa",
    # South Asia
    "IND": "South & Central Asia", "PAK": "South & Central Asia",
    "BGD": "South & Central Asia", "LKA": "South & Central Asia",
    "NPL": "South & Central Asia", "BTN": "South & Central Asia",
    "KAZ": "South & Central Asia", "UZB": "South & Central Asia",
    "TKM": "South & Central Asia", "TJK": "South & Central Asia",
    "KGZ": "South & Central Asia",
    # East & Southeast Asia
    "CHN": "East & SE Asia", "JPN": "East & SE Asia",
    "KOR": "East & SE Asia", "TWN": "East & SE Asia",
    "MNG": "East & SE Asia", "IDN": "East & SE Asia",
    "PHL": "East & SE Asia", "VNM": "East & SE Asia",
    "THA": "East & SE Asia", "MYS": "East & SE Asia",
    "SGP": "East & SE Asia", "MMR": "East & SE Asia",
    "KHM": "East & SE Asia", "LAO": "East & SE Asia",
    "BRN": "East & SE Asia", "TLS": "East & SE Asia",
    # Oceania
    "AUS": "Oceania", "NZL": "Oceania", "FJI": "Oceania",
    "PNG": "Oceania",
}

# Gun ownership: civilian firearms per 100 persons (Small Arms Survey 2017)
# Format: code -> (name, guns_per_100)
_GUN_OWNERSHIP_FALLBACK = {
    "AFG": ("Afghanistan", 12.5), "ALB": ("Albania", 8.6),
    "DZA": ("Algeria", 7.1), "AGO": ("Angola", 3.0),
    "ARG": ("Argentina", 10.2), "ARM": ("Armenia", 4.4),
    "AUS": ("Australia", 13.7), "AUT": ("Austria", 30.0),
    "AZE": ("Azerbaijan", 3.6), "BHS": ("Bahamas", 5.3),
    "BHR": ("Bahrain", 11.6), "BGD": ("Bangladesh", 0.5),
    "BRB": ("Barbados", 3.2), "BLR": ("Belarus", 7.3),
    "BEL": ("Belgium", 12.2), "BLZ": ("Belize", 10.0),
    "BEN": ("Benin", 1.4), "BOL": ("Bolivia", 2.8),
    "BIH": ("Bosnia and Herzegovina", 31.2),
    "BWA": ("Botswana", 3.3), "BRA": ("Brazil", 8.3),
    "BGR": ("Bulgaria", 6.2), "BFA": ("Burkina Faso", 1.1),
    "BDI": ("Burundi", 1.6), "KHM": ("Cambodia", 4.5),
    "CMR": ("Cameroon", 1.1), "CAN": ("Canada", 34.7),
    "CAF": ("Central African Republic", 1.0),
    "TCD": ("Chad", 1.3), "CHL": ("Chile", 10.5),
    "CHN": ("China", 3.6), "COL": ("Colombia", 10.1),
    "COG": ("Congo", 2.1), "COD": ("DR Congo", 1.4),
    "CRI": ("Costa Rica", 10.0), "CIV": ("Cote d'Ivoire", 2.8),
    "HRV": ("Croatia", 21.7), "CUB": ("Cuba", 4.5),
    "CYP": ("Cyprus", 36.4), "CZE": ("Czech Republic", 16.3),
    "DNK": ("Denmark", 9.9), "DOM": ("Dominican Republic", 8.7),
    "ECU": ("Ecuador", 3.8), "EGY": ("Egypt", 3.5),
    "SLV": ("El Salvador", 5.8), "ERI": ("Eritrea", 0.5),
    "EST": ("Estonia", 9.2), "SWZ": ("Eswatini", 3.5),
    "ETH": ("Ethiopia", 0.6), "FJI": ("Fiji", 0.5),
    "FIN": ("Finland", 32.4), "FRA": ("France", 19.6),
    "GAB": ("Gabon", 2.0), "GMB": ("Gambia", 1.3),
    "GEO": ("Georgia", 7.5), "DEU": ("Germany", 19.6),
    "GHA": ("Ghana", 1.4), "GRC": ("Greece", 22.5),
    "GTM": ("Guatemala", 12.0), "GIN": ("Guinea", 1.1),
    "GNB": ("Guinea-Bissau", 2.0), "GUY": ("Guyana", 4.0),
    "HTI": ("Haiti", 1.7), "HND": ("Honduras", 14.1),
    "HUN": ("Hungary", 5.5), "ISL": ("Iceland", 30.3),
    "IND": ("India", 5.3), "IDN": ("Indonesia", 0.5),
    "IRN": ("Iran", 7.3), "IRQ": ("Iraq", 19.6),
    "IRL": ("Ireland", 7.2), "ISR": ("Israel", 7.3),
    "ITA": ("Italy", 14.4), "JAM": ("Jamaica", 8.1),
    "JPN": ("Japan", 0.3), "JOR": ("Jordan", 11.5),
    "KAZ": ("Kazakhstan", 3.9), "KEN": ("Kenya", 1.7),
    "KOR": ("South Korea", 0.2), "KWT": ("Kuwait", 24.8),
    "KGZ": ("Kyrgyzstan", 3.9), "LAO": ("Laos", 2.2),
    "LVA": ("Latvia", 10.1), "LBN": ("Lebanon", 31.9),
    "LSO": ("Lesotho", 2.7), "LBR": ("Liberia", 2.2),
    "LBY": ("Libya", 15.5), "LTU": ("Lithuania", 8.1),
    "LUX": ("Luxembourg", 15.3), "MDG": ("Madagascar", 0.5),
    "MWI": ("Malawi", 0.7), "MYS": ("Malaysia", 1.5),
    "MLI": ("Mali", 1.5), "MLT": ("Malta", 11.9),
    "MRT": ("Mauritania", 3.5), "MUS": ("Mauritius", 3.5),
    "MEX": ("Mexico", 16.8), "MDA": ("Moldova", 4.0),
    "MNG": ("Mongolia", 7.3), "MNE": ("Montenegro", 23.1),
    "MAR": ("Morocco", 5.1), "MOZ": ("Mozambique", 2.8),
    "MMR": ("Myanmar", 1.6), "NAM": ("Namibia", 5.6),
    "NPL": ("Nepal", 2.0), "NLD": ("Netherlands", 2.6),
    "NZL": ("New Zealand", 26.3), "NIC": ("Nicaragua", 6.7),
    "NER": ("Niger", 0.7), "NGA": ("Nigeria", 1.5),
    "NOR": ("Norway", 28.8), "OMN": ("Oman", 25.5),
    "PAK": ("Pakistan", 22.3), "PAN": ("Panama", 7.7),
    "PNG": ("Papua New Guinea", 3.9), "PRY": ("Paraguay", 17.0),
    "PER": ("Peru", 5.0), "PHL": ("Philippines", 3.6),
    "POL": ("Poland", 2.5), "PRT": ("Portugal", 8.5),
    "QAT": ("Qatar", 19.2), "ROU": ("Romania", 2.6),
    "RUS": ("Russia", 12.3), "RWA": ("Rwanda", 0.6),
    "SAU": ("Saudi Arabia", 19.3), "SEN": ("Senegal", 2.0),
    "SRB": ("Serbia", 39.1), "SLE": ("Sierra Leone", 0.6),
    "SGP": ("Singapore", 0.3), "SVK": ("Slovakia", 8.3),
    "SVN": ("Slovenia", 13.5), "SOM": ("Somalia", 9.1),
    "ZAF": ("South Africa", 9.7), "SSD": ("South Sudan", 1.5),
    "ESP": ("Spain", 7.5), "LKA": ("Sri Lanka", 1.5),
    "SDN": ("Sudan", 6.2), "SUR": ("Suriname", 4.8),
    "SWE": ("Sweden", 23.1), "CHE": ("Switzerland", 27.6),
    "SYR": ("Syria", 3.9), "TJK": ("Tajikistan", 1.4),
    "TZA": ("Tanzania", 1.4), "THA": ("Thailand", 15.1),
    "TLS": ("Timor-Leste", 5.5), "TGO": ("Togo", 1.6),
    "TTO": ("Trinidad and Tobago", 3.0),
    "TUN": ("Tunisia", 1.0), "TUR": ("Turkey", 12.5),
    "TKM": ("Turkmenistan", 3.8), "UGA": ("Uganda", 1.4),
    "UKR": ("Ukraine", 9.9), "ARE": ("United Arab Emirates", 22.1),
    "GBR": ("United Kingdom", 4.6),
    "USA": ("United States", 120.5), "URY": ("Uruguay", 34.7),
    "UZB": ("Uzbekistan", 1.7), "VEN": ("Venezuela", 18.5),
    "VNM": ("Vietnam", 1.6), "YEM": ("Yemen", 52.8),
    "ZMB": ("Zambia", 1.6), "ZWE": ("Zimbabwe", 2.8),
}

# Gun control strictness: custom ordinal scale 1-5
# 1=Very Permissive, 2=Permissive, 3=Moderate, 4=Strict, 5=Very Strict
#
# Ratings based on publicly available information from:
#   - GunPolicy.org (Sydney School of Public Health) country profiles
#   - Library of Congress "Firearms-Control Legislation and Policy" reports
#   - National legislation summaries
#
# Dimensions considered:
#   - Civilian firearm ownership: right vs privilege vs prohibited
#   - Licensing/permit requirements for purchase and possession
#   - Background check and waiting period requirements
#   - Restrictions on categories of firearms (handguns, semi-auto, full-auto)
#   - Carry laws (concealed/open carry permissions)
#   - Registration and record-keeping requirements
#
# This is a simplified composite — real regulatory environments are far more
# nuanced than a single ordinal value can capture.
#
# Format: code -> (name, strictness_level)
_GUN_CONTROL_STRICTNESS_FALLBACK = {
    "AFG": ("Afghanistan", 1), "ALB": ("Albania", 3),
    "DZA": ("Algeria", 4), "AGO": ("Angola", 3),
    "ARG": ("Argentina", 3), "ARM": ("Armenia", 3),
    "AUS": ("Australia", 4), "AUT": ("Austria", 3),
    "AZE": ("Azerbaijan", 4), "BHS": ("Bahamas", 3),
    "BHR": ("Bahrain", 4), "BGD": ("Bangladesh", 4),
    "BRB": ("Barbados", 3), "BLR": ("Belarus", 4),
    "BEL": ("Belgium", 3), "BLZ": ("Belize", 2),
    "BEN": ("Benin", 3), "BOL": ("Bolivia", 3),
    "BIH": ("Bosnia and Herzegovina", 3),
    "BWA": ("Botswana", 3), "BRA": ("Brazil", 3),
    "BGR": ("Bulgaria", 3), "BFA": ("Burkina Faso", 3),
    "BDI": ("Burundi", 4), "KHM": ("Cambodia", 4),
    "CMR": ("Cameroon", 3), "CAN": ("Canada", 3),
    "CAF": ("Central African Republic", 2),
    "TCD": ("Chad", 3), "CHL": ("Chile", 3),
    "CHN": ("China", 5), "COL": ("Colombia", 3),
    "COG": ("Congo", 3), "COD": ("DR Congo", 3),
    "CRI": ("Costa Rica", 3), "CIV": ("Cote d'Ivoire", 3),
    "HRV": ("Croatia", 3), "CUB": ("Cuba", 4),
    "CYP": ("Cyprus", 3), "CZE": ("Czech Republic", 2),
    "DNK": ("Denmark", 4), "DOM": ("Dominican Republic", 3),
    "ECU": ("Ecuador", 3), "EGY": ("Egypt", 4),
    "SLV": ("El Salvador", 3), "ERI": ("Eritrea", 5),
    "EST": ("Estonia", 3), "SWZ": ("Eswatini", 3),
    "ETH": ("Ethiopia", 4), "FJI": ("Fiji", 4),
    "FIN": ("Finland", 3), "FRA": ("France", 3),
    "GAB": ("Gabon", 3), "GMB": ("Gambia", 3),
    "GEO": ("Georgia", 3), "DEU": ("Germany", 3),
    "GHA": ("Ghana", 3), "GRC": ("Greece", 3),
    "GTM": ("Guatemala", 2), "GIN": ("Guinea", 3),
    "GNB": ("Guinea-Bissau", 3), "GUY": ("Guyana", 3),
    "HTI": ("Haiti", 2), "HND": ("Honduras", 2),
    "HUN": ("Hungary", 4), "ISL": ("Iceland", 3),
    "IND": ("India", 3), "IDN": ("Indonesia", 4),
    "IRN": ("Iran", 4), "IRQ": ("Iraq", 2),
    "IRL": ("Ireland", 4), "ISR": ("Israel", 3),
    "ITA": ("Italy", 3), "JAM": ("Jamaica", 4),
    "JPN": ("Japan", 5), "JOR": ("Jordan", 3),
    "KAZ": ("Kazakhstan", 3), "KEN": ("Kenya", 4),
    "KOR": ("South Korea", 4), "KWT": ("Kuwait", 3),
    "KGZ": ("Kyrgyzstan", 3), "LAO": ("Laos", 4),
    "LVA": ("Latvia", 3), "LBN": ("Lebanon", 2),
    "LSO": ("Lesotho", 3), "LBR": ("Liberia", 3),
    "LBY": ("Libya", 2), "LTU": ("Lithuania", 3),
    "LUX": ("Luxembourg", 4), "MDG": ("Madagascar", 3),
    "MWI": ("Malawi", 3), "MYS": ("Malaysia", 4),
    "MLI": ("Mali", 3), "MLT": ("Malta", 4),
    "MRT": ("Mauritania", 3), "MUS": ("Mauritius", 4),
    "MEX": ("Mexico", 3), "MDA": ("Moldova", 4),
    "MNG": ("Mongolia", 3), "MNE": ("Montenegro", 3),
    "MAR": ("Morocco", 4), "MOZ": ("Mozambique", 3),
    "MMR": ("Myanmar", 5), "NAM": ("Namibia", 3),
    "NPL": ("Nepal", 4), "NLD": ("Netherlands", 4),
    "NZL": ("New Zealand", 4), "NIC": ("Nicaragua", 3),
    "NER": ("Niger", 3), "NGA": ("Nigeria", 3),
    "NOR": ("Norway", 3), "OMN": ("Oman", 4),
    "PAK": ("Pakistan", 2), "PAN": ("Panama", 3),
    "PNG": ("Papua New Guinea", 3), "PRY": ("Paraguay", 2),
    "PER": ("Peru", 3), "PHL": ("Philippines", 3),
    "POL": ("Poland", 4), "PRT": ("Portugal", 3),
    "QAT": ("Qatar", 4), "ROU": ("Romania", 4),
    "RUS": ("Russia", 4), "RWA": ("Rwanda", 5),
    "SAU": ("Saudi Arabia", 3), "SEN": ("Senegal", 3),
    "SRB": ("Serbia", 2), "SLE": ("Sierra Leone", 3),
    "SGP": ("Singapore", 5), "SVK": ("Slovakia", 3),
    "SVN": ("Slovenia", 3), "SOM": ("Somalia", 1),
    "ZAF": ("South Africa", 3), "SSD": ("South Sudan", 2),
    "ESP": ("Spain", 3), "LKA": ("Sri Lanka", 4),
    "SDN": ("Sudan", 2), "SUR": ("Suriname", 2),
    "SWE": ("Sweden", 3), "CHE": ("Switzerland", 2),
    "SYR": ("Syria", 3), "TJK": ("Tajikistan", 4),
    "TZA": ("Tanzania", 4), "THA": ("Thailand", 3),
    "TLS": ("Timor-Leste", 4), "TGO": ("Togo", 3),
    "TTO": ("Trinidad and Tobago", 3),
    "TUN": ("Tunisia", 4), "TUR": ("Turkey", 3),
    "TKM": ("Turkmenistan", 5), "UGA": ("Uganda", 3),
    "UKR": ("Ukraine", 3), "ARE": ("United Arab Emirates", 4),
    "GBR": ("United Kingdom", 4),
    "USA": ("United States", 1), "URY": ("Uruguay", 3),
    "UZB": ("Uzbekistan", 4), "VEN": ("Venezuela", 3),
    "VNM": ("Vietnam", 5), "YEM": ("Yemen", 1),
    "ZMB": ("Zambia", 3), "ZWE": ("Zimbabwe", 3),
}
