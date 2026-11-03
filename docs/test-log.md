# Test log

Run on 3 November 2026 in Power BI Desktop against the data built with seed 2026 (reporting date 31 Oct 2026).
Reference values come from `tests/expected_kpis.csv`, computed in pandas from the source files.

## Summary

- **Model validation:** 46 of 46 KPI queries in `tests/validation_summary.dax` returned the expected value within tolerance. The largest absolute difference was below 0.000001. Counts matched exactly.
- **Report checks:** values read from the rendered pages on 3 Nov 2026. Cases marked Not run have not been exercised by hand yet.
- Defects found while testing were fixed before this log was written. They are listed at the end.

## Report cases

| # | Page | Visual | Filter or setting | Expected | Actual | Result |
|---|---|---|---|---|---|---|
| 1 | 1 Workforce Overview | Headcount card | Reporting date 31 Oct 2026 | 989 | 989 | Pass |
| 2 | 1 Workforce Overview | Global card | 31 Oct 2026 | 73 | 73 | Pass |
| 3 | 1 Workforce Overview | National card | 31 Oct 2026 | 743 | 743 | Pass |
| 4 | 1 Workforce Overview | HQ card | 31 Oct 2026 | 50 | 50 | Pass |
| 5 | 1 Workforce Overview | Workforce evolution | None | Rises from about 750 in 2022-Q1 to about 1,000; small dip in late 2025 (Afghanistan closure) | About 750 in 2022-Q1, about 1,000 from 2024-Q4, slight dip in 2025-Q3 and Q4, back to about 1,000 in 2026 | Pass |
| 6 | 2 Global & International | Headcount 1 year earlier card | 31 Oct 2026 | 953 | 953 (change +36, +3.8%) | Pass |
| 7 | 2 Global & International | Average age card | 31 Oct 2026 | 39.6 | 39.6 | Pass |
| 8 | 2 Global & International | Average age | Population = International | 40.7 | 40.6547 in DAX query row 12; slicer not clicked | Pass (DAX) |
| 9 | 3 Diversity | GS share card | 31 Oct 2026, page filter Staff Type = International | 44.4% | 44.4% | Pass |
| 10 | 3 Diversity | GS/GN ratio card | 31 Oct 2026 | 0.80 | 0.80 | Pass |
| 11 | 3 Diversity | GS share over time | None | Higher at the end than at the start (31.8% in 2022-Q1, 44.4% in 2026-Q4) | Line visible, ends higher than it starts | Pass |
| 12 | 3 Diversity | Nationality ranking | GN/GS = GS | Only GS nationalities listed | Slicer not exercised | Not run |
| 13 | 3 Diversity | Expatriates card | 31 Oct 2026 | 187 | 187 | Pass |
| 14 | 4 Staffing & Vacancies | Retention rate card | 31 Oct 2026 | 83.4% | 83.4% | Pass |
| 15 | 4 Staffing & Vacancies | Vacancy rate card | 31 Oct 2026 | 3.7% | 3.7% | Pass |
| 16 | 4 Staffing & Vacancies | Due-vacancy rate card | 31 Oct 2026 | 1.7% | 1.7% | Pass |
| 17 | 4 Staffing & Vacancies | Open vacancies card | 31 Oct 2026 | 38 | 38 | Pass |
| 18 | 4 Staffing & Vacancies | Vacancy rate | Country = South Sudan | 3.9% | 0.039474 in DAX query row 19; slicer not clicked | Pass (DAX) |
| 19 | 5 Recruitment Duration | Avg days to close | 31 Oct 2026 | 90.5 | 90.5 | Pass |
| 20 | 5 Recruitment Duration | Avg JIRA time_to_done (days) | 31 Oct 2026 | 1.2 | 1.2 | Pass |
| 21 | 5 Recruitment Duration | Breakdown bar | Break down by = Grade | One bar per grade | Default view (Country) shows one bar per country; Grade not selected | Partial |
| 22 | 6 Surge Deployments | Requests card | 31 Oct 2026 | 76 | 76 | Pass |
| 23 | 6 Surge Deployments | National share card | 31 Oct 2026 | 54.0% | 54.0% | Pass |
| 24 | 7 Retention & Turnover | Turnover rate card | 31 Oct 2026 | 17.6% | 17.6% | Pass |
| 25 | 7 Retention & Turnover | Voluntary turnover card | 31 Oct 2026 | 6.0% | 6.0% | Pass |
| 26 | 7 Retention & Turnover | Appraisal completion card | 31 Oct 2026 | 79.1% | 79.1% | Pass |
| 27 | 8 Contracts | Avg current duration G3/G4 | 31 Oct 2026 | 16.4 | 16.4 | Pass |
| 28 | 8 Contracts | New joiner duration G3/G4 | 31 Oct 2026 | 11.7 | 11.7 | Pass |
| 29 | 8 Contracts | Ending within 4 months | 31 Oct 2026 | 68 | 68 | Pass |
| 30 | 8 Contracts | Detail table | 31 Oct 2026 | Only contracts ending within 4 months, nearest first, shaded | First rows end 2 to 18 days after the reporting date, shaded; full row count not checked | Pass |
| 31 | 9 Data Quality | Issues by check | None | Duplicate staff ID 30; Contract end before start 11; Resolved before created 9 | Chart shows all checks; the three counts verified in DAX query rows 38 to 40 | Pass (DAX) |
| 32 | 9 Data Quality | Overlap table | None | Two rows (Dec 2024, Jan 2025) with a non-zero difference | 2024-12-31: 995 vs 994 (+1); 2025-01-31: 996 vs 997 (-1) | Pass |
| 33 | All pages | Reporting Date slicer | Select 31 Oct 2025 | Headcount card on page 1 shows 953 | Value 953 verified in DAX query row 8; slicer not clicked | Pass (DAX) |
| 34 | Filters | Country filter consistency | Country = Kenya on pages 1, 2, 3, 7 | Headcount 128 on pages 1 and 2 | Value 128 verified in DAX query row 6; slicer not clicked | Pass (DAX) |
| 35 | Filters | Slicer sync | Choose Country = Syria on page 1, open pages 2, 3, 4, 7, 8 | Slicer still shows Syria; visuals filtered | Not exercised | Not run |
| 36 | Filters | Slicer not on page | Choose Gender = Female on page 1, open page 4 | Page 4 unaffected | Not exercised | Not run |
| 37 | Filters | Staff Type filter on vacancies | Staff Type = International on page 4 | Vacancy rate 4.3% | 0.042802 in DAX query row 20; slicer not clicked | Pass (DAX) |

Cases marked Not run or Partial are the interaction tests (slicer sync, slicer selection). Run them by hand before a demo.

## Model validation: all 46 KPI queries

Query: `tests/validation_summary.dax`, run in DAX query view. Column `ok` was `true` in every row.

| # | KPI | Filter | Date | Expected | Tolerance | Result |
|---|---|---|---|---|---|---|
| 1 | Headcount | none | 2026-10-31 | 989 | 0 | Pass |
| 2 | Headcount | Population=National | 2026-10-31 | 743 | 0 | Pass |
| 3 | Headcount | Population=International | 2026-10-31 | 173 | 0 | Pass |
| 4 | Headcount | Population=Global | 2026-10-31 | 73 | 0 | Pass |
| 5 | Headcount | Population Detail=Global - HQ | 2026-10-31 | 50 | 0 | Pass |
| 6 | Headcount | Country=Kenya | 2026-10-31 | 128 | 0 | Pass |
| 7 | Headcount | Country=Ukraine | 2026-10-31 | 129 | 0 | Pass |
| 8 | Headcount | none | 2025-10-31 | 953 | 0 | Pass |
| 9 | Headcount | Country=Ukraine | 2025-10-31 | 121 | 0 | Pass |
| 10 | Female Share | none | 2026-10-31 | 0.427705 | 0.0001 | Pass |
| 11 | Average Age | none | 2026-10-31 | 39.558255 | 0.01 | Pass |
| 12 | Average Age | Population=International | 2026-10-31 | 40.654697 | 0.01 | Pass |
| 13 | GS Share | Staff Type=International | 2026-10-31 | 0.444444 | 0.0001 | Pass |
| 14 | GS/GN Ratio | Staff Type=International | 2026-10-31 | 0.8 | 0.0001 | Pass |
| 15 | GS Share | Staff Type=International | 2025-10-31 | 0.421053 | 0.0001 | Pass |
| 16 | Expatriates | none | 2026-10-31 | 187 | 0 | Pass |
| 17 | Open Vacancies | none | 2026-10-31 | 38 | 0 | Pass |
| 18 | Vacancy Rate | none | 2026-10-31 | 0.037001 | 0.0001 | Pass |
| 19 | Vacancy Rate | Country=South Sudan | 2026-10-31 | 0.039474 | 0.0001 | Pass |
| 20 | Vacancy Rate | Staff Type=International | 2026-10-31 | 0.042802 | 0.0001 | Pass |
| 21 | Due Vacancy Rate | none | 2026-10-31 | 0.016553 | 0.0001 | Pass |
| 22 | Avg Planned Duration (months) | none | 2026-10-31 | 15.373134 | 0.01 | Pass |
| 23 | Vacancies Opened (12m) | none | 2026-10-31 | 201 | 0 | Pass |
| 24 | Avg Days to Close | none | 2026-10-31 | 90.482927 | 0.01 | Pass |
| 25 | Avg Time to Done (days) | none | 2026-10-31 | 1.161423 | 0.01 | Pass |
| 26 | Retention Rate (12m) | none | 2026-10-31 | 0.834208 | 0.0001 | Pass |
| 27 | Retention Rate (12m) | none | 2025-10-31 | 0.756423 | 0.0001 | Pass |
| 28 | Exits (12m) | none | 2026-10-31 | 171 | 0 | Pass |
| 29 | Turnover Rate (12m) | none | 2026-10-31 | 0.17641 | 0.0001 | Pass |
| 30 | Voluntary Turnover Rate (12m) | none | 2026-10-31 | 0.059835 | 0.0001 | Pass |
| 31 | Appraisal Completion | none | 2026-10-31 | 0.791111 | 0.0001 | Pass |
| 32 | Avg Current Contract Duration G3/G4 (months) | none | 2026-10-31 | 16.359649 | 0.01 | Pass |
| 33 | Avg Granted Duration New Joiners G3/G4 (months) | none | 2026-10-31 | 11.714286 | 0.01 | Pass |
| 34 | Contracts Ending Within 4 Months | none | 2026-10-31 | 68 | 0 | Pass |
| 35 | Contracts Ending Within 4 Months % | none | 2026-10-31 | 0.276423 | 0.0001 | Pass |
| 36 | Surge Requests (12m) | none | 2026-10-31 | 76 | 0 | Pass |
| 37 | Surge National Share (12m) | none | 2026-10-31 | 0.539683 | 0.0001 | Pass |
| 38 | DQ Issues: Duplicate staff ID | none | 2026-10-31 | 30 | 0 | Pass |
| 39 | DQ Issues: Contract end before start | none | 2026-10-31 | 11 | 0 | Pass |
| 40 | DQ Issues: Resolved before created | none | 2026-10-31 | 9 | 0 | Pass |
| 41 | DQ Issues: Missing date of birth | none | 2026-10-31 | 36 | 0 | Pass |
| 42 | DQ Issues: Missing nationality | none | 2026-10-31 | 18 | 0 | Pass |
| 43 | DQ Issues: Category label vs grade | none | 2026-10-31 | 36 | 0 | Pass |
| 44 | DQ Issues: Overlap month mismatch | none | 2026-10-31 | 58 | 0 | Pass |
| 45 | DQ Issues: Legacy vacancy not migrated | none | 2026-10-31 | 6 | 0 | Pass |
| 46 | DQ Issues: Country spelling variant | none | 2026-10-31 | 2754 | 0 | Pass |

## Defects found and fixed during testing

- Tracker and legacy files with real Excel dates loaded as blank dates, which removed National staff and 2022 to 2024 history. Date parsing now handles Excel serial numbers.
- `Average Headcount (12m)` filtered one table by a column of another. Rewritten with a variable.
- Two queries failed on load (a column added twice, a column dropped when files were combined).
- `Days Remaining` listed every contract. It now returns a value only for International contracts ending within 4 months.
- The Surge national share card was blank on the Diversity page because the page filter removed National grades. A measure without that filter is used.
- Blank date slot appeared on month axes because some measures returned 0. They now return blank when no date applies.
- Years displayed with a thousands separator. Fixed.
- 58 monthly points did not fit without a scrollbar. Time axes now show quarter-ends.
- Map visuals are disabled by some tenant settings. The map was replaced with a column chart.
