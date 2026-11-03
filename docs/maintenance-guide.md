# Maintenance guide

## Monthly refresh

1. Replace the CORE exports, the JIRA export and the country trackers in the data folder with the latest extracts. Keep the file names.
2. In Power BI Desktop open *Transform data > Manage parameters*. Check `DataFolder` points to the data folder.
3. Set `DataThrough` to the last month-end in the extracts (for example `#date(2026, 11, 30)`). The date table, the Reporting Date slicer and the monthly vacancy rows all extend to this date.
4. Refresh. Open page 9 and compare the issue counts with last month. New checks failing in bulk usually mean a column was renamed in an export.
5. Publish, or share the file.

## Add a country tracker

1. Save the workbook in `data/country_trackers/` as `NS_tracker_<Country>.xlsx`. The country is read from the file name.
2. If the file name is a variant (for example `DRC`), add it to the `Variants` sheet of `reference/country_list.xlsx`.
3. If the country is new, add it to the `Countries` sheet (name, ISO3, region, Is HQ = FALSE, office status).
4. Open the tracker and compare the column headers with `reference/tracker_column_map.xlsx`. For any header not listed, add a row to the `Aliases` sheet: the header text in lower case, and the standard column it maps to (`staff_id`, `gender`, `date_of_birth`, `nationality`, `grade`, `contract_type`, `team`, `start_date`, `end_date`, `exit_reason`, `voluntary_exit`, `last_appraisal_date`).
5. Refresh. The header row is found automatically, so title rows above it and total rows below it are fine. Rows whose Staff ID does not start with `EMP-` are ignored.

## Add a historical year

The legacy files stop at the cut-over (31 Dec 2024), so this is only needed to load older history.

1. Put the new `Staff_Snapshots_<year>.xlsx` in `data/historical/`. Sheet name `Snapshot`, same columns as the existing files.
2. Set `HistoryStart` to the first month-end of the new history. The date table and monthly vacancy rows start there.
3. Add the matching rows to the leavers, vacancy, surge and expatriation logs if they exist.
4. Refresh and check that page 1 shows the new months. The measure `First Data Month` picks the new start automatically.

To move the cut-over itself, change the `CutOver` parameter. Months up to and including it are read from the legacy files, later months from CORE and the trackers.

## Change the category mapping

All rules are in `reference/staff_category_mapping.xlsx`.

| To change | Edit sheet |
|---|---|
| Which grades are National or International | `Grade_StaffType` |
| Which units count as Global | `Unit_Scope` |
| How old category labels map to a staff type | `Legacy_Labels` |
| Spelling of contract types in old files | `Contract_Labels` |
| Old exit reason labels | `Exit_Labels` |

The HQ country is the one with `Is HQ` = TRUE in `country_list.xlsx`. The GN/GS list is `gn_gs_nationality.xlsx`: add a row for a new nationality, otherwise it falls into Unknown. Refresh after any change, then review page 9 for new label conflicts.

## Add a measure

Add it to the `_Measures` table, pick the display folder of the page it belongs to and write a description. Use `[Ref Date]` for any date logic and `REMOVEFILTERS ( DimDate )` when a measure sets its own month-end.

## Rebuild the demonstration data

```
pip install -r requirements.txt
python data_generator/generate.py
pytest
```

The generator uses seed 2026 and rewrites `data/` and `tests/expected_kpis.csv`. Running it twice gives identical files. Settings (countries, headcount targets, rates, planted problem counts) are in `data_generator/config.py`.

## Validate the model

Run each query in `tests/validation_queries.dax` against the open model and compare the `value` column with `tests/expected_kpis.csv`. Record the outcome in `docs/test-log.md`.
