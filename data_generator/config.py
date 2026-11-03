"""Settings for the synthetic MFR data set. Everything is seeded: same seed, same files."""
from datetime import date
from pathlib import Path

SEED = 2026

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

START = date(2022, 1, 1)          # first month of history
CUTOVER = date(2024, 12, 31)      # last month-end taken from the legacy files
EXPORT_DATE = date(2026, 10, 31)  # data is complete up to this date
SIM_END = date(2027, 2, 28)       # hires after the export date are simulated so that
                                  # vacancies still open at the export date exist

HQ_COUNTRY = "Switzerland"

# National / International headcount targets by country: (month, headcount) anchors,
# interpolated linearly by month. South Sudan scales up during 2024, Afghanistan closes in 2025.
CLOSING_COUNTRY = "Afghanistan"
SCALING_COUNTRY = "South Sudan"
NATIONAL_ANCHORS = {
    "Kenya":       [("2022-01", 85), ("2026-10", 105)],
    "South Sudan": [("2022-01", 70), ("2023-12", 80), ("2024-12", 160), ("2026-10", 175)],
    "DR Congo":    [("2022-01", 80), ("2026-10", 105)],
    "Nigeria":     [("2022-01", 65), ("2026-10", 95)],
    "Ukraine":     [("2022-01", 60), ("2026-10", 100)],
    "Syria":       [("2022-01", 70), ("2026-10", 90)],
    "Afghanistan": [("2022-01", 85), ("2025-02", 90), ("2025-11", 0), ("2026-10", 0)],
    "Bangladesh":  [("2022-01", 45), ("2026-10", 80)],
}
INTERNATIONAL_ANCHORS = {
    "Kenya":       [("2022-01", 18), ("2026-10", 26)],
    "South Sudan": [("2022-01", 24), ("2023-12", 28), ("2024-12", 40), ("2026-10", 44)],
    "DR Congo":    [("2022-01", 20), ("2026-10", 28)],
    "Nigeria":     [("2022-01", 14), ("2026-10", 22)],
    "Ukraine":     [("2022-01", 20), ("2026-10", 30)],
    "Syria":       [("2022-01", 18), ("2026-10", 26)],
    "Afghanistan": [("2022-01", 18), ("2025-02", 16), ("2025-11", 0), ("2026-10", 0)],
    "Bangladesh":  [("2022-01", 10), ("2026-10", 20)],
}
HQ_ANCHORS = [("2022-01", 40), ("2026-10", 50)]

# Annual exit rates and their share of voluntary exits
ANNUAL_EXIT_RATE = {"National": 0.13, "International": 0.22, "HQ": 0.09}
MONTH_SEASONALITY = {1: 1.35, 2: 0.9, 3: 1.0, 4: 0.9, 5: 0.95, 6: 1.2, 7: 1.15,
                     8: 0.9, 9: 0.95, 10: 0.95, 11: 0.9, 12: 1.2}
MIN_TENURE_DAYS = 75

# Share of International field staff placed in a Global unit
GLOBAL_UNIT_SHARE = 0.125

GRADE_WEIGHTS = {
    "National": {"N1": 0.15, "N2": 0.30, "N3": 0.28, "N4": 0.18, "N5": 0.09},
    "International": {"G1": 0.06, "G2": 0.12, "G3": 0.29, "G4": 0.28, "G5": 0.17, "G6": 0.08},
}
GENDER_FEMALE_SHARE = {"National": 0.38, "International": 0.46, "HQ": 0.58}
AGE_MEAN_SD = {"National": (35.5, 8.0), "International": (38.5, 8.0), "HQ": (41.0, 8.5)}

# Probability that an International hire has a Global South nationality, by hire year.
# Rises slowly: the diversity story on page 3.
GS_SHARE_BY_YEAR = {2021: 0.33, 2022: 0.36, 2023: 0.40, 2024: 0.44, 2025: 0.48, 2026: 0.52, 2027: 0.53}
GS_SHARE_HQ = 0.2

# Planted problem volumes (see quality_issues.py)
DUPLICATES_TRACKER_CORE = 30
MISSING_DOB_SHARE = 0.02
MISSING_NATIONALITY_SHARE = 0.01
OVERLAP_MISSING_SHARE = 0.012     # historical rows dropped in Dec 2024 / Jan 2025
OVERLAP_STALE_ROWS = 14           # leavers still listed in the historical file
JIRA_RESOLVED_BEFORE_CREATED = 9
JIRA_REOPENED = 22
MISLABEL_CORE = 12
MISLABEL_HIST_STAFF = 24
CONTRACT_END_BEFORE_START = 11
MIGRATED_VACANCIES = 38
