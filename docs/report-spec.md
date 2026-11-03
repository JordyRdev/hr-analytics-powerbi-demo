# Report specification

Source of truth for the report layout. Canvas 1280 x 720 px, one page per tab. Positions are x, y, width, height in pixels.
The PBIR files in `powerbi/MFR_HR_Dashboard.Report` follow this document; if they disagree, fix the files.

## Shared layout

| Zone | Position (x, y, w, h) | Content |
|---|---|---|
| Title bar | 0, 0, 1280, 48 | Organisation, report name, page title. Navy fill, white text. |
| Filter pane | 8, 60, 180, up to 650 | One dropdown slicer per field, 54 px high, 58 px pitch. Note box underneath. |
| KPI row | 196, 56, 170 x 84 per card, 178 px pitch | Up to six cards. |
| Content | 196, 148 to 1272, 712 | Two columns (528 and 540 px wide) or one full-width visual. |

### Filter pane

Slicers share a sync group per field, so a selection carries across pages that show the same slicer. A page without a slicer is not filtered by it.

| Slicer | Field | Sync group | Behaviour |
|---|---|---|---|
| Reporting date | `Reporting Date[Label]` | `sync_reporting_date` | Single select. Nothing selected means the latest month-end. |
| Population | `DimPopulation[Population]` | `sync_population` | Multi select |
| Staff type | `DimGrade[Staff Type]` | `sync_staff_type` | Multi select |
| Country | `DimCountry[Country]` | `sync_country` | Multi select |
| Grade | `DimGrade[Grade]` | `sync_grade` | Multi select |
| GN/GS | `DimNationality[GN/GS]` | `sync_gn_gs` | Multi select |
| Gender | `DimGender[Gender]` | `sync_gender` | Multi select |

Charts with a month axis ignore the Reporting Date slicer and show the full history. Cards and charts without a date axis read it.
Every visual with a definition has a header tooltip (the `i` icon) carrying the measure description.

## Page 1: Workforce Overview

Population = Global, International or National. HQ staff are part of Global. Rules: docs/categorisation-rules.md.

Slicers: Reporting date, Population, Staff type, Country, Grade, GN/GS, Gender.

| Visual | Type | Position | Fields | Sort | Notes |
|---|---|---|---|---|---|
| Headcount | `card` | 196, 56, 170, 84 | Values: [Headcount] | default | Tooltip: Distinct staff present at the reference month-end. Follows every slicer. |
| Global | `card` | 374, 56, 170, 84 | Values: [Headcount Global] | default | Tooltip: Headcount of the Global population (HQ plus Global-unit field staff). |
| International | `card` | 552, 56, 170, 84 | Values: [Headcount International] | default | Tooltip: Headcount of the International population (International staff outside Global units). |
| National | `card` | 730, 56, 170, 84 | Values: [Headcount National] | default | Tooltip: Headcount of the National population. |
| of which HQ | `card` | 908, 56, 170, 84 | Values: [Headcount HQ] | default | Tooltip: Headcount of HQ staff. A subset of Global. |
| Female share | `card` | 1086, 56, 170, 84 | Values: [Female Share] | default | Tooltip: Female headcount divided by headcount. |
| Gender by population (HQ shown separately) | `hundredPercentStackedBarChart` | 196, 148, 528, 272 | Category: DimPopulation[Population Detail]; Series: DimGender[Gender]; Y: [Headcount] | DimPopulation[Detail Sort] asc | data labels on; legend top; Tooltip: Headcount split by gender within each population. HQ is a subset of Global and is shown on its own row. |
| Workforce evolution by population | `columnChart` | 732, 148, 540, 272 | Category: DimDate[Year Month]; Series: DimPopulation[Population]; Y: [Headcount] | DimDate[Year Month] asc | legend top; Tooltip: Month-end headcount, January 2022 to the latest month. Ignores the Reporting Date slicer so the whole history shows. |
| National vs International share by country | `hundredPercentStackedBarChart` | 196, 428, 528, 284 | Category: DimCountry[Country]; Series: DimGrade[Staff Type]; Y: [Staff Type Share of Country] | default | data labels on; legend top; Tooltip: Headcount as a share of the country total, ignoring the Staff Type split. Drives the 100% stacked National vs International bars. |
| Headcount by country | `filledMap` | 732, 428, 540, 284 | Category: DimCountry[Country]; Y: [Headcount] | default | Tooltip: Headcount at the reporting date by duty country. Closed offices show no staff. |

## Page 2: Global & International Staff

Use the Population slicer to compare Global and International. All slicers behave the same way on pages 1, 2, 3 and 7.

Slicers: Reporting date, Population, Staff type, Country, Grade, GN/GS, Gender.

| Visual | Type | Position | Fields | Sort | Notes |
|---|---|---|---|---|---|
| Headcount | `card` | 196, 56, 170, 84 | Values: [Headcount] | default | Tooltip: Distinct staff present at the reference month-end. Follows every slicer. |
| Headcount 1 year earlier | `card` | 374, 56, 170, 84 | Values: [Headcount PY] | default | Tooltip: Headcount at the same point one year earlier. |
| Change | `card` | 552, 56, 170, 84 | Values: [Headcount Change vs PY] | default | Tooltip: Headcount minus headcount one year earlier. |
| Change % | `card` | 730, 56, 170, 84 | Values: [Headcount Change % vs PY] | default | Tooltip: Headcount change as a share of headcount one year earlier. |
| Average age | `card` | 908, 56, 170, 84 | Values: [Average Age] | default | Tooltip: Mean age in years of staff present at the reference month-end. Staff without a date of birth are skipped. |
| Age change vs 1 year earlier | `card` | 1086, 56, 170, 84 | Values: [Average Age Change vs PY] | default | Tooltip: Mean age minus mean age one year earlier, in years. |
| Headcount by country: now vs 1 year earlier | `clusteredBarChart` | 196, 148, 528, 272 | Category: DimCountry[Country]; Y: [Headcount], [Headcount PY] | [Headcount] desc | data labels on; legend top; Tooltip: Headcount at the same point one year earlier. |
| Average age by population | `lineChart` | 732, 148, 540, 272 | Category: DimDate[Year Month]; Series: DimPopulation[Population]; Y: [Average Age] | DimDate[Year Month] asc | legend top; Tooltip: Mean age in years of staff present at the reference month-end. Staff without a date of birth are skipped. |
| Average age by grade: now vs 1 year earlier | `clusteredColumnChart` | 196, 428, 528, 284 | Category: DimGrade[Grade]; Y: [Average Age], [Average Age PY] | DimGrade[Sort] asc | legend top; Tooltip: Mean age one year earlier. |
| Headcount by grade and contract type | `pivotTable` | 732, 428, 540, 284 | Rows: DimGrade[Grade]; Columns: DimContractType[Contract Type]; Values: [Headcount] | default | Tooltip: Staff in post at the reporting date. Open-ended contracts exist for HQ only. |

## Page 3: Diversity

Page filter: Staff Type = International (HQ included). GS and GN counts ignore the GN/GS slicer; the ranking and profile charts respect it.

Slicers: Reporting date, Population, Country, Grade, GN/GS, Gender.
Page filter: `DimGrade[Staff Type]` = International.

| Visual | Type | Position | Fields | Sort | Notes |
|---|---|---|---|---|---|
| GS share | `card` | 196, 56, 170, 84 | Values: [GS Share] | default | Tooltip: GS headcount divided by GS plus GN headcount. Staff with unknown nationality are excluded. |
| GS/GN ratio | `card` | 374, 56, 170, 84 | Values: [GS/GN Ratio] | default | Tooltip: GS headcount divided by GN headcount. |
| GS staff | `card` | 552, 56, 170, 84 | Values: [GS Headcount] | default | Tooltip: Headcount with a Global South nationality. Ignores the GN/GS slicer. |
| GN staff | `card` | 730, 56, 170, 84 | Values: [GN Headcount] | default | Tooltip: Headcount with a Global North nationality. Ignores the GN/GS slicer. |
| Expatriates | `card` | 908, 56, 170, 84 | Values: [Expatriates] | default | Tooltip: Distinct International field staff whose nationality differs from the duty country, from the monthly staff snapshots. |
| Surge national share (12m) | `card` | 1086, 56, 170, 84 | Values: [Surge National Share] | default | Tooltip: Filled surge requests filled by National staff divided by all filled surge requests. |
| GS share over time | `lineChart` | 196, 148, 528, 172 | Category: DimDate[Year Month]; Y: [GS Share] | DimDate[Year Month] asc | Tooltip: GS headcount divided by GS plus GN headcount. Staff with unknown nationality are excluded. |
| GS share by grade | `clusteredColumnChart` | 732, 148, 540, 172 | Category: DimGrade[Grade]; Y: [GS Share] | DimGrade[Sort] asc | data labels on; Tooltip: GS headcount divided by GS plus GN headcount. Staff with unknown nationality are excluded. |
| GS share by grade over time | `lineChart` | 196, 328, 528, 172 | Category: DimDate[Year Month]; Series: DimGrade[Grade]; Y: [GS Share] | DimDate[Year Month] asc | legend top; Tooltip: GS headcount divided by GS plus GN headcount. Staff with unknown nationality are excluded. |
| Expatriates over time | `lineChart` | 732, 328, 540, 172 | Category: DimDate[Year Month]; Y: [Expatriates] | DimDate[Year Month] asc | Tooltip: Distinct International field staff whose nationality differs from the duty country, from the monthly staff snapshots. |
| Nationality ranking (use the GN/GS slicer) | `clusteredBarChart` | 196, 508, 528, 204 | Category: DimNationality[Nationality]; Y: [Headcount] | [Headcount] desc | data labels on; Tooltip: Headcount by nationality, largest first. The GN/GS slicer narrows the list. |
| Profile: contract type by gender | `hundredPercentStackedColumnChart` | 732, 508, 266, 204 | Category: DimContractType[Contract Type]; Series: DimGender[Gender]; Y: [Headcount] | default | legend top; Tooltip: Gender mix within each contract type, for the staff selected. |
| Profile: country by gender | `hundredPercentStackedBarChart` | 1006, 508, 266, 204 | Category: DimCountry[Country]; Series: DimGender[Gender]; Y: [Headcount] | default | legend top; Tooltip: Gender mix within each country, for the staff selected. |

## Page 4: Staffing & Vacancies

Vacancy measures ignore Population, Gender and GN/GS because vacancies do not carry them. Those slicers are not on this page.

Slicers: Reporting date, Staff type, Country, Grade.

| Visual | Type | Position | Fields | Sort | Notes |
|---|---|---|---|---|---|
| Retention rate (12m) | `card` | 196, 56, 170, 84 | Values: [Retention Rate (12m)] | default | Tooltip: Staff present 12 months before the reference date who are still present at it, divided by staff present 12 months before. |
| Vacancy rate | `card` | 374, 56, 170, 84 | Values: [Vacancy Rate] | default | Tooltip: Open vacancies divided by filled positions plus open vacancies. |
| Due-vacancy rate | `card` | 552, 56, 170, 84 | Values: [Due Vacancy Rate] | default | Tooltip: Open vacancies past their planned start date divided by total positions (filled plus open). |
| Open vacancies | `card` | 730, 56, 170, 84 | Values: [Open Vacancies] | default | Tooltip: Vacancies open at the reference month-end. |
| Avg planned duration (months) | `card` | 908, 56, 170, 84 | Values: [Avg Planned Duration (months)] | default | Tooltip: Mean initial planned duration of the positions opened in the window. |
| Vacancies opened (12m) | `card` | 1086, 56, 170, 84 | Values: [Vacancies Opened] | default | Tooltip: Vacancies opened. Uses the date axis when a visual has one, otherwise the 12 months to the reporting date. |
| Vacancies open at month-end, by source | `columnChart` | 196, 148, 528, 184 | Category: DimDate[Year Month]; Series: FactVacancyMonthly[Source]; Y: [Open Vacancies] | DimDate[Year Month] asc | legend top; Tooltip: Vacancies open at the reference month-end. |
| Vacancy rate and due-vacancy rate | `lineChart` | 732, 148, 540, 184 | Category: DimDate[Year Month]; Y: [Vacancy Rate], [Due Vacancy Rate] | DimDate[Year Month] asc | legend top; Tooltip: Open vacancies divided by filled positions plus open vacancies. |
| New positions vs replacements, by year opened | `columnChart` | 196, 340, 528, 184 | Category: DimDate[Year]; Series: FactVacancies[Opening Reason]; Y: [Vacancies Opened] | default | data labels on; legend top; Tooltip: Vacancies opened. Uses the date axis when a visual has one, otherwise the 12 months to the reporting date. |
| Average planned duration by country (months) | `clusteredBarChart` | 732, 340, 540, 184 | Category: DimCountry[Country]; Y: [Avg Planned Duration (months)] | [Avg Planned Duration (months)] desc | data labels on; Tooltip: Mean initial planned duration of the positions opened in the window. |
| Closure outcomes (12 months) | `clusteredBarChart` | 196, 532, 528, 180 | Category: FactVacancies[Closure Outcome]; Y: [Vacancies Closed] | [Vacancies Closed] desc | data labels on; Tooltip: Vacancies closed (filled or cancelled) in the window, by closed date. |
| Candidate type on closure (12 months) | `clusteredColumnChart` | 732, 532, 540, 180 | Category: FactVacancies[Candidate Type]; Y: [Vacancies Closed] | default | data labels on; Tooltip: External, current staff or former staff, for vacancies closed in the window. |

## Page 5: Recruitment Duration

Days to close = closed date minus opened date. Cancelled vacancies and tickets with a date error are excluded.

Slicers: Reporting date, Staff type, Country, Grade.

| Visual | Type | Position | Fields | Sort | Notes |
|---|---|---|---|---|---|
| Avg days to close (12m) | `card` | 196, 56, 170, 84 | Values: [Avg Days to Close] | default | Tooltip: Mean days from opened to closed date for filled vacancies. Cancelled vacancies and tickets with a date error are excluded. |
| Avg JIRA time_to_done (days) | `card` | 374, 56, 170, 84 | Values: [Avg Time To Done (days)] | default | Tooltip: Mean JIRA time_to_done_hours converted to days, for the same vacancies as Avg Days to Close. It measures only the last workflow stage. |
| Filled vacancies measured | `card` | 552, 56, 170, 84 | Values: [Filled Vacancies] | default | Tooltip: Vacancies closed with a valid duration in the window. Sample size behind Avg Days to Close. |
| Vacancies closed (12m) | `card` | 730, 56, 170, 84 | Values: [Vacancies Closed] | default | Tooltip: Vacancies closed (filled or cancelled) in the window, by closed date. |
| Break down by | `slicer` | 908, 56, 354, 84 | Values: Breakdown[Breakdown] | default | Tooltip: Switches the category of the bar chart below. |
| Average days to close, by selected breakdown | `clusteredBarChart` | 196, 148, 528, 272 | Category: Breakdown[Breakdown]; Y: [Avg Days to Close] | default | data labels on; Tooltip: Mean days from opened to closed date for filled vacancies. Cancelled vacancies and tickets with a date error are excluded. |
| Distribution of days to close | `clusteredColumnChart` | 732, 148, 540, 272 | Category: FactVacancies[Days Bucket]; Y: [Filled Vacancies] | default | data labels on; Tooltip: Number of filled vacancies in each duration band. |
| Days to close vs JIRA time_to_done_hours (one dot per ticket) | `scatterChart` | 196, 428, 528, 284 | Category: FactVacancies[Vacancy ID]; X: Sum of FactVacancies[Days to Close]; Y: Sum of FactVacancies[Time To Done Hours] | default | Tooltip: Each dot is a closed vacancy. JIRA tickets only; legacy vacancies have no time_to_done value. |
| Average days to close by month closed | `lineChart` | 732, 428, 540, 150 | Category: DimDate[Year Month]; Y: [Avg Days to Close] | DimDate[Year Month] asc | Tooltip: Mean days from opened to closed date for filled vacancies. Cancelled vacancies and tickets with a date error are excluded. |
| Why time_to_done_hours is not used | `textbox` | 732, 586, 540, 126 | Static text | default | time_to_done_hours records only the last JIRA workflow stage, a day or two on average. HR reports the full duration, from the date the vacancy is opened to the date it is closed, excluding cancelled vacancies. The scatter shows the two measures are unrelated, so the JIRA field cannot stand in for duration to close. |

## Page 6: Surge Deployments

Surge requests for 2022 to 2024 come from the legacy log, 2025 onward from JIRA.

Slicers: Reporting date, Staff type, Country, Grade.

| Visual | Type | Position | Fields | Sort | Notes |
|---|---|---|---|---|---|
| Requests (12m) | `card` | 196, 56, 170, 84 | Values: [Surge Requests] | default | Tooltip: Surge requests raised. Uses the date axis when a visual has one, otherwise the 12 months to the reporting date. |
| Filled | `card` | 374, 56, 170, 84 | Values: [Surge Requests Filled] | default | Tooltip: Surge requests with status Filled. |
| Filled by National | `card` | 552, 56, 170, 84 | Values: [Surge Filled by National] | default | Tooltip: Filled surge requests where the post went to a National staff member. |
| Filled by International | `card` | 730, 56, 170, 84 | Values: [Surge Filled by International] | default | Tooltip: Filled surge requests where the post went to an International staff member. |
| National share of fills | `card` | 908, 56, 170, 84 | Values: [Surge National Share] | default | Tooltip: Filled surge requests filled by National staff divided by all filled surge requests. |
| Surge requests by country (12 months) | `clusteredBarChart` | 196, 148, 528, 280 | Category: DimCountry[Country]; Y: [Surge Requests] | [Surge Requests] desc | data labels on; Tooltip: Surge requests raised. Uses the date axis when a visual has one, otherwise the 12 months to the reporting date. |
| National vs International fill, by year | `hundredPercentStackedColumnChart` | 732, 148, 540, 280 | Category: DimDate[Year]; Series: FactSurges[Filled By]; Y: [Surge Requests Filled] | default | data labels on; legend top; Tooltip: Filled surge requests filled by National staff divided by all filled surge requests. |
| Surge requests per month | `columnChart` | 196, 436, 1076, 276 | Category: DimDate[Year Month]; Y: [Surge Requests] | DimDate[Year Month] asc | Tooltip: Requests raised each month, January 2022 to the latest month. |

## Page 7: Retention & Turnover

Appraisal history starts in January 2024, so the completion trend starts in January 2025.

Slicers: Reporting date, Population, Staff type, Country, Grade, GN/GS, Gender.

| Visual | Type | Position | Fields | Sort | Notes |
|---|---|---|---|---|---|
| Retention rate (12m) | `card` | 196, 56, 170, 84 | Values: [Retention Rate (12m)] | default | Tooltip: Staff present 12 months before the reference date who are still present at it, divided by staff present 12 months before. |
| Turnover rate (12m) | `card` | 374, 56, 170, 84 | Values: [Turnover Rate (12m)] | default | Tooltip: Exits in the 12 months divided by the mean headcount of the same months. |
| Voluntary turnover | `card` | 552, 56, 170, 84 | Values: [Voluntary Turnover Rate (12m)] | default | Tooltip: Voluntary exits divided by mean headcount. |
| Non-voluntary turnover | `card` | 730, 56, 170, 84 | Values: [Non-voluntary Turnover Rate (12m)] | default | Tooltip: Non-voluntary exits divided by mean headcount. |
| Exits (12m) | `card` | 908, 56, 170, 84 | Values: [Exits (12m)] | default | Tooltip: Exit events in the 12 months to the reference date. |
| Appraisal completion | `card` | 1086, 56, 170, 84 | Values: [Appraisal Completion] | default | Tooltip: Eligible staff with an appraisal dated in the 12 months to the reference date, divided by eligible staff. |
| Retention rate (rolling 12 months) | `lineChart` | 196, 148, 528, 272 | Category: DimDate[Year Month]; Y: [Retention Rate (12m)] | DimDate[Year Month] asc | Tooltip: Staff present 12 months before the reference date who are still present at it, divided by staff present 12 months before. |
| Turnover rate: voluntary and non-voluntary | `lineChart` | 732, 148, 540, 272 | Category: DimDate[Year Month]; Y: [Voluntary Turnover Rate (12m)], [Non-voluntary Turnover Rate (12m)] | DimDate[Year Month] asc | legend top; Tooltip: Exits in the 12 months divided by the mean headcount of the same months. |
| Exits by reason (12 months) | `clusteredBarChart` | 196, 428, 528, 284 | Category: FactExits[Exit Reason]; Y: [Exits (12m)] | [Exits (12m)] desc | data labels on; Tooltip: Exit events in the 12 months to the reference date. |
| Appraisal completion (eligible staff, last 12 months) | `lineChart` | 732, 428, 540, 284 | Category: DimDate[Year Month]; Y: [Appraisal Completion] | DimDate[Year Month] asc | Tooltip: Eligible staff with an appraisal dated in the 12 months to the reference date, divided by eligible staff. |

## Page 8: Contracts

International contracts only. Gender and GN/GS slicers are not on this page because contracts do not carry them.

Slicers: Reporting date, Population, Country, Grade.

| Visual | Type | Position | Fields | Sort | Notes |
|---|---|---|---|---|---|
| Int'l G3/G4 current contract (months) | `card` | 196, 56, 170, 84 | Values: [Avg Current Contract Duration G3/G4 (months)] | default | Tooltip: Mean granted months of the International G3 and G4 contracts in force at the reference date. Open-ended contracts have no duration and are skipped. |
| Int'l G3/G4 new joiners (months) | `card` | 374, 56, 170, 84 | Values: [Avg Granted Duration New Joiners G3/G4 (months)] | default | Tooltip: Mean granted months of the first contracts of International G3 and G4 staff that started in the 12 months to the reference date. |
| Int'l contracts ending in 4 months | `card` | 552, 56, 170, 84 | Values: [Contracts Ending Within 4 Months] | default | Tooltip: International contracts in force whose end date falls after the reference date and within the next 4 months. |
| Share of Int'l staff | `card` | 730, 56, 170, 84 | Values: [Contracts Ending Within 4 Months %] | default | Tooltip: Contracts ending within 4 months divided by International headcount at the reference date. |
| Contracts in force | `card` | 908, 56, 170, 84 | Values: [Contracts in Force] | default | Tooltip: Contracts in force at the reference month-end. |
| International contracts ending within 4 months, by grade | `columnChart` | 196, 148, 528, 260 | Category: DimGrade[Grade]; Y: [Contracts Ending Within 4 Months] | DimGrade[Sort] asc | data labels on; Tooltip: International contracts in force whose end date falls after the reference date and within the next 4 months. |
| International contracts ending within 4 months, by country | `clusteredBarChart` | 732, 148, 540, 260 | Category: DimCountry[Country]; Y: [Contracts Ending Within 4 Months] | [Contracts Ending Within 4 Months] desc | data labels on; Tooltip: International contracts in force whose end date falls after the reference date and within the next 4 months. |
| Contracts ending within 4 months (days remaining) | `tableEx` | 196, 416, 1076, 296 | Values: FactContracts[Staff ID], FactContracts[Grade], FactContracts[Country], FactContracts[End Date], [Days Remaining] | [Days Remaining] asc | background gradient on [Days Remaining], #E76F51 to #FFFFFF; Tooltip: Days from the reference date to the end of a contract. Blank unless the contract ends within 4 months, so a table of contracts lists only those. |

## Page 9: Data Quality

Every row in DQ_Issues is a record that failed a check. Nothing is removed from the model silently. See docs/data-quality.md.

Slicers: none.

| Visual | Type | Position | Fields | Sort | Notes |
|---|---|---|---|---|---|
| Issues logged | `card` | 196, 56, 170, 84 | Values: [DQ Issues] | default | Tooltip: Rows in DQ_Issues in the current filter context. |
| Last refresh | `card` | 374, 56, 170, 84 | Values: [Last Refresh] | default | Tooltip: Date and time of the last data refresh. |
| Data through | `card` | 552, 56, 170, 84 | Values: [Data Through] | default | Tooltip: Last month-end loaded. |
| Issues by check and source | `barChart` | 196, 148, 528, 272 | Category: DQ_Issues[Check]; Series: DQ_Issues[Source]; Y: [DQ Issues] | [DQ Issues] desc | legend top; Tooltip: Rows in DQ_Issues. Detail for each row is in the DQ_Issues table. |
| Issues by month of the affected record | `columnChart` | 732, 148, 540, 272 | Category: DimDate[Year Month]; Y: [DQ Issues] | DimDate[Year Month] asc | Tooltip: Month of the record that failed the check (snapshot month, ticket created, contract start). |
| Overlap months: legacy snapshot vs CORE and trackers | `tableEx` | 196, 428, 528, 284 | Values: Recon_Overlap[Month End], [Recon Historical Headcount], [Recon Current Headcount], [Recon Difference] | Recon_Overlap[Month End] asc | Tooltip: Dec 2024 and Jan 2025 are reported by both systems. The cut-over rule takes the legacy file up to Dec 2024 and CORE from Jan 2025. |
| Expatriates: snapshots vs deployment log | `lineChart` | 732, 428, 540, 284 | Category: DimDate[Year Month]; Y: [Expatriates], [Expatriates (deployment log)] | DimDate[Year Month] asc | legend top; Tooltip: Expatriate deployments active at the reference month-end, from the deployment table. Used to reconcile against the snapshot count. |

## Formatting

- Theme `powerbi/theme/mfr_theme.json`: navy `#1F3A5F`, teal `#2A9D8F`, warm grey `#8D8A84`, accent `#E76F51`.
- Percent measures show one decimal, counts use thousands separators. Formats live on the measures.
- Month axes use `DimDate[Year Month]` (text, sorts correctly) and are sorted ascending.
- Chart titles are 11 pt bold navy. Cards show the value at 24 pt with the title above.
