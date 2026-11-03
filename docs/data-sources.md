# Data sources

All files are in `data/`. They are synthetic and pseudonymised: staff are identified by `EMP-nnnnnn` only. The owners below are fictional roles.
The model reads the folder named by the `DataFolder` parameter.

| Source | Files | Simulated owner | Refresh | Covers |
|---|---|---|---|---|
| CORE staff export | `core_hris/core_staff_export.csv` | People & Culture systems | Monthly extract | International and HQ staff, plus 30 national staff loaded early, active since Jan 2025 |
| CORE contracts | `core_hris/core_contracts_export.csv` | People & Culture systems | Monthly | Contract history from Jan 2025 |
| CORE appraisals | `core_hris/core_appraisals_export.csv` | People & Culture systems | Monthly | All appraisals since Jan 2024, all staff |
| JIRA recruitment board | `jira/jira_recruitment_export.csv` | Talent Acquisition | Monthly | Vacancy and Surge tickets created since Jan 2025, plus vacancies migrated from the legacy log |
| Country trackers | `country_trackers/NS_tracker_<Country>.xlsx` | Country HR focal points | Monthly, by email | National staff active since Jan 2025 |
| Legacy snapshots | `historical/Staff_Snapshots_2022.xlsx` ... `2024`, `2025_Jan` | People & Culture (retired system) | Frozen | Month-end staff lists, Jan 2022 to Jan 2025 |
| Legacy logs | `historical/Vacancy_Log_2022_2024.xlsx`, `Surge_Log_2022_2024.xlsx`, `Expatriation_Log_2022_2024.xlsx`, `Leavers_Log_2022_2024.xlsx` | People & Culture (retired system) | Frozen | Events before 2025 |
| Reference tables | `reference/*.xlsx` | People & Culture analytics | When rules change | Category mapping, GN/GS, countries with spelling variants, tracker column aliases, vacancy labels |

## Dependencies

- Trackers depend on `reference/tracker_column_map.xlsx`: a new header spelling needs a new alias row.
- Every source depends on `reference/country_list.xlsx` for country names.
- Staff Type and Population depend on `reference/staff_category_mapping.xlsx` (grade scale, unit scope, legacy labels).
- Vacancies in JIRA that were migrated from the legacy log depend on the `legacy_vacancy_ref` field being filled in.

## Source notes

**CORE staff export.** One row per person. Fields: ID, date of birth, gender, nationality, staff category label, contract type, grade, duty country, team, start and end date, exit reason, voluntary flag, last appraisal date.
The category label is free text and is not trusted; grade decides.

**CORE contracts.** One row per contract: type, grade, duty country, team, start, end (blank for open-ended), granted months.

**JIRA.** `issue_type` is Vacancy or Surge. Dates carry a time of day. `time_to_done_hours` is the time in the final workflow stage only.
Status values: Open, In Progress, Reopened, Done, Cancelled.

**Country trackers.** One workbook per country. Header row, column names and sheet names differ by country; some carry a title block above the header and a total row below.
Layouts A to D are listed in `data_generator/sources.py`. Country comes from the file name. Dates are real Excel dates in some files and dd/mm/yyyy text in others.

**Legacy snapshots.** One sheet, `Snapshot`, with one row per person per month-end. Old labels: Expat, Local, HQ-based for category; Fixed Term, Short Term, Consultant, Permanent for contract; F, M, X for sex.

## Known limits

- Trackers hold current values only (no grade history).
- Legacy files have no appraisal data.
- The legacy log closed in December 2024; anything still open then was meant to be re-created in JIRA (6 vacancies were not).
- The first CORE extract covers staff active on or after 1 January 2025, so people who left earlier exist only in the legacy files.
