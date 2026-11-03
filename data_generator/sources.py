"""Turn the simulated truth into the files each source system would export."""
from datetime import date, timedelta

import numpy as np
import pandas as pd

import config as C
import reference as R
import workforce as W

TRACKER_LAYOUTS = {
    # layout: sheet name, header row (1-based), column names, date style
    "A": dict(sheet="National Staff", header_row=3, title="{c} country office - National Staff Tracker", dates="excel",
              cols=["Staff ID", "Sex", "Date of Birth", "Nationality", "Grade", "Contract Type", "Team", "Start Date",
                    "End Date", "Exit Reason", "Voluntary", "Last Appraisal"]),
    "B": dict(sheet="Staff List", header_row=1, title=None, dates="text",
              cols=["ID No.", "Gender", "DOB", "Nationality", "Level", "Contract", "Department", "Entry Date",
                    "Departure Date", "Reason for Leaving", "Resigned (Y/N)", "Last Appraisal Date"]),
    "C": dict(sheet="Tracker", header_row=2, title="Country office tracker", dates="excel", footer=True,
              cols=["Employee Number", "Sex", "Birth Date", "Country of Origin", "Grade", "Type of Contract", "Unit",
                    "Contract Start", "Contract End", "Exit Type", "Voluntary Exit", "Appraisal Date"]),
    "D": dict(sheet="NS", header_row=5, title="Meridian Field Research\nNational staff list\nMaintained by country HR\nDo not edit headers",
              dates="excel",
              cols=["Staff ID", "Gender", "Date of birth", "Nationality", "Grade", "Contract type", "Team",
                    "Start date", "End date", "Reason for exit", "Voluntary", "Last appraisal date"]),
}
TRACKER_STD = ["staff_id", "gender", "date_of_birth", "nationality", "grade", "contract_type", "team", "start_date",
               "end_date", "exit_reason", "voluntary_exit", "last_appraisal_date"]
COUNTRY_LAYOUT = {"Kenya": "A", "Somalia": "A", "South Sudan": "A", "Mali": "A",
                  "Nigeria": "B", "Niger": "B", "Iraq": "B", "Colombia": "B",
                  "DR Congo": "C", "Syria": "C", "Afghanistan": "C", "Haiti": "C",
                  "Ukraine": "D", "Bangladesh": "D"}
TRACKER_FILE_NAME = {"DR Congo": "DRC"}   # file names use the short form HR people type

LEGACY_CONTRACT = {"Fixed-term": "Fixed Term", "Short-term": "Short Term", "Consultancy": "Consultant",
                   "Open-ended": "Permanent"}
LEGACY_CATEGORY = {"National": "Local", "International": "Expat", "HQ": "HQ-based"}
LEGACY_SEX = {"Female": "F", "Male": "M", "Other": "X"}
LEGACY_OUTCOME = {"National Recruitment": "Local hire", "External Recruitment": "External hire",
                  "Internal Mobility": "Internal move", "Cancelled Position": "Cancelled"}
LEGACY_CANDIDATE = {"External": "External", "Current staff": "Internal", "Former staff": "Ex-staff"}
LEGACY_REASON = {"New Position": "New post", "Replacement": "Replacement"}


def iso(d):
    return None if d is None or (isinstance(d, float) and np.isnan(d)) else d.isoformat()


def staff_table(emps):
    rows = []
    for e in emps:
        if e["start"] > C.EXPORT_DATE:
            continue
        rows.append(dict(staff_id=e["staff_id"], kind=e["kind"], country=e["country"], unit=e["unit"],
                         gender=e["gender"], dob=e["dob"], nationality=e["nationality"], start=e["start"],
                         end=e["end"], exit_reason=e["exit_reason"], voluntary=e["voluntary"],
                         grade_now=e["grade_now"], ctype_now=e["ctype_now"]))
    return pd.DataFrame(rows)


def last_appraisal(appr):
    df = pd.DataFrame(appr)
    return df.groupby("staff_id")["appraisal_date"].max().to_dict()


def core_frames(rng, staff, contracts, appraisals):
    """CORE HRIS exports: International and HQ staff, plus a few nationals loaded early in two pilot countries."""
    last = last_appraisal(appraisals)
    active = staff[(staff["end"].isna()) | (staff["end"] >= date(2025, 1, 1))]
    core = active[active["kind"] != "National"]
    pilot = active[(active["kind"] == "National") & active["country"].isin(["Kenya", "Colombia"])]
    dupes = pilot.sample(n=C.DUPLICATES_TRACKER_CORE, random_state=int(rng.integers(0, 2**31 - 1)))
    core = pd.concat([core, dupes]).sort_values("staff_id")
    cat = {"National": "National", "International": "International", "HQ": "HQ"}
    out = pd.DataFrame({
        "staff_id": core["staff_id"], "date_of_birth": core["dob"], "gender": core["gender"],
        "nationality": core["nationality"], "staff_category": core["kind"].map(cat),
        "contract_type": core["ctype_now"], "grade": core["grade_now"], "duty_country": core["country"],
        "team": core["unit"], "start_date": core["start"], "end_date": core["end"],
        "exit_reason": core["exit_reason"], "voluntary_exit": core["voluntary"],
        "last_appraisal_date": core["staff_id"].map(last)})
    ids = set(out["staff_id"])
    cdf = pd.DataFrame(contracts)
    cdf = cdf[cdf["staff_id"].isin(ids)]
    cdf = cdf[cdf["end_date"].isna() | (cdf["end_date"] >= date(2025, 1, 1))]
    cdf = cdf.drop(columns=["is_first"]).reset_index(drop=True)
    adf = pd.DataFrame(appraisals)
    return out.reset_index(drop=True), cdf, adf, set(dupes["staff_id"])


def tracker_frames(staff, appraisals, contracts):
    last = last_appraisal(appraisals)
    nat = staff[(staff["kind"] == "National") & ((staff["end"].isna()) | (staff["end"] >= date(2025, 1, 1)))]
    out = {}
    for country, g in nat.groupby("country"):
        df = pd.DataFrame({
            "staff_id": g["staff_id"], "gender": g["gender"], "date_of_birth": g["dob"],
            "nationality": g["nationality"], "grade": g["grade_now"], "contract_type": g["ctype_now"],
            "team": g["unit"], "start_date": g["start"], "end_date": g["end"], "exit_reason": g["exit_reason"],
            "voluntary_exit": g["voluntary"], "last_appraisal_date": g["staff_id"].map(last)})
        out[country] = df.sort_values("staff_id").reset_index(drop=True)
    return out


def snapshot_frame(staff, contracts, me):
    """Month-end snapshot as the legacy system kept it."""
    c = contracts[(contracts["start_date"] <= me) & (contracts["end_date"].isna() | (contracts["end_date"] >= me))]
    df = c.merge(staff[["staff_id", "kind", "gender", "dob", "nationality", "start"]], on="staff_id")
    return pd.DataFrame({
        "Snapshot Date": me, "Staff No": df["staff_id"], "Sex": df["gender"].map(LEGACY_SEX),
        "Birth Date": df["dob"], "Nationality": df["nationality"], "Category": df["kind"].map(LEGACY_CATEGORY),
        "Grade": df["grade"], "Location": df["duty_country"], "Unit": df["team"],
        "Contract": df["contract_type"].map(LEGACY_CONTRACT), "Start Date": df["start"]})


def historical_snapshots(staff, contracts):
    cdf = pd.DataFrame(contracts)
    out = {}
    for me in W.month_ends(C.START, date(2025, 1, 31)):
        out[me] = snapshot_frame(staff, cdf, me)
    return out


def leavers_log(staff):
    x = staff[(staff["end"].notna()) & (staff["end"] <= C.CUTOVER)]
    return pd.DataFrame({"Staff No": x["staff_id"], "Leaving Date": x["end"],
                         "Reason": x["exit_reason"].map(R.LEGACY_EXIT_LABELS),
                         "Voluntary": x["voluntary"].map({"Y": "Yes", "N": "No"})}).sort_values("Leaving Date")


def expat_log(staff):
    x = staff[(staff["kind"] == "International") & (staff["nationality"] != staff["country"]) &
              (staff["start"] <= C.CUTOVER) & (staff["end"].isna() | (staff["end"] >= C.START))]
    to = x["end"].where(x["end"].notna() & (x["end"] <= C.CUTOVER))
    return pd.DataFrame({"Staff No": x["staff_id"], "Nationality": x["nationality"], "Posted To": x["country"],
                         "From": x["start"], "To": to}).sort_values(["From", "Staff No"])


def vacancy_log(vacs):
    rows = []
    for v in vacs:
        if v["opened"] > C.CUTOVER:
            continue
        closed = v["closed"] if (v["closed"] is not None and v["closed"] <= C.CUTOVER) else None
        done = closed is not None
        rows.append({"Vacancy Ref": f"VAC-H-{v['seq']:05d}", "Country": v["country"], "Grade": v["grade"],
                     "Reason": LEGACY_REASON[v["opening_reason"]], "Date Opened": v["opened"],
                     "Planned Start": v["planned_start"], "Planned Months": v["planned_months"],
                     "Date Closed": closed,
                     "Outcome": LEGACY_OUTCOME[v["outcome"]] if done else None,
                     "Candidate": LEGACY_CANDIDATE.get(v["candidate_type"]) if done else None,
                     "_seq": v["seq"], "_true_closed": v["closed"]})
    return pd.DataFrame(rows)


def surge_log(surges):
    rows = []
    for s in surges:
        if s["created"] > C.CUTOVER:
            continue
        filled = s["filled"] if (s["filled"] is not None and s["filled"] <= C.CUTOVER) else None
        status = s["status"]
        if status == "Filled" and filled is None:
            status = "Open"
        rows.append({"Request No": f"SRG-H-{s['seq']:04d}", "Date Requested": s["created"], "Country": s["country"],
                     "Grade": s["grade"], "Filled By": {"National": "Local", "International": "Expat"}[s["filled_by"]]
                     if filled and s["filled_by"] else None,
                     "Date Filled": filled, "Duration (months)": s["planned_months"], "Status": status})
    return pd.DataFrame(rows)


def jira_frame(rng, vacs, surges, vlog):
    rows = []
    mig_candidates = vlog[vlog["Date Closed"].isna() & (vlog["_true_closed"].isna() | (vlog["_true_closed"] >= date(2025, 1, 1)))]
    orphans = set(mig_candidates.sample(n=6, random_state=int(rng.integers(0, 2**31 - 1)))["_seq"]) if len(mig_candidates) > 6 else set()
    migrated = {int(r["_seq"]): r["Vacancy Ref"] for _, r in mig_candidates.iterrows() if r["_seq"] not in orphans}

    for v in vacs:
        legacy = migrated.get(v["seq"])
        if v["opened"] < date(2025, 1, 1) and legacy is None:
            continue
        created = v["opened"]
        if legacy:
            created = min(date(2025, 1, 6) + timedelta(days=int(rng.integers(0, 19))), v["closed"] or date(2025, 1, 24))
        status = v["status"]
        if status == "Open":
            status = "In Progress" if rng.random() < 0.6 else "Open"
        rows.append(dict(issue_key=None, issue_type="Vacancy", created=created, resolved=v["closed"], status=status,
                         country=v["country"], grade=v["grade"], opening_reason=v["opening_reason"],
                         planned_duration_months=v["planned_months"], planned_start_date=v["planned_start"],
                         closure_outcome=v["outcome"], candidate_type=v["candidate_type"],
                         filled_by_staff_type=v["filled_by"], time_to_done_hours=v["time_to_done_hours"],
                         reopened_count=0, legacy_vacancy_ref=legacy))
    for s in surges:
        if s["created"] < date(2025, 1, 1):
            continue
        rows.append(dict(issue_key=None, issue_type="Surge", created=s["created"], resolved=s["filled"] if s["status"] != "Open" else None,
                         status={"Filled": "Done", "Cancelled": "Cancelled", "Open": "In Progress"}[s["status"]],
                         country=s["country"], grade=s["grade"], opening_reason=None,
                         planned_duration_months=s["planned_months"], planned_start_date=s["planned_start"],
                         closure_outcome={"Filled": "Filled", "Cancelled": "Cancelled Position", "Open": None}[s["status"]],
                         candidate_type=None, filled_by_staff_type=s["filled_by"],
                         time_to_done_hours=round(float(rng.lognormal(np.log(14), 0.7)), 1),
                         reopened_count=0, legacy_vacancy_ref=None))
    df = pd.DataFrame(rows).sort_values(["created", "issue_type"], kind="stable").reset_index(drop=True)
    df["issue_key"] = [f"HRREC-{1000 + i}" for i in range(len(df))]
    return df, sorted(orphans)


def stamp_jira(rng, df):
    """Add a time of day to the date columns, as JIRA exports do."""
    df = df.copy()
    for col, (h0, h1) in (("created", (8, 13)), ("resolved", (13, 19))):
        df[col] = [f"{d.isoformat()} {int(rng.integers(h0, h1)):02d}:{int(rng.integers(0, 60)):02d}"
                   if d is not None and not pd.isna(d) else None for d in df[col]]
    return df
