"""The same cleaning and modelling rules as the Power Query layer, written in pandas.

It reads only the files under data/, never the simulation, so its output is an independent check on the model.
Rules (all also documented in docs/data-model.md):
  * country and nationality text is trimmed and mapped through country_list.xlsx / Variants
  * Staff Type comes from the grade scale; Population from country, Staff Type and unit scope
  * month-ends up to and including the cut-over come from the legacy snapshots, later ones from CORE and trackers
  * a staff ID in CORE wins over the same ID in a tracker
  * a contract that ends before it starts gets end = start + granted months - 1 day
  * JIRA tickets resolved before creation are closed on their creation date and excluded from duration measures
  * migrated vacancies keep the opened date of the legacy log
"""
from datetime import date, timedelta
from functools import lru_cache
import calendar

import numpy as np
import pandas as pd

import config as C

DATA = C.DATA
CUTOVER = pd.Timestamp(C.CUTOVER)
DATA_THROUGH = pd.Timestamp(C.EXPORT_DATE)
FIRST_ME = pd.Timestamp(2022, 1, 31)


def eomonth(ts, n=0):
    ts = pd.Timestamp(ts)
    m = ts.year * 12 + ts.month - 1 + n
    y, mo = divmod(m, 12)
    mo += 1
    return pd.Timestamp(y, mo, calendar.monthrange(y, mo)[1])


def edate(ts, n):
    ts = pd.Timestamp(ts)
    m = ts.year * 12 + ts.month - 1 + n
    y, mo = divmod(m, 12)
    mo += 1
    return pd.Timestamp(y, mo, min(ts.day, calendar.monthrange(y, mo)[1]))


def month_ends(first, last):
    out, d = [], eomonth(first)
    while d <= last:
        out.append(d)
        d = eomonth(d, 1)
    return out


def parse_date(v):
    if v is None or (isinstance(v, float) and np.isnan(v)) or v is pd.NaT:
        return pd.NaT
    if isinstance(v, str):
        v = v.strip()
        if not v:
            return pd.NaT
        if "/" in v:
            return pd.to_datetime(v, format="%d/%m/%Y", errors="coerce")
        return pd.to_datetime(v[:10], errors="coerce")
    return pd.Timestamp(v).normalize()


def dates(series):
    return series.map(parse_date).astype("datetime64[ns]")


# ---- reference ----------------------------------------------------------------------------------------------
@lru_cache(maxsize=1)
def ref():
    d = DATA / "reference"
    sc = pd.read_excel(d / "staff_category_mapping.xlsx", sheet_name=None)
    cl = pd.read_excel(d / "country_list.xlsx", sheet_name=None)
    variants = {str(v).strip().lower(): c for v, c in zip(cl["Variants"]["Variant"], cl["Variants"]["Country"])}
    return dict(
        grade=sc["Grade_StaffType"].set_index("Grade"),
        unit_scope=dict(zip(sc["Unit_Scope"]["Unit"], sc["Unit_Scope"]["Scope"])),
        legacy=dict(zip(sc["Legacy_Labels"]["Legacy Label"], sc["Legacy_Labels"]["Staff Type"])),
        contract=dict(zip(sc["Contract_Labels"]["Label"], sc["Contract_Labels"]["Contract Type"])),
        gender=dict(zip(sc["Gender_Labels"]["Label"], sc["Gender_Labels"]["Gender"])),
        exit_labels=dict(zip(sc["Exit_Labels"]["Legacy Label"], sc["Exit_Labels"]["Exit Reason"])),
        countries=cl["Countries"], variants=variants,
        hq=cl["Countries"].loc[cl["Countries"]["Is HQ"].astype(bool), "Country"].iloc[0],
        gngs=dict(zip(*pd.read_excel(d / "gn_gs_nationality.xlsx").T.values)),
        aliases=dict(zip(*pd.read_excel(d / "tracker_column_map.xlsx").T.values)),
        vlabels={(f, l): s for f, l, s in pd.read_excel(d / "vacancy_label_mapping.xlsx").values},
    )


def clean_country(v):
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return None
    t = str(v).strip()
    if not t:
        return None
    return ref()["variants"].get(t.lower(), t)


def derive(df, label_col=None):
    """Staff Type, Population Detail and Population from grade / label, country and unit."""
    r = ref()
    st = df["grade"].map(r["grade"]["Staff Type"])
    if label_col is not None:
        st = st.fillna(df[label_col].map(r["legacy"]))
    df = df.assign(staff_type=st)
    scope = df["unit"].map(r["unit_scope"])
    pd_ = np.where(df["country"] == r["hq"], "Global - HQ",
                   np.where((df["staff_type"] == "International") & (scope == "Global"), "Global - Field",
                            np.where(df["staff_type"] == "International", "International", "National")))
    df["population_detail"] = pd_
    df["population"] = np.where(df["population_detail"].str.startswith("Global"), "Global", df["population_detail"])
    df["gn_gs"] = df["nationality"].map(r["gngs"]).fillna("Unknown")
    return df


# ---- staff ---------------------------------------------------------------------------------------------------
def _read_tracker(path):
    r = ref()
    raw = pd.read_excel(path, header=None, sheet_name=0, dtype=object)
    hdr = None
    for i in range(len(raw)):
        vals = [str(x).strip().lower() for x in raw.iloc[i].tolist() if isinstance(x, str)]
        if any(r["aliases"].get(v) == "staff_id" for v in vals):
            hdr = i
            break
    names = [r["aliases"].get(str(x).strip().lower()) if isinstance(x, str) else None for x in raw.iloc[hdr]]
    df = raw.iloc[hdr + 1:].copy()
    df.columns = names
    df = df.loc[:, [c for c in df.columns if c is not None]]
    df = df[df["staff_id"].astype(str).str.startswith("EMP-")].copy()
    country = clean_country(path.stem.replace("NS_tracker_", ""))
    df["country"] = country
    return df


@lru_cache(maxsize=1)
def core_raw():
    d = DATA / "core_hris"
    staff = pd.read_csv(d / "core_staff_export.csv", dtype=str)
    contracts = pd.read_csv(d / "core_contracts_export.csv", dtype=str)
    appr = pd.read_csv(d / "core_appraisals_export.csv", dtype=str)
    return staff, contracts, appr


@lru_cache(maxsize=1)
def trackers():
    r = ref()
    frames = [_read_tracker(p) for p in sorted((DATA / "country_trackers").glob("*.xlsx"))]
    t = pd.concat(frames, ignore_index=True)
    for c in ("date_of_birth", "start_date", "end_date", "last_appraisal_date"):
        t[c] = dates(t[c])
    t["gender"] = t["gender"].map(r["gender"]).fillna("Other")
    t["voluntary_exit"] = t["voluntary_exit"].map(
        lambda v: None if v is None or (isinstance(v, float) and np.isnan(v)) else
        ("Y" if str(v).strip().upper() in ("Y", "YES", "TRUE") else "N"))
    t["nationality"] = t["nationality"].map(clean_country)
    t = t.rename(columns={"team": "unit"})
    return t


@lru_cache(maxsize=1)
def core_staff():
    s, _, _ = core_raw()
    s = s.copy()
    for c in ("date_of_birth", "start_date", "end_date", "last_appraisal_date"):
        s[c] = dates(s[c])
    s["nationality"] = s["nationality"].map(clean_country)
    s["country"] = s["duty_country"].map(clean_country)
    s = s.rename(columns={"team": "unit"})
    return s


@lru_cache(maxsize=1)
def core_contracts():
    _, c, _ = core_raw()
    c = c.copy()
    c["start_date"] = dates(c["start_date"])
    c["end_date_raw"] = dates(c["end_date"])
    c["granted_months"] = pd.to_numeric(c["granted_months"])
    bad = c["end_date_raw"] < c["start_date"]
    repaired = [edate(s, int(g)) - pd.Timedelta(days=1) if not np.isnan(g) else s
                for s, g in zip(c["start_date"], c["granted_months"])]
    c["end_date"] = np.where(bad, pd.Series(repaired, index=c.index), c["end_date_raw"])
    c["end_date"] = pd.to_datetime(c["end_date"])
    c["end_before_start"] = bad
    c["country"] = c["duty_country"].map(clean_country)
    return c.rename(columns={"team": "unit"})


@lru_cache(maxsize=1)
def historical_snapshots():
    r = ref()
    frames = []
    for p in sorted((DATA / "historical").glob("Staff_Snapshots_*.xlsx")):
        df = pd.read_excel(p, dtype=object)
        frames.append(df)
    h = pd.concat(frames, ignore_index=True)
    h = h.rename(columns={"Snapshot Date": "month_end", "Staff No": "staff_id", "Sex": "gender", "Birth Date": "dob",
                          "Nationality": "nationality", "Category": "label", "Grade": "grade", "Location": "country",
                          "Unit": "unit", "Contract": "contract_type", "Start Date": "start_date"})
    h["month_end"] = dates(h["month_end"])
    h["dob"] = dates(h["dob"])
    h["start_date"] = dates(h["start_date"])
    h["country"] = h["country"].map(clean_country)
    h["nationality"] = h["nationality"].map(clean_country)
    h["gender"] = h["gender"].map(r["gender"]).fillna("Other")
    h["contract_type"] = h["contract_type"].map(r["contract"])
    return h


def _span_frame():
    """Spans for the current period: CORE contracts first, tracker rows for IDs that CORE does not hold."""
    cs, cc = core_staff(), core_contracts()
    st = cs.set_index("staff_id")
    a = cc.merge(cs[["staff_id", "date_of_birth", "gender", "nationality", "staff_category", "start_date"]]
                 .rename(columns={"start_date": "emp_start"}), on="staff_id", how="left")
    a = a.rename(columns={"start_date": "span_start", "end_date": "span_end"})
    a["source"] = "CORE"
    a["label"] = a["staff_category"]
    t = trackers()
    t = t[~t["staff_id"].isin(set(cs["staff_id"]))]
    b = pd.DataFrame({"staff_id": t["staff_id"], "span_start": t["start_date"], "span_end": t["end_date"],
                      "grade": t["grade"], "contract_type": t["contract_type"], "country": t["country"],
                      "unit": t["unit"], "date_of_birth": t["date_of_birth"], "gender": t["gender"],
                      "nationality": t["nationality"], "emp_start": t["start_date"], "source": "Tracker",
                      "label": None})
    cols = ["staff_id", "span_start", "span_end", "grade", "contract_type", "country", "unit", "date_of_birth",
            "gender", "nationality", "emp_start", "source", "label"]
    return pd.concat([a[cols], b[cols]], ignore_index=True)


@lru_cache(maxsize=1)
def staff_monthly():
    h = historical_snapshots()
    hist = h[h["month_end"] <= CUTOVER].rename(columns={"dob": "date_of_birth", "start_date": "emp_start"})
    hist = hist.assign(source="Historical")
    spans = _span_frame()
    mes = month_ends(CUTOVER, DATA_THROUGH)
    parts = []
    for me in mes:
        m = spans[(spans["span_start"] <= me) & (spans["span_end"].isna() | (spans["span_end"] >= me))].copy()
        m["month_end"] = me
        parts.append(m)
    cur = pd.concat(parts, ignore_index=True)
    cur = cur.sort_values(["staff_id", "month_end", "source", "span_start"], ascending=[True, True, True, False])
    cur = cur.drop_duplicates(["staff_id", "month_end"], keep="first")
    cols = ["staff_id", "month_end", "source", "country", "nationality", "grade", "contract_type", "gender",
            "date_of_birth", "unit", "emp_start", "label"]
    fact = pd.concat([hist[cols], cur[cur["month_end"] > CUTOVER][cols]], ignore_index=True)
    fact = derive(fact, "label")
    fact["age"] = (fact["month_end"] - fact["date_of_birth"]).dt.days / 365.25
    fact["is_expatriate"] = ((fact["staff_type"] == "International") & (fact["country"] != ref()["hq"]) &
                             fact["nationality"].notna() & (fact["nationality"] != fact["country"]))
    # overlap reconciliation sources
    recon = pd.concat([
        hist[hist["month_end"] == CUTOVER].assign(src="Historical"),
        h[h["month_end"] == pd.Timestamp(2025, 1, 31)].assign(src="Historical"),
        cur[cur["month_end"].isin([CUTOVER, pd.Timestamp(2025, 1, 31)])].assign(src="Current")], ignore_index=True)
    fact.attrs["recon"] = recon.groupby(["month_end", "src"])["staff_id"].nunique().reset_index()
    return fact


@lru_cache(maxsize=1)
def exits():
    r = ref()
    lv = pd.read_excel(DATA / "historical" / "Leavers_Log_2022_2024.xlsx", dtype=object)
    h = pd.DataFrame({
        "staff_id": lv["Staff No"], "exit_date": dates(lv["Leaving Date"]),
        "exit_reason": lv["Reason"].map(r["exit_labels"]),
        "voluntary": lv["Voluntary"].map({"Yes": "Y", "No": "N"}),
        "country": lv["Location"].map(clean_country), "grade": lv["Grade"], "unit": lv["Unit"],
        "nationality": lv["Nationality"].map(clean_country), "gender": lv["Sex"].map(r["gender"]),
        "contract_type": lv["Contract"].map(r["contract"]), "source": "Historical"})
    cs = core_staff()
    c = cs[cs["end_date"].notna()]
    c = pd.DataFrame({"staff_id": c["staff_id"], "exit_date": c["end_date"], "exit_reason": c["exit_reason"],
                      "voluntary": c["voluntary_exit"], "country": c["country"], "grade": c["grade"],
                      "unit": c["unit"], "nationality": c["nationality"], "gender": c["gender"],
                      "contract_type": c["contract_type"], "source": "CORE"})
    t = trackers()
    t = t[t["end_date"].notna() & ~t["staff_id"].isin(set(cs["staff_id"]))]
    t = pd.DataFrame({"staff_id": t["staff_id"], "exit_date": t["end_date"], "exit_reason": t["exit_reason"],
                      "voluntary": t["voluntary_exit"], "country": t["country"], "grade": t["grade"],
                      "unit": t["unit"], "nationality": t["nationality"], "gender": t["gender"],
                      "contract_type": t["contract_type"], "source": "Tracker"})
    e = pd.concat([h, c[c["exit_date"] > CUTOVER], t[t["exit_date"] > CUTOVER]], ignore_index=True)
    return derive(e)


@lru_cache(maxsize=1)
def appraisals():
    _, _, a = core_raw()
    a = a.copy()
    a["appraisal_date"] = dates(a["appraisal_date"])
    return a


@lru_cache(maxsize=1)
def contracts():
    c = core_contracts()
    cs = core_staff().set_index("staff_id")
    out = c.assign(emp_start=c["staff_id"].map(cs["start_date"]))
    out["is_new_joiner_contract"] = out["start_date"] == out["emp_start"]
    return derive(out.assign(nationality=None))


# ---- recruitment ---------------------------------------------------------------------------------------------
@lru_cache(maxsize=1)
def vacancies():
    r = ref()
    vl = pd.read_excel(DATA / "historical" / "Vacancy_Log_2022_2024.xlsx", dtype=object)
    h = pd.DataFrame({
        "vacancy_id": vl["Vacancy Ref"], "country": vl["Country"].map(clean_country), "grade": vl["Grade"],
        "opening_reason": vl["Reason"].map(lambda x: r["vlabels"].get(("Reason", x))),
        "opened": dates(vl["Date Opened"]), "planned_start": dates(vl["Planned Start"]),
        "planned_months": pd.to_numeric(vl["Planned Months"]), "closed": dates(vl["Date Closed"]),
        "outcome": vl["Outcome"].map(lambda x: r["vlabels"].get(("Outcome", x))),
        "candidate_type": vl["Candidate"].map(lambda x: r["vlabels"].get(("Candidate", x))),
        "time_to_done_hours": np.nan, "date_issue": False, "reopened": False, "source": "Historical"})
    j = pd.read_csv(DATA / "jira" / "jira_recruitment_export.csv", dtype=str)
    j = j[j["issue_type"] == "Vacancy"].copy()
    created, resolved = dates(j["created"]), dates(j["resolved"])
    closed_status = j["status"].isin(["Done", "Cancelled"])
    closed = resolved.where(closed_status)
    issue = closed_status & resolved.notna() & (resolved < created)
    closed = closed.where(~issue, created)
    legacy = j["legacy_vacancy_ref"]
    hist_open = h.set_index("vacancy_id")["opened"]
    opened = created.where(legacy.isna(), legacy.map(hist_open))
    jv = pd.DataFrame({
        "vacancy_id": j["issue_key"], "country": j["country"].map(clean_country), "grade": j["grade"],
        "opening_reason": j["opening_reason"], "opened": opened, "planned_start": dates(j["planned_start_date"]),
        "planned_months": pd.to_numeric(j["planned_duration_months"]), "closed": closed,
        "outcome": j["closure_outcome"].where(closed.notna()), "candidate_type": j["candidate_type"].where(closed.notna()),
        "time_to_done_hours": pd.to_numeric(j["time_to_done_hours"]), "date_issue": issue,
        "reopened": pd.to_numeric(j["reopened_count"]) > 0,
        "source": np.where(legacy.notna(), "JIRA (migrated)", "JIRA")})
    h = h[~h["vacancy_id"].isin(set(legacy.dropna()))]
    v = pd.concat([h, jv], ignore_index=True)
    v["days_to_close"] = np.where(v["closed"].notna() & (v["outcome"] != "Cancelled Position") & ~v["date_issue"],
                                  (v["closed"] - v["opened"]).dt.days, np.nan)
    v["time_to_done_days"] = np.where(v["days_to_close"].notna(), v["time_to_done_hours"] / 24, np.nan)
    return derive(v.assign(unit=None, nationality=None))


@lru_cache(maxsize=1)
def vacancy_monthly():
    v = vacancies()
    parts = []
    for me in month_ends(FIRST_ME, DATA_THROUGH):
        m = v[(v["opened"] <= me) & (v["closed"].isna() | (v["closed"] > me))].copy()
        m["month_end"] = me
        m["is_due"] = m["planned_start"] < me
        parts.append(m)
    return pd.concat(parts, ignore_index=True)


@lru_cache(maxsize=1)
def surges():
    r = ref()
    sl = pd.read_excel(DATA / "historical" / "Surge_Log_2022_2024.xlsx", dtype=object)
    h = pd.DataFrame({"surge_id": sl["Request No"], "request_date": dates(sl["Date Requested"]),
                      "country": sl["Country"].map(clean_country), "grade": sl["Grade"],
                      "status": sl["Status"], "filled_by": sl["Filled By"].map(lambda x: r["vlabels"].get(("FilledBy", x))),
                      "planned_months": pd.to_numeric(sl["Duration (months)"]), "source": "Historical"})
    j = pd.read_csv(DATA / "jira" / "jira_recruitment_export.csv", dtype=str)
    j = j[j["issue_type"] == "Surge"]
    jv = pd.DataFrame({"surge_id": j["issue_key"], "request_date": dates(j["created"]),
                       "country": j["country"].map(clean_country), "grade": j["grade"],
                       "status": j["status"].map({"Done": "Filled", "Cancelled": "Cancelled"}).fillna("Open"),
                       "filled_by": j["filled_by_staff_type"],
                       "planned_months": pd.to_numeric(j["planned_duration_months"]), "source": "JIRA"})
    s = pd.concat([h, jv], ignore_index=True)
    return derive(s.assign(unit=None, nationality=None))


@lru_cache(maxsize=1)
def expatriation():
    cs = core_staff()
    r = ref()
    cs = derive(cs.assign(grade=cs["grade"]), "staff_category")
    cur = cs[(cs["staff_type"] == "International") & (cs["country"] != r["hq"]) & cs["nationality"].notna() &
             (cs["nationality"] != cs["country"])]
    cur = pd.DataFrame({"staff_id": cur["staff_id"], "country": cur["country"], "nationality": cur["nationality"],
                        "start": cur["start_date"], "end": cur["end_date"], "source": "CORE"})
    el = pd.read_excel(DATA / "historical" / "Expatriation_Log_2022_2024.xlsx", dtype=object)
    h = pd.DataFrame({"staff_id": el["Staff No"], "country": el["Posted To"].map(clean_country),
                      "nationality": el["Nationality"].map(clean_country), "start": dates(el["From"]),
                      "end": dates(el["To"]), "source": "Historical"})
    h = h[~h["staff_id"].isin(set(cur["staff_id"]))]
    return pd.concat([h, cur], ignore_index=True)
