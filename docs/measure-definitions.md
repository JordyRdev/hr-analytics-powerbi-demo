# Measure definitions (draft, definitions only)

Final DAX is added once the model is written. Every measure reads a single reporting date. The report has one
`Reporting Date` slicer (month-ends). Charts with a date axis override it with the month on the axis.

| KPI | Numerator | Denominator | Date logic |
|---|---|---|---|
| Headcount | Distinct staff IDs present at the month-end | none | Snapshot at reporting date |
| Headcount vs 1 year earlier | Headcount at date minus headcount at date - 12 months | Headcount at date - 12 months (for %) | Month-end 12 months before |
| Average age | Mean age in years of staff present, age taken at the month-end | none | Snapshot |
| GS share | Staff with GS nationality | Staff with GS or GN nationality (unknown excluded) | Snapshot |
| GS/GN ratio | GS staff | GN staff | Snapshot |
| Expatriates | International field staff whose nationality differs from duty country | none | Snapshot |
| Vacancy rate | Vacancies open at month-end | Filled positions + open vacancies | Snapshot |
| Due-vacancy rate | Open vacancies past planned start date | Filled positions + open vacancies | Snapshot |
| Avg planned duration | Mean planned duration in months of vacancies opened in the window | none | 12 months to reporting date |
| Avg days to close | Mean (closed date - opened date), cancelled and date-error tickets excluded | none | Vacancies closed in the 12 months to reporting date |
| Surge national share | Surge requests filled by National staff | Surge requests filled | Requests in the window |
| Retention rate (12m) | Staff present at date - 12 months and still present at date | Staff present at date - 12 months | Two snapshots |
| Turnover rate (12m) | Exits in the 12 months to date | Mean of the 12 month-end headcounts | Rolling 12 months |
| Voluntary / non-voluntary turnover | Exits with the voluntary flag Yes / No | Same as turnover | Rolling 12 months |
| Appraisal completion | Eligible staff with an appraisal dated in the 12 months to date | Eligible staff (at least 6 months of service at date) | Snapshot plus 12-month look-back |
| Int'l G3/G4 current contract duration | Mean granted months of contracts in force | none | Contracts in force at date |
| Int'l G3/G4 new joiner duration | Mean granted months of first contracts starting in the window | none | 12 months to date |
| Contracts ending within 4 months | Int'l contracts in force with end date after date and on or before date + 4 months | Int'l headcount (for %) | Contracts in force at date |

Notes that apply to all of them:

- "Present at month-end" means start date on or before the month-end and end date blank or on or after it. The data
  contains no end date that falls on a month-end, so the boundary does not change any result.
- Month-end offsets use calendar months (`EDATE` / `DateOffset`), so 31 Oct 2026 minus 6 months is 30 Apr 2026.
- Rates use `DIVIDE`, so an empty denominator shows blank, not zero.
- Rolling 12-month measures return blank when the window starts before the first month of data (Jan 2022).
