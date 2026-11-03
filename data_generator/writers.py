"""Write the source files. Excel files are written with fixed timestamps so reruns are byte-identical."""
import io
import re
import zipfile
from datetime import date, datetime
from pathlib import Path

import pandas as pd
from openpyxl import Workbook

import config as C
import reference as R
from sources import (COUNTRY_LAYOUT, TRACKER_FILE_NAME, TRACKER_LAYOUTS, TRACKER_STD)

STAMP = datetime(2026, 11, 1, 9, 0, 0)


def _save(wb, path):
    wb.properties.creator = "MFR People & Culture"
    wb.properties.lastModifiedBy = "MFR People & Culture"
    wb.properties.created = STAMP
    wb.properties.modified = STAMP
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(buf) as zin, zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zout:
        for name in sorted(zin.namelist()):
            zi = zipfile.ZipInfo(name, date_time=(2026, 11, 1, 9, 0, 0))
            zi.compress_type = zipfile.ZIP_DEFLATED
            zi.external_attr = 0o644 << 16
            data = zin.read(name)
            if name == "docProps/core.xml":
                data = re.sub(rb"(<dcterms:modified[^>]*>)[^<]*(</dcterms:modified>)", rb"\g<1>2026-11-01T09:00:00Z\g<2>", data)
            zout.writestr(zi, data)


def _cell(v):
    if v is None or (isinstance(v, float) and pd.isna(v)) or v is pd.NaT:
        return None
    if isinstance(v, pd.Timestamp):
        return v.date()
    return v


def _sheet(ws, header, rows, date_cols=()):
    ws.append(header)
    for r in rows:
        ws.append([_cell(x) for x in r])
    for j, h in enumerate(header, 1):
        if h in date_cols:
            for row in ws.iter_rows(min_row=2, min_col=j, max_col=j):
                for c in row:
                    if isinstance(c.value, date):
                        c.number_format = "yyyy-mm-dd"


def write_reference():
    d = C.DATA / "reference"
    wb = Workbook(); ws = wb.active; ws.title = "Grade_StaffType"
    _sheet(ws, ["Grade", "Staff Type", "Band", "Sort"], R.GRADES)
    ws = wb.create_sheet("Unit_Scope")
    _sheet(ws, ["Unit", "Scope"], [(u, "Country") for u in R.COUNTRY_UNITS] +
           [(u, "Global") for u in R.GLOBAL_UNITS] +
           [(u, "HQ") for u in R.HQ_UNITS if u not in R.GLOBAL_UNITS])
    ws = wb.create_sheet("Legacy_Labels")
    _sheet(ws, ["Legacy Label", "Staff Type"], R.LEGACY_LABELS)
    ws = wb.create_sheet("Contract_Labels")
    _sheet(ws, ["Label", "Contract Type"],
           [(c[0], c[0]) for c in R.CONTRACT_TYPES] +
           [("Fixed Term", "Fixed-term"), ("Short Term", "Short-term"), ("Consultant", "Consultancy"), ("Permanent", "Open-ended")])
    ws = wb.create_sheet("Contract_Types")
    _sheet(ws, ["Contract Type", "Sort", "Has End Date"], R.CONTRACT_TYPES)
    ws = wb.create_sheet("Gender_Labels")
    _sheet(ws, ["Label", "Gender"], [("F", "Female"), ("Female", "Female"), ("M", "Male"), ("Male", "Male"),
                                     ("X", "Other"), ("Other", "Other")])
    ws = wb.create_sheet("Population_Rules")
    _sheet(ws, ["Order", "Condition", "Population Detail", "Population"],
           [(1, "Duty country is the HQ country", "Global - HQ", "Global"),
            (2, "Staff Type = International and unit scope = Global", "Global - Field", "Global"),
            (3, "Staff Type = International", "International", "International"),
            (4, "Staff Type = National", "National", "National")])
    _save(wb, d / "staff_category_mapping.xlsx")

    wb = Workbook(); ws = wb.active; ws.title = "Nationality_GNGS"
    _sheet(ws, ["Nationality", "GN/GS"], R.NATIONALITIES)
    _save(wb, d / "gn_gs_nationality.xlsx")

    wb = Workbook(); ws = wb.active; ws.title = "Countries"
    _sheet(ws, ["Country", "ISO3", "Region", "Is HQ", "Office Status"],
           [(c[0], c[1], c[2], c[0] == C.HQ_COUNTRY, c[3]) for c in R.COUNTRIES])
    ws = wb.create_sheet("Variants")
    _sheet(ws, ["Variant", "Country"], [(v, k) for k, vs in R.COUNTRY_VARIANTS.items() for v in vs])
    _save(wb, d / "country_list.xlsx")

    aliases = []
    for lay in TRACKER_LAYOUTS.values():
        for h, std in zip(lay["cols"], TRACKER_STD):
            aliases.append((h.strip().lower(), std))
    seen, rows = set(), []
    for a, s in aliases:
        if (a, s) not in seen:
            seen.add((a, s)); rows.append((a, s))
    wb = Workbook(); ws = wb.active; ws.title = "Aliases"
    _sheet(ws, ["Alias", "Standard Column"], rows)
    _save(wb, d / "tracker_column_map.xlsx")

    wb = Workbook(); ws = wb.active; ws.title = "Labels"
    from sources import LEGACY_CANDIDATE, LEGACY_OUTCOME, LEGACY_REASON
    rows = [("Reason", v, k) for k, v in LEGACY_REASON.items()] + \
           [("Outcome", v, k) for k, v in LEGACY_OUTCOME.items()] + \
           [("Candidate", v, k) for k, v in LEGACY_CANDIDATE.items()]
    _sheet(ws, ["Field", "Legacy Label", "Standard Label"], rows)
    _save(wb, d / "vacancy_label_mapping.xlsx")


def write_core(f):
    d = C.DATA / "core_hris"; d.mkdir(parents=True, exist_ok=True)
    f["core_staff"].to_csv(d / "core_staff_export.csv", index=False)
    cc = f["core_contracts"][["contract_id", "staff_id", "contract_type", "grade", "duty_country", "team",
                              "start_date", "end_date", "granted_months"]].copy()
    cc["granted_months"] = cc["granted_months"].astype("Int64")
    cc.to_csv(d / "core_contracts_export.csv", index=False)
    f["core_appraisals"].to_csv(d / "core_appraisals_export.csv", index=False)


def write_jira(df):
    d = C.DATA / "jira"; d.mkdir(parents=True, exist_ok=True)
    df = df.copy()
    df["planned_duration_months"] = df["planned_duration_months"].astype("Int64")
    df["reopened_count"] = df["reopened_count"].astype("Int64")
    df.to_csv(d / "jira_recruitment_export.csv", index=False)


def _txt(d):
    return d.strftime("%d/%m/%Y") if isinstance(d, date) and not pd.isna(d) else None


def write_trackers(trackers):
    d = C.DATA / "country_trackers"
    for country, df in trackers.items():
        lay = TRACKER_LAYOUTS[COUNTRY_LAYOUT[country]]
        wb = Workbook(); ws = wb.active; ws.title = lay["sheet"]
        top = lay["header_row"] - 1
        title_lines = (lay["title"] or "").format(c=country).split("\n") if lay["title"] else []
        for i in range(top):
            ws.append([title_lines[i] if i < len(title_lines) else None])
        body = df.copy()
        gender = {"Female": "F", "Male": "M", "Other": "X"}
        if COUNTRY_LAYOUT[country] in ("A", "C", "D"):
            body["gender"] = body["gender"].map(gender)
        vol = {"Y": "Y", "N": "N"}
        if COUNTRY_LAYOUT[country] == "B":
            vol = {"Y": "Yes", "N": "No"}
        elif COUNTRY_LAYOUT[country] == "C":
            vol = {"Y": "TRUE", "N": "FALSE"}
        body["voluntary_exit"] = body["voluntary_exit"].map(vol)
        date_cols = ["date_of_birth", "start_date", "end_date", "last_appraisal_date"]
        if lay["dates"] == "text":
            for c in date_cols:
                body[c] = body[c].map(_txt)
        ws.append(lay["cols"])
        for r in body[TRACKER_STD].itertuples(index=False):
            ws.append([_cell(x) for x in r])
        if lay["dates"] == "excel":
            for j, name in enumerate(TRACKER_STD, 1):
                if name in date_cols:
                    for row in ws.iter_rows(min_row=lay["header_row"] + 1, min_col=j, max_col=j):
                        for c in row:
                            if isinstance(c.value, date):
                                c.number_format = "yyyy-mm-dd"
        if lay.get("footer"):
            ws.append([])
            ws.append([f"Total staff: {len(body)}"])
        fname = TRACKER_FILE_NAME.get(country, country)
        _save(wb, d / f"NS_tracker_{fname}.xlsx")


def write_historical(f):
    d = C.DATA / "historical"
    snaps = f["hist_snap"]
    groups = {"Staff_Snapshots_2022.xlsx": 2022, "Staff_Snapshots_2023.xlsx": 2023, "Staff_Snapshots_2024.xlsx": 2024,
              "Staff_Snapshots_2025_Jan.xlsx": 2025}
    header = ["Snapshot Date", "Staff No", "Sex", "Birth Date", "Nationality", "Category", "Grade", "Location", "Unit",
              "Contract", "Start Date"]
    for fname, year in groups.items():
        wb = Workbook(write_only=True)
        ws = wb.create_sheet("Snapshot")
        ws.append(header)
        for me in sorted(k for k in snaps if k.year == year):
            s = snaps[me].sort_values("Staff No")
            for r in s[header].itertuples(index=False):
                row = [_cell(x) for x in r]
                if year == 2022:
                    row[3] = _txt(row[3]) if row[3] is not None else None
                ws.append(row)
        _save_ro(wb, d / fname)
    for fname, sheet, df, dcols in [
        ("Vacancy_Log_2022_2024.xlsx", "Vacancies", f["hist_vac"].drop(columns=["_seq", "_true_closed"]), None),
        ("Surge_Log_2022_2024.xlsx", "Surges", f["hist_surge"], None),
        ("Expatriation_Log_2022_2024.xlsx", "Deployments", f["hist_expat"], None),
        ("Leavers_Log_2022_2024.xlsx", "Leavers", f["hist_leavers"], None)]:
        wb = Workbook(); ws = wb.active; ws.title = sheet
        _sheet(ws, list(df.columns), df.itertuples(index=False),
               date_cols=[c for c in df.columns if c.startswith("Date") or c in ("Planned Start", "From", "To", "Leaving Date")])
        _save(wb, d / fname)


def _save_ro(wb, path):
    # write-only workbooks cannot be re-read, so set properties before saving
    _save(wb, path)
