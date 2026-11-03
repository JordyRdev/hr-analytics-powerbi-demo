# User guide

For HR colleagues using the MFR HR dashboard. All figures in this repository are synthetic.

## Opening the report

Open `MFR_HR_Dashboard.pbip` in Power BI Desktop, or the published version if one has been shared. There are nine pages, listed as tabs along the bottom.

| Page | Use it to |
|---|---|
| 1 Workforce Overview | See headcount by population, gender, country and month |
| 2 Global & International Staff | Compare countries with a year ago; check average age and grade mix |
| 3 Diversity | Follow the share of staff from Global South countries, expatriates, nationality ranking |
| 4 Staffing & Vacancies | Check vacancy rate, open vacancies, how positions were filled |
| 5 Recruitment Duration | See how many days vacancies take to fill |
| 6 Surge Deployments | See surge requests by country and who filled them |
| 7 Retention & Turnover | Retention, turnover, exit reasons, appraisal completion |
| 8 Contracts | See which International contracts end in the next four months |
| 9 Data Quality | See which records failed a check and how the two systems differ for December 2024 and January 2025 |

## The filter pane

The left-hand column has the slicers. Selections carry across pages that show the same slicer.

- **Reporting date** picks the month-end all cards and tables report on. Leave it empty for the latest month. Charts with a month axis always show the full history.
- **Population**: Global (HQ plus Global-unit staff in the field), International, National. HQ is part of Global.
- **Staff type**: National or International contract, decided by grade.
- **Country, Grade, Gender, GN/GS** work as expected.

Hold Ctrl to pick several values. Click a selected value again to clear it.

Pages 4 to 6 have no Population, Gender or GN/GS slicer, because vacancies and surge requests do not record them. Page 8 has no Gender or GN/GS slicer for the same reason.

## Reading the numbers

- Hover over a visual and use the `i` icon for the definition of its measure. The full list is in `docs/measure-definitions.md`.
- **Headcount** is the number of people in post on the last day of the month.
- **Vacancy rate** is open vacancies divided by filled positions plus open vacancies.
- **Retention rate** is the share of people employed twelve months ago who are still employed.
- **Turnover rate** is exits in the last twelve months divided by average headcount.
- **Days to close** runs from the day a vacancy is opened to the day it is closed. Cancelled vacancies are left out. The JIRA field `time_to_done_hours` is shown on page 5 for comparison only: it covers the last workflow step and should not be used for reporting.
- **GS share** is the share of staff with a Global South nationality among staff whose nationality is known.

## Things that look odd but are expected

- Afghanistan has staff until 2025 and none afterwards: the office closed.
- South Sudan grows sharply during 2024.
- Retention is lower for the year to October 2025 than the year to October 2026 because of the Afghanistan closure.
- December 2024 and January 2025 differ slightly between the old and the new system. Page 9 shows the gap.
- A few vacancies stay open for a long time. Six are carried over from the old system and were never closed in JIRA; they are listed on page 9.

## Reporting a data problem

Page 9 lists records that failed a check. Fix them in the source (CORE, JIRA or the country tracker), not in the report. The next refresh picks the correction up.
