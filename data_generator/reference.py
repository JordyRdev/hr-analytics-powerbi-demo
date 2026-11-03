"""Reference lists: countries, nationalities with GN/GS flag, grades, units, legacy labels."""
from config import HQ_COUNTRY

# canonical name, ISO3, region, office status
COUNTRIES = [
    ("Kenya", "KEN", "East Africa", "Active"),
    ("Somalia", "SOM", "East Africa", "Active"),
    ("South Sudan", "SSD", "East Africa", "Active"),
    ("DR Congo", "COD", "Central Africa", "Active"),
    ("Nigeria", "NGA", "West Africa", "Active"),
    ("Niger", "NER", "West Africa", "Closed 2025"),
    ("Mali", "MLI", "West Africa", "Active"),
    ("Ukraine", "UKR", "Eastern Europe", "Active"),
    ("Syria", "SYR", "Middle East", "Active"),
    ("Iraq", "IRQ", "Middle East", "Active"),
    ("Afghanistan", "AFG", "South Asia", "Active"),
    ("Bangladesh", "BGD", "South Asia", "Active"),
    ("Haiti", "HTI", "Americas", "Active"),
    ("Colombia", "COL", "Americas", "Active"),
    (HQ_COUNTRY, "CHE", "Europe", "HQ"),
]
FIELD_COUNTRIES = [c[0] for c in COUNTRIES if c[0] != HQ_COUNTRY]

# spelling variants found in the sources -> canonical
COUNTRY_VARIANTS = {
    "DR Congo": ["DRC", "Congo, Dem. Rep.", "Democratic Republic of the Congo", "D.R. Congo"],
    "South Sudan": ["S. Sudan", "South-Sudan"],
    "Syria": ["Syrian Arab Republic"],
    "Afghanistan": ["Afghanistan "],
    "Bangladesh": ["Bangladesh (Dhaka)"],
    "Ukraine": ["Ukraine - Kyiv"],
    "Switzerland": ["Geneva HQ", "CH"],
    "Haiti": ["Haiti "],
}

# Nationality -> GN / GS (illustrative classification, owned by HR and editable in the file)
GN = ["Switzerland", "United Kingdom", "France", "Germany", "Netherlands", "Belgium", "Italy", "Spain",
      "Sweden", "Norway", "Denmark", "Ireland", "Canada", "United States", "Australia", "Japan", "Finland"]
GS = ["Kenya", "Somalia", "South Sudan", "DR Congo", "Nigeria", "Niger", "Mali", "Ukraine", "Syria", "Iraq",
      "Afghanistan", "Bangladesh", "Haiti", "Colombia", "India", "Pakistan", "Philippines", "Uganda",
      "Ethiopia", "Lebanon", "Jordan", "Brazil", "Senegal"]
NATIONALITIES = [(n, "GN") for n in GN] + [(n, "GS") for n in GS]
GN_WEIGHTS = [3, 5, 6, 5, 3, 3, 3, 3, 2, 2, 1, 1, 3, 4, 2, 1, 1]
GS_COMMON = ["India", "Pakistan", "Philippines", "Uganda", "Ethiopia", "Lebanon", "Jordan", "Brazil", "Senegal"]

GRADES = [
    ("N1", "National", "Support", 1), ("N2", "National", "Support", 2),
    ("N3", "National", "Professional", 3), ("N4", "National", "Professional", 4),
    ("N5", "National", "Management", 5),
    ("G1", "International", "Support", 6), ("G2", "International", "Support", 7),
    ("G3", "International", "Professional", 8), ("G4", "International", "Professional", 9),
    ("G5", "International", "Management", 10), ("G6", "International", "Management", 11),
]
CONTRACT_TYPES = [("Fixed-term", 1, True), ("Short-term", 2, True), ("Consultancy", 3, True), ("Open-ended", 4, False)]

# unit, scope
COUNTRY_UNITS = ["Programmes", "Research & Assessment", "Finance & Admin", "Human Resources",
                 "Logistics & Supply", "Security", "Data & IT"]
COUNTRY_UNIT_WEIGHTS = [0.34, 0.2, 0.12, 0.06, 0.14, 0.06, 0.08]
GLOBAL_UNITS = ["Global Research Unit", "Global Support Unit"]
HQ_UNITS = ["Executive Office", "Finance & Legal", "People & Culture", "Communications",
            "Global Research Unit", "Global Support Unit"]
HQ_UNIT_WEIGHTS = [0.06, 0.16, 0.12, 0.1, 0.32, 0.24]

LEGACY_LABELS = [("Expat", "International"), ("HQ-based", "International"), ("HQ", "International"), ("Local", "National"),
                 ("National", "National"), ("International", "International")]

EXIT_REASONS = [
    # reason, voluntary, weight (National), weight (International)
    ("Resignation", "Y", 0.34, 0.34),
    ("Retirement", "Y", 0.03, 0.03),
    ("Personal reasons", "Y", 0.10, 0.12),
    ("End of contract", "N", 0.28, 0.18),
    ("End of project funding", "N", 0.17, 0.25),
    ("Dismissal", "N", 0.03, 0.02),
    ("Redundancy", "N", 0.05, 0.06),
]
# labels used by the legacy files for the same reasons
LEGACY_EXIT_LABELS = {"Resignation": "Resigned", "Retirement": "Retired", "Personal reasons": "Personal",
                      "End of contract": "Contract ended", "End of project funding": "Project ended",
                      "Dismissal": "Dismissed", "Redundancy": "Redundancy", "Office closure": "Closure"}

SURGE_COUNTRY_WEIGHTS = {"Ukraine": 18, "Syria": 12, "Somalia": 12, "Haiti": 10, "Bangladesh": 9, "South Sudan": 9,
                         "DR Congo": 8, "Afghanistan": 6, "Iraq": 5, "Nigeria": 5, "Kenya": 4, "Mali": 4,
                         "Colombia": 3, "Niger": 2}
