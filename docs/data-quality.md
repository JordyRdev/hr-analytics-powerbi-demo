# Data quality

The data is synthetic. Problems were planted on purpose, with fixed counts, so the model's handling can be checked. `tests/planted_issues.csv` holds the counts written when the data was built; `tests/test_generated_data.py` checks that each problem is present. `DQ_Issues` in the model lists the individual records. Counts in the model can be a little lower than the planted counts where a planted person never appears at a month-end.

## Planted problems

| Problem | Source | Planted | What the model does | DQ check |
|---|---|---|---|---|
| Country spelling variants (DRC, Congo, Dem. Rep., trailing spaces) | All sources | 2814 cells, plus the DRC tracker file name | Mapped to the standard name through `Variants` in `country_list.xlsx` | Country spelling variant |
| Staff ID held by CORE and by a tracker | CORE and trackers | 30 IDs (10 with a different grade) | CORE row wins | Duplicate staff ID |
| Legacy and CORE both report Dec 2024 and Jan 2025 | Legacy snapshots | Dec 2024 and Jan 2025: staff missing from the legacy file, leavers still listed | Legacy used to Dec 2024, CORE from Jan 2025. Both kept in `Recon_Overlap` | Overlap month mismatch |
| Missing date of birth | All | 36 staff | Age blank, excluded from averages | Missing date of birth |
| Missing nationality | All | 18 staff | Shown as Unknown, excluded from GS/GN measures | Missing nationality |
| JIRA ticket resolved before created | JIRA | 9 tickets | Closed on creation date, excluded from duration | Resolved before created |
| JIRA ticket reopened | JIRA | 27 tickets | Latest resolution date used; open if currently reopened | Reopened ticket |
| National grade labelled International or Expat | CORE, legacy snapshots | 12 CORE staff, 24 legacy staff | Grade decides Staff Type | Category label vs grade |
| Contract end before start | CORE contracts | 11 contracts | End rebuilt from granted months | Contract end before start |
| Vacancy open in the legacy log, never re-created in JIRA | Legacy vacancy log | 6 vacancies | Stays open in the model, so it inflates open vacancies until HR closes it | Legacy vacancy not migrated |
| Dates stored as text | 2022 snapshot file, layout B trackers | 9211 snapshot rows, 216 tracker rows | Parsed as dd/mm/yyyy | none (handled in Power Query) |

Overlap detail: December 2024 has 29 staff missing from the legacy file and 28 leavers still listed. January 2025 shows the same pattern with different missing staff.

Source files are always read-only. Nothing is corrected in place; a corrected value exists only in the model, and the original is listed in `DQ_Issues`.

## Expected DQ_Issues counts

From `tests/expected_kpis.csv`, computed in pandas from the files:

| Check | Expected rows |
|---|---|
| Duplicate staff ID | 30 |
| Contract end before start | 11 |
| Resolved before created | 9 |
| Missing date of birth | 36 |
| Missing nationality | 18 |
| Category label vs grade | 36 |
| Overlap month mismatch | 58 |
| Legacy vacancy not migrated | 6 |
| Country spelling variant | 2754 |

`Reopened ticket` is not in the table above; it should show the planted count of 27.

## Known limitations not fixed

- Tracker rows carry only the current grade and contract type. National staff therefore show their latest grade for every month from January 2025.
- Internal mobility is not modelled in the staff tables: a vacancy closed as Internal Mobility is followed by a new staff record, not by a change to an existing one.
- Surge requests raised in late 2024 and filled in 2025 have no fill date, because the legacy log was closed in December 2024 and surges were not migrated.
- Appraisal history starts in January 2024, so completion cannot be shown before January 2025.
- Expatriates are counted from the monthly snapshots. The deployment log adds people whose nationality is missing in the snapshots; page 9 shows the difference.
- The GN/GS classification is an illustrative mapping in a reference file. HR should own and review it.
- Legacy vacancies have no `time_to_done_hours`, so the scatter on page 5 covers JIRA tickets only.
