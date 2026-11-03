# Measure definitions

All measures sit in the `_Measures` table, grouped in display folders that follow the report pages. Every measure reads one reference month-end (`[Ref Date]`). The DAX below is copied from the model.

## Date logic

- `Reporting Date` is a disconnected table of month-ends. Its slicer sets `[Selected Reporting Date]`; with nothing selected the latest month-end is used.
- `[Ref Date]` equals the month on the date axis when a visual has one, otherwise the slicer value. The same measure therefore gives a card value and a monthly trend.
- Month offsets use `EOMONTH` on a month-end, so 31 Oct 2026 minus 6 months is 30 Apr 2026.
- A person is present at a month-end when start date is on or before it and end date is blank or on or after it. No end date in the data falls on a month-end.
- Rolling 12-month measures cover the 12 months after `EOMONTH([Ref Date], -12)`. They return blank when the window starts before January 2022.
- Rates use `DIVIDE`, so an empty denominator gives blank.
- Measures that set a month-end explicitly call `REMOVEFILTERS ( DimDate )` first, otherwise the axis filter would cancel the date they ask for.

## KPI summary

| KPI | Numerator | Denominator | Date logic |
|---|---|---|---|
| Headcount | Distinct staff IDs present | none | Snapshot at reporting date |
| Headcount vs 1 year earlier | Headcount minus headcount 12 months before | Headcount 12 months before (for %) | Two snapshots |
| Average age | Mean age in years at the month-end | none | Snapshot |
| GS share, GS/GN ratio | GS staff; GS staff | GS plus GN staff; GN staff | Snapshot. Unknown nationality excluded |
| Expatriates | International field staff with nationality different from duty country | none | Snapshot |
| Vacancy rate | Open vacancies | Filled positions plus open vacancies | Snapshot |
| Due-vacancy rate | Open vacancies past planned start date | Filled positions plus open vacancies | Snapshot |
| Avg planned duration | Mean planned months of vacancies opened | none | 12 months to reporting date |
| Avg days to close | Mean closed date minus opened date, cancelled and date-error tickets excluded | none | Vacancies closed in the last 12 months |
| Surge national share | Filled surge requests filled by National staff | Filled surge requests | Requests in the last 12 months |
| Retention rate (12m) | Staff present 12 months ago and still present | Staff present 12 months ago | Two snapshots |
| Turnover rate (12m) | Exits in the window | Mean of the 12 month-end headcounts | Rolling 12 months |
| Appraisal completion | Eligible staff with an appraisal in the last 12 months | Eligible staff (6 months of service or more) | Snapshot plus look-back |
| Int'l G3/G4 current contract duration | Mean granted months of contracts in force | none | Contracts in force |
| Int'l G3/G4 new joiner duration | Mean granted months of first contracts started in the window | none | 12 months to reporting date |
| Contracts ending within 4 months | Int'l contracts in force ending in the next 4 months | Int'l headcount (for %) | Contracts in force |

## Duration to close and time_to_done_hours

Duration to close is closed date minus opened date. JIRA also exports `time_to_done_hours`, which records only the time spent in the last workflow stage (typically a day or two) and says nothing about how long the position was open. Page 5 shows both side by side; the scatter shows no relationship. Reporting must use the full duration.

## Filter behaviour worth knowing

- Vacancy measures ignore the Population, Gender and GN/GS selections because vacancies do not carry them. Those slicers are not shown on pages 4 to 6.
- GS and GN counts ignore the GN/GS slicer, so the share cards stay meaningful when it is used. The nationality ranking respects it.
- Fixed-population measures (Global, International, National, International contracts) use `KEEPFILTERS`, so a conflicting slicer selection gives blank rather than a wrong number.
- The Breakdown field parameter offers Country, Grade, Closure Outcome and Staff Type. Vacancies carry no Population, so Staff Type replaces it.

## 00 Date logic

### Selected Reporting Date

Month-end picked in the Reporting Date slicer. Latest month-end when nothing is selected.

Format: `yyyy-mm-dd`

```dax
Selected Reporting Date =
MAX ( 'Reporting Date'[Month End] )
```

### Ref Date

Month-end every 'at date' measure reads. Follows the date axis of a visual when one is present, otherwise the Reporting Date slicer.

Format: `yyyy-mm-dd`

```dax
Ref Date =
IF ( ISCROSSFILTERED ( DimDate ), MAX ( DimDate[Month End] ), [Selected Reporting Date] )
```

### Window Start

Last month-end before the 12-month window that ends at the reference date.

Format: `yyyy-mm-dd`

```dax
Window Start =
EOMONTH ( [Ref Date], -12 )
```

### First Data Month

Earliest month-end in the staff snapshots. Used to blank rolling measures that would start before the data.

Format: `yyyy-mm-dd`

```dax
First Data Month =
CALCULATE ( MIN ( FactStaffMonthly[Month End] ), REMOVEFILTERS () )
```

## 01 Workforce

### Headcount

Distinct staff present at the reference month-end. Follows every slicer.

Format: `#,0`

```dax
Headcount =
VAR _d = [Ref Date]
RETURN
    CALCULATE (
        DISTINCTCOUNT ( FactStaffMonthly[Staff ID] ),
        REMOVEFILTERS ( DimDate ),
        FactStaffMonthly[Month End] = _d
    )
```

### Headcount PY

Headcount at the same point one year earlier.

Format: `#,0`

```dax
Headcount PY =
VAR _d = EOMONTH ( [Ref Date], -12 )
RETURN
    CALCULATE (
        DISTINCTCOUNT ( FactStaffMonthly[Staff ID] ),
        REMOVEFILTERS ( DimDate ),
        FactStaffMonthly[Month End] = _d
    )
```

### Headcount Change vs PY

Headcount minus headcount one year earlier.

Format: `+#,0;-#,0;0`

```dax
Headcount Change vs PY =
[Headcount] - [Headcount PY]
```

### Headcount Change % vs PY

Headcount change as a share of headcount one year earlier.

Format: `+0.0%;-0.0%;0.0%`

```dax
Headcount Change % vs PY =
DIVIDE ( [Headcount] - [Headcount PY], [Headcount PY] )
```

### Headcount Global

Headcount of the Global population (HQ plus Global-unit field staff).

Format: `#,0`

```dax
Headcount Global =
CALCULATE ( [Headcount], KEEPFILTERS ( DimPopulation[Population] = "Global" ) )
```

### Headcount International

Headcount of the International population (International staff outside Global units).

Format: `#,0`

```dax
Headcount International =
CALCULATE ( [Headcount], KEEPFILTERS ( DimPopulation[Population] = "International" ) )
```

### Headcount National

Headcount of the National population.

Format: `#,0`

```dax
Headcount National =
CALCULATE ( [Headcount], KEEPFILTERS ( DimPopulation[Population] = "National" ) )
```

### Headcount HQ

Headcount of HQ staff. A subset of Global.

Format: `#,0`

```dax
Headcount HQ =
CALCULATE ( [Headcount], KEEPFILTERS ( DimPopulation[Population Detail] = "Global - HQ" ) )
```

### Female Headcount

Headcount of female staff.

Format: `#,0`

```dax
Female Headcount =
CALCULATE ( [Headcount], KEEPFILTERS ( DimGender[Gender] = "Female" ) )
```

### Female Share

Female headcount divided by headcount.

Format: `0.0%`

```dax
Female Share =
DIVIDE ( [Female Headcount], [Headcount] )
```

### Staff Type Share of Country

Headcount as a share of the country total, ignoring the Staff Type split. Drives the 100% stacked National vs International bars.

Format: `0.0%`

```dax
Staff Type Share of Country =
DIVIDE ( [Headcount], CALCULATE ( [Headcount], REMOVEFILTERS ( DimGrade[Staff Type] ) ) )
```

## 02 Global and International

### Average Age

Mean age in years of staff present at the reference month-end. Staff without a date of birth are skipped.

Format: `0.0`

```dax
Average Age =
VAR _d = [Ref Date]
RETURN
    CALCULATE (
        AVERAGE ( FactStaffMonthly[Age] ),
        REMOVEFILTERS ( DimDate ),
        FactStaffMonthly[Month End] = _d
    )
```

### Average Age PY

Mean age one year earlier.

Format: `0.0`

```dax
Average Age PY =
VAR _d = EOMONTH ( [Ref Date], -12 )
RETURN
    CALCULATE (
        AVERAGE ( FactStaffMonthly[Age] ),
        REMOVEFILTERS ( DimDate ),
        FactStaffMonthly[Month End] = _d
    )
```

### Average Age Change vs PY

Mean age minus mean age one year earlier, in years.

Format: `+0.0;-0.0;0.0`

```dax
Average Age Change vs PY =
[Average Age] - [Average Age PY]
```

## 03 Diversity

### GS Headcount

Headcount with a Global South nationality. Ignores the GN/GS slicer.

Format: `#,0`

```dax
GS Headcount =
CALCULATE ( [Headcount], DimNationality[GN/GS] = "GS" )
```

### GN Headcount

Headcount with a Global North nationality. Ignores the GN/GS slicer.

Format: `#,0`

```dax
GN Headcount =
CALCULATE ( [Headcount], DimNationality[GN/GS] = "GN" )
```

### GS Share

GS headcount divided by GS plus GN headcount. Staff with unknown nationality are excluded.

Format: `0.0%`

```dax
GS Share =
DIVIDE ( [GS Headcount], [GS Headcount] + [GN Headcount] )
```

### GS/GN Ratio

GS headcount divided by GN headcount.

Format: `0.00`

```dax
GS/GN Ratio =
DIVIDE ( [GS Headcount], [GN Headcount] )
```

### Expatriates

Distinct International field staff whose nationality differs from the duty country, from the monthly staff snapshots.

Format: `#,0`

```dax
Expatriates =
CALCULATE ( [Headcount], FactStaffMonthly[Is Expatriate] = TRUE () )
```

### Expatriates (deployment log)

Expatriate deployments active at the reference month-end, from the deployment table. Used to reconcile against the snapshot count.

Format: `#,0`

```dax
Expatriates (deployment log) =
VAR _d = [Ref Date]
RETURN
    IF (
        ISBLANK ( _d ),
        BLANK (),
        CALCULATE (
            DISTINCTCOUNT ( FactExpatriation[Staff ID] ),
            REMOVEFILTERS ( DimDate ),
            FILTER (
                ALL ( FactExpatriation[Start Date], FactExpatriation[End Date] ),
                FactExpatriation[Start Date] <= _d
                    && ( ISBLANK ( FactExpatriation[End Date] ) || FactExpatriation[End Date] >= _d )
            )
        ) + 0
    )
```

## 04 Staffing and vacancies

### Open Vacancies

Vacancies open at the reference month-end.

Format: `#,0`

```dax
Open Vacancies =
VAR _d = [Ref Date]
RETURN
    IF (
        ISBLANK ( _d ),
        BLANK (),
        CALCULATE (
            DISTINCTCOUNT ( FactVacancyMonthly[Vacancy ID] ),
            REMOVEFILTERS ( DimDate ),
            FactVacancyMonthly[Month End] = _d
        ) + 0
    )
```

### Due Open Vacancies

Open vacancies whose planned start date is before the reference month-end.

Format: `#,0`

```dax
Due Open Vacancies =
VAR _d = [Ref Date]
RETURN
    IF (
        ISBLANK ( _d ),
        BLANK (),
        CALCULATE (
            DISTINCTCOUNT ( FactVacancyMonthly[Vacancy ID] ),
            REMOVEFILTERS ( DimDate ),
            FactVacancyMonthly[Month End] = _d,
            FactVacancyMonthly[Is Due] = TRUE ()
        ) + 0
    )
```

### Filled Positions

Staff in post at the reference month-end, ignoring Population, Gender and GN/GS selections because vacancies carry none of them.

Format: `#,0`

```dax
Filled Positions =
VAR _d = [Ref Date]
RETURN
    CALCULATE (
        DISTINCTCOUNT ( FactStaffMonthly[Staff ID] ),
        REMOVEFILTERS ( DimDate ),
        REMOVEFILTERS ( DimPopulation ),
        REMOVEFILTERS ( DimNationality ),
        REMOVEFILTERS ( DimGender ),
        FactStaffMonthly[Month End] = _d
    )
```

### Vacancy Rate

Open vacancies divided by filled positions plus open vacancies.

Format: `0.0%`

```dax
Vacancy Rate =
DIVIDE ( [Open Vacancies], [Filled Positions] + [Open Vacancies] )
```

### Due Vacancy Rate

Open vacancies past their planned start date divided by total positions (filled plus open).

Format: `0.0%`

```dax
Due Vacancy Rate =
DIVIDE ( [Due Open Vacancies], [Filled Positions] + [Open Vacancies] )
```

### Vacancies Opened

Vacancies opened. Uses the date axis when a visual has one, otherwise the 12 months to the reporting date.

Format: `#,0`

```dax
Vacancies Opened =
VAR _ref = [Ref Date]
VAR _lo = EOMONTH ( _ref, -12 )
RETURN
    IF (
        ISCROSSFILTERED ( DimDate ),
        COUNTROWS ( FactVacancies ),
        CALCULATE ( COUNTROWS ( FactVacancies ), DATESBETWEEN ( DimDate[Date], _lo + 1, _ref ) )
    )
```

### Avg Planned Duration (months)

Mean initial planned duration of the positions opened in the window.

Format: `0.0`

```dax
Avg Planned Duration (months) =
VAR _ref = [Ref Date]
VAR _lo = EOMONTH ( _ref, -12 )
RETURN
    IF (
        ISCROSSFILTERED ( DimDate ),
        AVERAGE ( FactVacancies[Planned Duration Months] ),
        CALCULATE ( AVERAGE ( FactVacancies[Planned Duration Months] ), DATESBETWEEN ( DimDate[Date], _lo + 1, _ref ) )
    )
```

### Vacancies Closed

Vacancies closed (filled or cancelled) in the window, by closed date.

Format: `#,0`

```dax
Vacancies Closed =
VAR _ref = [Ref Date]
VAR _lo = EOMONTH ( _ref, -12 )
RETURN
    IF (
        ISCROSSFILTERED ( DimDate ),
        CALCULATE ( COUNTROWS ( FactVacancies ), USERELATIONSHIP ( FactVacancies[Closed Date], DimDate[Date] ) ),
        CALCULATE (
            COUNTROWS ( FactVacancies ),
            USERELATIONSHIP ( FactVacancies[Closed Date], DimDate[Date] ),
            DATESBETWEEN ( DimDate[Date], _lo + 1, _ref )
        )
    )
```

### Retention Rate (12m)

Staff present 12 months before the reference date who are still present at it, divided by staff present 12 months before.

Format: `0.0%`

```dax
Retention Rate (12m) =
VAR _end = [Ref Date]
VAR _start = EOMONTH ( _end, -12 )
VAR _startIds =
    CALCULATETABLE (
        VALUES ( FactStaffMonthly[Staff ID] ),
        REMOVEFILTERS ( DimDate ),
        FactStaffMonthly[Month End] = _start
    )
VAR _endIds =
    CALCULATETABLE (
        VALUES ( FactStaffMonthly[Staff ID] ),
        REMOVEFILTERS ( DimDate ),
        FactStaffMonthly[Month End] = _end
    )
RETURN
    IF (
        _start < [First Data Month],
        BLANK (),
        DIVIDE ( COUNTROWS ( INTERSECT ( _startIds, _endIds ) ), COUNTROWS ( _startIds ) )
    )
```

## 05 Recruitment duration

### Avg Days to Close

Mean days from opened to closed date for filled vacancies. Cancelled vacancies and tickets with a date error are excluded.

Format: `0.0`

```dax
Avg Days to Close =
VAR _ref = [Ref Date]
VAR _lo = EOMONTH ( _ref, -12 )
RETURN
    IF (
        ISCROSSFILTERED ( DimDate ),
        CALCULATE ( AVERAGE ( FactVacancies[Days to Close] ), USERELATIONSHIP ( FactVacancies[Closed Date], DimDate[Date] ) ),
        CALCULATE (
            AVERAGE ( FactVacancies[Days to Close] ),
            USERELATIONSHIP ( FactVacancies[Closed Date], DimDate[Date] ),
            DATESBETWEEN ( DimDate[Date], _lo + 1, _ref )
        )
    )
```

### Avg Time To Done (days)

Mean JIRA time_to_done_hours converted to days, for the same vacancies as Avg Days to Close. It measures only the last workflow stage.

Format: `0.0`

```dax
Avg Time To Done (days) =
VAR _ref = [Ref Date]
VAR _lo = EOMONTH ( _ref, -12 )
RETURN
    IF (
        ISCROSSFILTERED ( DimDate ),
        CALCULATE ( AVERAGE ( FactVacancies[Time To Done Days] ), USERELATIONSHIP ( FactVacancies[Closed Date], DimDate[Date] ) ),
        CALCULATE (
            AVERAGE ( FactVacancies[Time To Done Days] ),
            USERELATIONSHIP ( FactVacancies[Closed Date], DimDate[Date] ),
            DATESBETWEEN ( DimDate[Date], _lo + 1, _ref )
        )
    )
```

### Filled Vacancies

Vacancies closed with a valid duration in the window. Sample size behind Avg Days to Close.

Format: `#,0`

```dax
Filled Vacancies =
VAR _ref = [Ref Date]
VAR _lo = EOMONTH ( _ref, -12 )
RETURN
    IF (
        ISCROSSFILTERED ( DimDate ),
        CALCULATE ( COUNT ( FactVacancies[Days to Close] ), USERELATIONSHIP ( FactVacancies[Closed Date], DimDate[Date] ) ),
        CALCULATE (
            COUNT ( FactVacancies[Days to Close] ),
            USERELATIONSHIP ( FactVacancies[Closed Date], DimDate[Date] ),
            DATESBETWEEN ( DimDate[Date], _lo + 1, _ref )
        )
    )
```

## 06 Surge deployments

### Surge Requests

Surge requests raised. Uses the date axis when a visual has one, otherwise the 12 months to the reporting date.

Format: `#,0`

```dax
Surge Requests =
VAR _ref = [Ref Date]
VAR _lo = EOMONTH ( _ref, -12 )
RETURN
    IF (
        ISCROSSFILTERED ( DimDate ),
        COUNTROWS ( FactSurges ),
        CALCULATE ( COUNTROWS ( FactSurges ), DATESBETWEEN ( DimDate[Date], _lo + 1, _ref ) )
    )
```

### Surge Requests Filled

Surge requests with status Filled.

Format: `#,0`

```dax
Surge Requests Filled =
CALCULATE ( [Surge Requests], FactSurges[Status] = "Filled" )
```

### Surge Filled by National

Filled surge requests where the post went to a National staff member.

Format: `#,0`

```dax
Surge Filled by National =
CALCULATE ( [Surge Requests], FactSurges[Status] = "Filled", FactSurges[Filled By] = "National" )
```

### Surge Filled by International

Filled surge requests where the post went to an International staff member.

Format: `#,0`

```dax
Surge Filled by International =
CALCULATE ( [Surge Requests], FactSurges[Status] = "Filled", FactSurges[Filled By] = "International" )
```

### Surge National Share

Filled surge requests filled by National staff divided by all filled surge requests.

Format: `0.0%`

```dax
Surge National Share =
DIVIDE ( [Surge Filled by National], [Surge Requests Filled] )
```

### Surge National Share (all staff types)

Surge National Share with the Staff Type filter removed. National fills sit on National grades, so a page filter on International staff would otherwise hide them.

Format: `0.0%`

```dax
Surge National Share (all staff types) =
CALCULATE ( [Surge National Share], REMOVEFILTERS ( DimGrade[Staff Type] ) )
```

## 07 Retention and turnover

### Exits (12m)

Exit events in the 12 months to the reference date.

Format: `#,0`

```dax
Exits (12m) =
VAR _end = [Ref Date]
VAR _start = EOMONTH ( _end, -12 )
RETURN
    IF (
        ISBLANK ( _end ),
        BLANK (),
        CALCULATE (
            COUNTROWS ( FactExits ),
            REMOVEFILTERS ( DimDate ),
            FactExits[Exit Date] > _start,
            FactExits[Exit Date] <= _end
        ) + 0
    )
```

### Voluntary Exits (12m)

Exits flagged voluntary in the 12 months to the reference date.

Format: `#,0`

```dax
Voluntary Exits (12m) =
CALCULATE ( [Exits (12m)], FactExits[Voluntary] = "Yes" )
```

### Non-voluntary Exits (12m)

Exits flagged non-voluntary in the 12 months to the reference date.

Format: `#,0`

```dax
Non-voluntary Exits (12m) =
CALCULATE ( [Exits (12m)], FactExits[Voluntary] = "No" )
```

### Average Headcount (12m)

Mean of the 12 month-end headcounts in the window.

Format: `#,0.0`

```dax
Average Headcount (12m) =
VAR _end = [Ref Date]
VAR _start = EOMONTH ( _end, -12 )
VAR _months =
    FILTER (
        ALL ( 'Reporting Date'[Month End] ),
        'Reporting Date'[Month End] > _start && 'Reporting Date'[Month End] <= _end
    )
RETURN
    AVERAGEX (
        _months,
        VAR _m = 'Reporting Date'[Month End]
        RETURN
            CALCULATE (
                DISTINCTCOUNT ( FactStaffMonthly[Staff ID] ),
                REMOVEFILTERS ( DimDate ),
                FactStaffMonthly[Month End] = _m
            )
    )
```

### Turnover Rate (12m)

Exits in the 12 months divided by the mean headcount of the same months.

Format: `0.0%`

```dax
Turnover Rate (12m) =
VAR _end = [Ref Date]
VAR _firstMonth = EOMONTH ( _end, -11 )
RETURN
    IF ( _firstMonth < [First Data Month], BLANK (), DIVIDE ( [Exits (12m)], [Average Headcount (12m)] ) )
```

### Voluntary Turnover Rate (12m)

Voluntary exits divided by mean headcount.

Format: `0.0%`

```dax
Voluntary Turnover Rate (12m) =
VAR _end = [Ref Date]
VAR _firstMonth = EOMONTH ( _end, -11 )
RETURN
    IF ( _firstMonth < [First Data Month], BLANK (), DIVIDE ( [Voluntary Exits (12m)], [Average Headcount (12m)] ) )
```

### Non-voluntary Turnover Rate (12m)

Non-voluntary exits divided by mean headcount.

Format: `0.0%`

```dax
Non-voluntary Turnover Rate (12m) =
VAR _end = [Ref Date]
VAR _firstMonth = EOMONTH ( _end, -11 )
RETURN
    IF ( _firstMonth < [First Data Month], BLANK (), DIVIDE ( [Non-voluntary Exits (12m)], [Average Headcount (12m)] ) )
```

### Appraisal Eligible Staff

Staff present at the reference date with at least 6 months of service.

Format: `#,0`

```dax
Appraisal Eligible Staff =
VAR _end = [Ref Date]
RETURN
    CALCULATE (
        DISTINCTCOUNT ( FactStaffMonthly[Staff ID] ),
        REMOVEFILTERS ( DimDate ),
        FactStaffMonthly[Month End] = _end,
        FactStaffMonthly[Start Date] <= EOMONTH ( _end, -6 )
    )
```

### Appraisal Completion

Eligible staff with an appraisal dated in the 12 months to the reference date, divided by eligible staff.

Format: `0.0%`

```dax
Appraisal Completion =
VAR _end = [Ref Date]
VAR _start = EOMONTH ( _end, -12 )
VAR _firstAppraisal = CALCULATE ( MIN ( FactAppraisals[Appraisal Date] ), REMOVEFILTERS () )
VAR _eligible =
    CALCULATETABLE (
        VALUES ( FactStaffMonthly[Staff ID] ),
        REMOVEFILTERS ( DimDate ),
        FactStaffMonthly[Month End] = _end,
        FactStaffMonthly[Start Date] <= EOMONTH ( _end, -6 )
    )
VAR _appraised =
    CALCULATETABLE (
        VALUES ( FactAppraisals[Staff ID] ),
        REMOVEFILTERS ( DimDate ),
        FactAppraisals[Appraisal Date] > _start,
        FactAppraisals[Appraisal Date] <= _end
    )
RETURN
    IF (
        _end < EOMONTH ( _firstAppraisal, 12 ),
        BLANK (),
        DIVIDE ( COUNTROWS ( INTERSECT ( _eligible, _appraised ) ), COUNTROWS ( _eligible ) )
    )
```

## 08 Contracts

### Contracts in Force

Contracts in force at the reference month-end.

Format: `#,0`

```dax
Contracts in Force =
VAR _d = [Ref Date]
RETURN
    IF (
        ISBLANK ( _d ),
        BLANK (),
        CALCULATE (
            COUNTROWS ( FactContracts ),
            REMOVEFILTERS ( DimDate ),
            FILTER (
            ALL ( FactContracts[Start Date], FactContracts[End Date] ),
            FactContracts[Start Date] <= _d
                && ( ISBLANK ( FactContracts[End Date] ) || FactContracts[End Date] >= _d )
        )
        ) + 0
    )
```

### Avg Current Contract Duration G3/G4 (months)

Mean granted months of the International G3 and G4 contracts in force at the reference date. Open-ended contracts have no duration and are skipped.

Format: `0.0`

```dax
Avg Current Contract Duration G3/G4 (months) =
VAR _d = [Ref Date]
RETURN
    CALCULATE (
        AVERAGE ( FactContracts[Granted Months] ),
        REMOVEFILTERS ( DimDate ),
        KEEPFILTERS ( DimGrade[Staff Type] = "International" ),
        KEEPFILTERS ( DimGrade[Grade] IN { "G3", "G4" } ),
        FILTER (
            ALL ( FactContracts[Start Date], FactContracts[End Date] ),
            FactContracts[Start Date] <= _d
                && ( ISBLANK ( FactContracts[End Date] ) || FactContracts[End Date] >= _d )
        )
    )
```

### Avg Granted Duration New Joiners G3/G4 (months)

Mean granted months of the first contracts of International G3 and G4 staff that started in the 12 months to the reference date.

Format: `0.0`

```dax
Avg Granted Duration New Joiners G3/G4 (months) =
VAR _end = [Ref Date]
VAR _start = EOMONTH ( _end, -12 )
RETURN
    CALCULATE (
        AVERAGE ( FactContracts[Granted Months] ),
        REMOVEFILTERS ( DimDate ),
        KEEPFILTERS ( DimGrade[Staff Type] = "International" ),
        KEEPFILTERS ( DimGrade[Grade] IN { "G3", "G4" } ),
        FactContracts[Is New Joiner Contract] = TRUE (),
        FactContracts[Start Date] > _start,
        FactContracts[Start Date] <= _end
    )
```

### Contracts Ending Within 4 Months

International contracts in force whose end date falls after the reference date and within the next 4 months.

Format: `#,0`

```dax
Contracts Ending Within 4 Months =
VAR _d = [Ref Date]
RETURN
    IF (
        ISBLANK ( _d ),
        BLANK (),
        CALCULATE (
            COUNTROWS ( FactContracts ),
            REMOVEFILTERS ( DimDate ),
            KEEPFILTERS ( DimGrade[Staff Type] = "International" ),
            FILTER (
                ALL ( FactContracts[Start Date], FactContracts[End Date] ),
                FactContracts[Start Date] <= _d
                    && FactContracts[End Date] > _d
                    && FactContracts[End Date] <= EOMONTH ( _d, 4 )
            )
        ) + 0
    )
```

### Contracts Ending Within 4 Months %

Contracts ending within 4 months divided by International headcount at the reference date.

Format: `0.0%`

```dax
Contracts Ending Within 4 Months % =
DIVIDE ( [Contracts Ending Within 4 Months], CALCULATE ( [Headcount], KEEPFILTERS ( DimGrade[Staff Type] = "International" ) ) )
```

### Days Remaining

Days from the reference date to the end of a contract. Blank unless the International contract ends within the next 4 months, so a table of contracts lists only those.

Format: `0`

```dax
Days Remaining =
VAR _d = [Ref Date]
VAR _end = MAX ( FactContracts[End Date] )
VAR _start = MIN ( FactContracts[Start Date] )
VAR _isInternational =
    CALCULATE ( COUNTROWS ( FactContracts ), KEEPFILTERS ( DimGrade[Staff Type] = "International" ) ) > 0
RETURN
    IF (
        _isInternational && _start <= _d && _end > _d && _end <= EOMONTH ( _d, 4 ),
        DATEDIFF ( _d, _end, DAY )
    )
```

## 09 Data quality

### DQ Issues

Rows in DQ_Issues in the current filter context.

Format: `#,0`

```dax
DQ Issues =
COUNTROWS ( DQ_Issues ) + 0
```

### Recon Historical Headcount

Staff in the legacy snapshot for an overlap month.

Format: `#,0`

```dax
Recon Historical Headcount =
CALCULATE ( DISTINCTCOUNT ( Recon_Overlap[Staff ID] ), Recon_Overlap[Source] = "Historical" )
```

### Recon Current Headcount

Staff derived from CORE and the trackers for an overlap month.

Format: `#,0`

```dax
Recon Current Headcount =
CALCULATE ( DISTINCTCOUNT ( Recon_Overlap[Staff ID] ), Recon_Overlap[Source] = "Current" )
```

### Recon Difference

Historical minus current headcount for an overlap month.

Format: `+#,0;-#,0;0`

```dax
Recon Difference =
[Recon Historical Headcount] - [Recon Current Headcount]
```

### Expatriate Count Difference

Expatriates from the deployment log minus expatriates from the monthly snapshots.

Format: `+#,0;-#,0;0`

```dax
Expatriate Count Difference =
[Expatriates (deployment log)] - [Expatriates]
```

### Last Refresh

Date and time of the last data refresh.

Format: `yyyy-mm-dd hh:mm`

```dax
Last Refresh =
MAX ( 'Refresh Info'[Last Refresh] )
```

### Data Through

Last month-end loaded.

Format: `yyyy-mm-dd`

```dax
Data Through =
MAX ( 'Refresh Info'[Data Through] )
```
