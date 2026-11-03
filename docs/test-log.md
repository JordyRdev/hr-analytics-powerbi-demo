# Test log

Reference values come from `tests/expected_kpis.csv` (computed in pandas from the source files). The Actual and Result columns are filled in during the Power BI build.
Validation DAX for the KPI rows is in `tests/validation_queries.dax`.

| # | Page | Visual | Filter or setting | Expected | Actual | Result |
|---|---|---|---|---|---|---|
| 1 | 1 Workforce Overview | Headcount card | Reporting date 31 Oct 2026 | 989 | | |
| 2 | 1 Workforce Overview | Global card | 31 Oct 2026 | 73 | | |
| 3 | 1 Workforce Overview | National card | 31 Oct 2026 | 743 | | |
| 4 | 1 Workforce Overview | HQ card | 31 Oct 2026 | 50 | | |
| 5 | 1 Workforce Overview | Workforce evolution | None | Total headcount rises from 746 in Jan 2022 to 989 in Oct 2026; South Sudan step-up through 2024, Afghanistan gone by Nov 2025 | | |
| 6 | 2 Global & International | Headcount PY card | 31 Oct 2026 | 953 | | |
| 7 | 2 Global & International | Average age card | 31 Oct 2026 | 39.5583 | | |
| 8 | 2 Global & International | Average age card | Population = International | 40.6547 | | |
| 9 | 3 Diversity | GS share card | 31 Oct 2026 (page filter Staff Type = International) | 0.4444 | | |
| 10 | 3 Diversity | GS/GN ratio card | 31 Oct 2026 | 0.8 | | |
| 11 | 3 Diversity | GS share over time | None | Line rises between Jan 2022 and Oct 2026 | | |
| 12 | 3 Diversity | Nationality ranking | GN/GS = GS | Only GS nationalities listed | | |
| 13 | 3 Diversity | Expatriates card | 31 Oct 2026 | 187 | | |
| 14 | 4 Staffing & Vacancies | Retention rate card | 31 Oct 2026 | 0.8342 | | |
| 15 | 4 Staffing & Vacancies | Vacancy rate card | 31 Oct 2026 | 0.037 | | |
| 16 | 4 Staffing & Vacancies | Due-vacancy rate card | 31 Oct 2026 | 0.0166 | | |
| 17 | 4 Staffing & Vacancies | Open vacancies card | 31 Oct 2026 | 38 | | |
| 18 | 4 Staffing & Vacancies | Vacancy rate card | Country = South Sudan | 0.0395 | | |
| 19 | 5 Recruitment Duration | Avg days to close | 31 Oct 2026 | 90.4829 | | |
| 20 | 5 Recruitment Duration | Avg time_to_done (days) | 31 Oct 2026 | 1.1614 | | |
| 21 | 5 Recruitment Duration | Breakdown bar | Break down by = Grade | One bar per grade with data; values agree with the card when no breakdown is applied | | |
| 22 | 6 Surge Deployments | Requests card | 31 Oct 2026 | 76 | | |
| 23 | 6 Surge Deployments | National share card | 31 Oct 2026 | 0.5397 | | |
| 24 | 7 Retention & Turnover | Turnover rate card | 31 Oct 2026 | 0.1764 | | |
| 25 | 7 Retention & Turnover | Voluntary turnover card | 31 Oct 2026 | 0.0598 | | |
| 26 | 7 Retention & Turnover | Appraisal completion card | 31 Oct 2026 | 0.7911 | | |
| 27 | 8 Contracts | Avg current duration G3/G4 | 31 Oct 2026 | 16.3596 | | |
| 28 | 8 Contracts | New joiner duration G3/G4 | 31 Oct 2026 | 11.7143 | | |
| 29 | 8 Contracts | Ending within 4 months | 31 Oct 2026 | 68 | | |
| 30 | 8 Contracts | Detail table | 31 Oct 2026 | Rows equal the card above; days remaining between 2 and 119; nearest dates shaded | | |
| 31 | 9 Data Quality | Issues by check | None | Duplicate staff ID = 30; Contract end before start = 11; Resolved before created = 9 | | |
| 32 | 9 Data Quality | Overlap table | None | Two rows (Dec 2024, Jan 2025) with a non-zero difference | | |
| 33 | All pages | Reporting Date slicer | Select 31 Oct 2025 | Headcount card on page 1 shows 953 | | |
| 34 | Filters | Country filter consistency | Country = Kenya on pages 1, 2, 3, 7 | Headcount card equals 128 on pages 1 and 2 (page 3 shows International staff only) | | |
| 35 | Filters | Slicer sync | Choose Country = Syria on page 1, open pages 2, 3, 4, 7, 8 | Country slicer still shows Syria and visuals are filtered | | |
| 36 | Filters | Slicer not on page | Choose Gender = Female on page 1, open page 4 | Page 4 is unaffected (no Gender slicer there) | | |
| 37 | Filters | Staff Type filter on vacancies | Staff Type = International on page 4 | Vacancy rate card shows 0.0428 | | |
