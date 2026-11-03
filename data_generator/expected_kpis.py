"""Reference KPI values for tests/expected_kpis.csv, computed in pandas from the source files.

Every row is one KPI under one filter at one reporting date. tests/validation_queries.dax holds the matching
DAX queries, one per row, in the same order.
"""
import numpy as np
import pandas as pd

import pandas_model as M

RD = pd.Timestamp(2026, 10, 31)
PY = pd.Timestamp(2025, 10, 31)

FILTERS = {
    "none": {},
    "Population=National": {"population": "National"},
    "Population=International": {"population": "International"},
    "Population=Global": {"population": "Global"},
    "Population Detail=Global - HQ": {"population_detail": "Global - HQ"},
    "Staff Type=International": {"staff_type": "International"},
    "Country=Kenya": {"country": "Kenya"},
    "Country=South Sudan": {"country": "South Sudan"},
    "Country=Ukraine": {"country": "Ukraine"},
}


def sel(df, flt):
    for col, val in FILTERS[flt].items():
        df = df[df[col] == val]
    return df


def staff_at(rd, flt):
    f = M.staff_monthly()
    return sel(f[f["month_end"] == rd], flt)


def headcount(rd, flt):
    return staff_at(rd, flt)["staff_id"].nunique()


def vacancy_rate(rd, flt, due=False):
    vm = M.vacancy_monthly()
    vm = vm[vm["month_end"] == rd]
    vm = sel(vm, flt) if "population" not in FILTERS[flt] and "population_detail" not in FILTERS[flt] else vm
    f = M.staff_monthly()
    f = f[f["month_end"] == rd]
    # Population and nationality filters do not apply to the staff side of a vacancy rate
    flt_vac = {k: v for k, v in FILTERS[flt].items() if k not in ("population", "population_detail")}
    for col, val in flt_vac.items():
        f = f[f[col] == val]
        vm = vm[vm[col] == val] if col in vm else vm
    open_n = (vm["is_due"] if due else vm["vacancy_id"].notna()).sum()
    return open_n / (f["staff_id"].nunique() + vm["vacancy_id"].nunique())


def retention(rd):
    f = M.staff_monthly()
    start = M.eomonth(rd, -12)
    a = set(f.loc[f["month_end"] == start, "staff_id"])
    b = set(f.loc[f["month_end"] == rd, "staff_id"])
    return len(a & b) / len(a)


def avg_headcount(rd):
    f = M.staff_monthly()
    mes = [m for m in M.month_ends(M.eomonth(rd, -12), rd) if m > M.eomonth(rd, -12)]
    return np.mean([f.loc[f["month_end"] == m, "staff_id"].nunique() for m in mes])


def exits12(rd, voluntary=None):
    e = M.exits()
    e = e[(e["exit_date"] > M.eomonth(rd, -12)) & (e["exit_date"] <= rd)]
    if voluntary is not None:
        e = e[e["voluntary"] == voluntary]
    return len(e)


def appraisal_completion(rd):
    f = M.staff_monthly()
    f = f[(f["month_end"] == rd) & (f["emp_start"] <= M.eomonth(rd, -6))]
    a = M.appraisals()
    a = a[(a["appraisal_date"] > M.eomonth(rd, -12)) & (a["appraisal_date"] <= rd)]
    elig = set(f["staff_id"])
    return len(elig & set(a["staff_id"])) / len(elig)


def contracts_in_force(rd):
    c = M.contracts()
    return c[(c["start_date"] <= rd) & (c["end_date"].isna() | (c["end_date"] >= rd))]


def build():
    rows = []

    def add(kpi, flt, rd, value, tol):
        rows.append(dict(kpi=kpi, filter=flt, reporting_date=rd.date().isoformat(), expected_value=value, tolerance=tol))

    for flt in ["none", "Population=National", "Population=International", "Population=Global",
                "Population Detail=Global - HQ", "Country=Kenya", "Country=Ukraine"]:
        add("Headcount", flt, RD, headcount(RD, flt), 0)
    add("Headcount", "none", PY, headcount(PY, "none"), 0)
    add("Headcount", "Country=Ukraine", PY, headcount(PY, "Country=Ukraine"), 0)
    s = staff_at(RD, "none")
    add("Female Share", "none", RD, (s["gender"] == "Female").sum() / len(s), 0.0001)
    add("Average Age", "none", RD, s["age"].mean(), 0.01)
    add("Average Age", "Population=International", RD, staff_at(RD, "Population=International")["age"].mean(), 0.01)
    si = staff_at(RD, "Staff Type=International")
    gs, gn = (si["gn_gs"] == "GS").sum(), (si["gn_gs"] == "GN").sum()
    add("GS Share", "Staff Type=International", RD, gs / (gs + gn), 0.0001)
    add("GS/GN Ratio", "Staff Type=International", RD, gs / gn, 0.0001)
    pyi = staff_at(PY, "Staff Type=International")
    add("GS Share", "Staff Type=International", PY,
        (pyi["gn_gs"] == "GS").sum() / ((pyi["gn_gs"] == "GS").sum() + (pyi["gn_gs"] == "GN").sum()), 0.0001)
    add("Expatriates", "none", RD, int(s["is_expatriate"].sum()), 0)

    vm = M.vacancy_monthly()
    add("Open Vacancies", "none", RD, vm[vm["month_end"] == RD]["vacancy_id"].nunique(), 0)
    add("Vacancy Rate", "none", RD, vacancy_rate(RD, "none"), 0.0001)
    add("Vacancy Rate", "Country=South Sudan", RD, vacancy_rate(RD, "Country=South Sudan"), 0.0001)
    add("Vacancy Rate", "Staff Type=International", RD, vacancy_rate(RD, "Staff Type=International"), 0.0001)
    add("Due Vacancy Rate", "none", RD, vacancy_rate(RD, "none", due=True), 0.0001)
    v = M.vacancies()
    lo = M.eomonth(RD, -12)
    opened = v[(v["opened"] > lo) & (v["opened"] <= RD)]
    add("Avg Planned Duration (months)", "none", RD, opened["planned_months"].mean(), 0.01)
    add("Vacancies Opened (12m)", "none", RD, len(opened), 0)
    closed = v[(v["closed"] > lo) & (v["closed"] <= RD) & v["days_to_close"].notna()]
    add("Avg Days to Close", "none", RD, closed["days_to_close"].mean(), 0.01)
    add("Avg Time to Done (days)", "none", RD, closed["time_to_done_days"].mean(), 0.01)

    add("Retention Rate (12m)", "none", RD, retention(RD), 0.0001)
    add("Retention Rate (12m)", "none", PY, retention(PY), 0.0001)
    add("Exits (12m)", "none", RD, exits12(RD), 0)
    add("Turnover Rate (12m)", "none", RD, exits12(RD) / avg_headcount(RD), 0.0001)
    add("Voluntary Turnover Rate (12m)", "none", RD, exits12(RD, "Y") / avg_headcount(RD), 0.0001)
    add("Appraisal Completion", "none", RD, appraisal_completion(RD), 0.0001)

    c = contracts_in_force(RD)
    g34 = c[(c["staff_type"] == "International") & c["grade"].isin(["G3", "G4"])]
    add("Avg Current Contract Duration G3/G4 (months)", "none", RD, g34["granted_months"].mean(), 0.01)
    allc = M.contracts()
    nj = allc[(allc["staff_type"] == "International") & allc["grade"].isin(["G3", "G4"]) &
              allc["is_new_joiner_contract"] & (allc["start_date"] > lo) & (allc["start_date"] <= RD)]
    add("Avg Granted Duration New Joiners G3/G4 (months)", "none", RD, nj["granted_months"].mean(), 0.01)
    ending = c[(c["staff_type"] == "International") & c["end_date"].notna() &
               (c["end_date"] > RD) & (c["end_date"] <= M.eomonth(RD, 4))]
    add("Contracts Ending Within 4 Months", "none", RD, len(ending), 0)
    add("Contracts Ending Within 4 Months %", "none", RD,
        len(ending) / staff_at(RD, "Staff Type=International")["staff_id"].nunique(), 0.0001)

    sg = M.surges()
    win = sg[(sg["request_date"] > lo) & (sg["request_date"] <= RD)]
    add("Surge Requests (12m)", "none", RD, len(win), 0)
    filled = win[win["status"] == "Filled"]
    add("Surge National Share (12m)", "none", RD, (filled["filled_by"] == "National").sum() / len(filled), 0.0001)

    # data quality counts (rows in DQ_Issues by check)
    cs = M.core_staff()
    tr = M.trackers()
    add("DQ Issues: Duplicate staff ID", "none", RD, len(set(cs["staff_id"]) & set(tr["staff_id"])), 0)
    add("DQ Issues: Contract end before start", "none", RD, int(M.core_contracts()["end_before_start"].sum()), 0)
    j = pd.read_csv(M.DATA / "jira" / "jira_recruitment_export.csv", dtype=str)
    jv = j[j["issue_type"] == "Vacancy"]
    add("DQ Issues: Resolved before created", "none", RD,
        int((M.dates(jv["resolved"]) < M.dates(jv["created"])).sum()), 0)
    # more data-quality counts: rows the DQ_Issues table should hold per check
    f = M.staff_monthly()
    per_staff = f.groupby("staff_id").agg(dob=("date_of_birth", "max"), nat=("nationality", "max"))
    add("DQ Issues: Missing date of birth", "none", RD, int(per_staff["dob"].isna().sum()), 0)
    add("DQ Issues: Missing nationality", "none", RD, int(f.groupby("staff_id")["nationality"].apply(lambda x: x.isna().all()).sum()), 0)
    legacy = M.ref()["legacy"]
    cs2 = M.derive(M.core_staff().copy(), "staff_category")
    core_bad = int((cs2["staff_category"].map(legacy) != cs2["staff_type"]).sum())
    h = M.derive(M.historical_snapshots()[["staff_id", "grade", "label", "country", "unit", "nationality"]].copy(), "label")
    hist_bad = h[h["label"].map(legacy) != h["staff_type"]]["staff_id"].nunique()
    add("DQ Issues: Category label vs grade", "none", RD, core_bad + hist_bad, 0)
    add("DQ Issues: Overlap month mismatch", "none", RD, overlap_mismatch(), 0)
    add("DQ Issues: Legacy vacancy not migrated", "none", RD, orphan_vacancies(), 0)
    add("DQ Issues: Country spelling variant", "none", RD, variant_rows(), 0)
    return pd.DataFrame(rows)


def overlap_mismatch():
    spans = M._span_frame()
    hist = M.historical_snapshots()
    total = 0
    for me in (M.CUTOVER, pd.Timestamp(2025, 1, 31)):
        cur = set(spans[(spans["span_start"] <= me) & (spans["span_end"].isna() | (spans["span_end"] >= me))]["staff_id"])
        old = set(hist[hist["month_end"] == me]["staff_id"])
        total += len(cur ^ old)
    return total


def orphan_vacancies():
    vl = pd.read_excel(M.DATA / "historical" / "Vacancy_Log_2022_2024.xlsx", dtype=object)
    j = pd.read_csv(M.DATA / "jira" / "jira_recruitment_export.csv", dtype=str)
    open_ids = set(vl.loc[vl["Date Closed"].isna(), "Vacancy Ref"])
    return len(open_ids - set(j["legacy_vacancy_ref"].dropna()))


def variant_rows():
    """Rows where a country or nationality value differs from its cleaned form, per source."""
    def differs(series):
        return series.map(lambda v: isinstance(v, str) and v != M.clean_country(v))

    n = 0
    cs = pd.read_csv(M.DATA / "core_hris" / "core_staff_export.csv", dtype=str)
    n += int((differs(cs["duty_country"]) | differs(cs["nationality"])).sum())
    cc = pd.read_csv(M.DATA / "core_hris" / "core_contracts_export.csv", dtype=str)
    n += int(differs(cc["duty_country"]).sum())
    j = pd.read_csv(M.DATA / "jira" / "jira_recruitment_export.csv", dtype=str)
    n += int(differs(j["country"]).sum())
    for p in sorted((M.DATA / "country_trackers").glob("*.xlsx")):
        t = M._read_tracker(p)
        n += int(differs(t["nationality"]).sum())
        n += int(p.stem.replace("NS_tracker_", "") != M.clean_country(p.stem.replace("NS_tracker_", "")))
    for p in sorted((M.DATA / "historical").glob("Staff_Snapshots_*.xlsx")):
        h = pd.read_excel(p, dtype=object)
        n += int((differs(h["Location"]) | differs(h["Nationality"])).sum())
    vl = pd.read_excel(M.DATA / "historical" / "Vacancy_Log_2022_2024.xlsx", dtype=object)
    n += int(differs(vl["Country"]).sum())
    sl = pd.read_excel(M.DATA / "historical" / "Surge_Log_2022_2024.xlsx", dtype=object)
    n += int(differs(sl["Country"]).sum())
    el = pd.read_excel(M.DATA / "historical" / "Expatriation_Log_2022_2024.xlsx", dtype=object)
    n += int((differs(el["Posted To"]) | differs(el["Nationality"])).sum())
    lv = pd.read_excel(M.DATA / "historical" / "Leavers_Log_2022_2024.xlsx", dtype=object)
    n += int((differs(lv["Location"]) | differs(lv["Nationality"])).sum())
    return n


def write_expected_kpis(path):
    df = build()
    df["expected_value"] = df["expected_value"].map(lambda x: round(float(x), 6))
    df.to_csv(path, index=False)
    return df


if __name__ == "__main__":
    print(build().to_string())
