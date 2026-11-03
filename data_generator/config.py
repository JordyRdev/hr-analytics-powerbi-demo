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

# National / International headcount targets by country: (date, headcount) anchors,
# interpolated linearly by month. Ukraine scales up during 2024, Niger closes in 2025.
NATIONAL_ANCHORS = {
    "Kenya":       [("2022-01", 105), ("2026-10", 130)],
    "Somalia":     [("2022-01", 115), ("2026-10", 140)],
    "South Sudan": [("2022-01", 110), ("2026-10", 120)],
    "DR Congo":    [("2022-01", 100), ("2026-10", 125)],
    "Nigeria":     [("2022-01", 85),  ("2026-10", 115)],
    "Niger":       [("2022-01", 75), ("2025-02", 95), ("2025-11", 0), ("2026-10", 0)],
    "Mali":        [("2022-01", 70),  ("2026-10", 75)],
    "Ukraine":     [("2022-01", 30), ("2023-12", 55), ("2024-12", 150), ("2026-10", 175)],
    "Syria":       [("2022-01", 90),  ("2026-10", 105)],
    "Iraq":        [("2022-01", 75),  ("2026-10", 70)],
    "Afghanistan": [("2022-01", 80),  ("2026-10", 85)],
    "Bangladesh":  [("2022-01", 55),  ("2026-10", 95)],
    "Haiti":       [("2022-01", 45),  ("2026-10", 65)],
    "Colombia":    [("2022-01", 40),  ("2026-10", 50)],
}
INTERNATIONAL_ANCHORS = {
    "Kenya":       [("2022-01", 24), ("2026-10", 34)],
    "Somalia":     [("2022-01", 32), ("2026-10", 40)],
    "South Sudan": [("2022-01", 30), ("2026-10", 38)],
    "DR Congo":    [("2022-01", 26), ("2026-10", 34)],
    "Nigeria":     [("2022-01", 18), ("2026-10", 28)],
    "Niger":       [("2022-01", 12), ("2025-02", 14), ("2025-11", 0), ("2026-10", 0)],
    "Mali":        [("2022-01", 16), ("2026-10", 20)],
    "Ukraine":     [("2022-01", 6), ("2023-12", 12), ("2024-12", 34), ("2026-10", 44)],
    "Syria":       [("2022-01", 22), ("2026-10", 28)],
    "Iraq":        [("2022-01", 18), ("2026-10", 20)],
    "Afghanistan": [("2022-01", 22), ("2026-10", 22)],
    "Bangladesh":  [("2022-01", 10), ("2026-10", 20)],
    "Haiti":       [("2022-01", 10), ("2026-10", 18)],
    "Colombia":    [("2022-01", 8),  ("2026-10", 14)],
}
HQ_ANCHORS = [("2022-01", 68), ("2026-10", 90)]

# Annual exit rates and their share of voluntary exits
ANNUAL_EXIT_RATE = {"National": 0.13, "International": 0.22, "HQ": 0.09}
MONTH_SEASONALITY = {1: 1.35, 2: 0.9, 3: 1.0, 4: 0.9, 5: 0.95, 6: 1.2, 7: 1.15,
                     8: 0.9, 9: 0.95, 10: 0.95, 11: 0.9, 12: 1.2}
MIN_TENURE_DAYS = 75

# Share of International field staff placed in a Global unit
GLOBAL_UNIT_SHARE = 0.125

GRADE_WEIGHTS = {
    "National": {"N1": 0.15, "N2": 0.30, "N3": 0.28, "N4": 0.18, "N5": 0.09},
    "International": {"G1": 0.04, "G2": 0.12, "G3": 0.30, "G4": 0.29, "G5": 0.17, "G6": 0.08},
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
