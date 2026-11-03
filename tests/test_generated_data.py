"""Checks on the synthetic source files: structure, ranges, shares and the planted problems."""
import pandas as pd
import pytest

import config as C
import expected_kpis as K
import pandas_model as M

DATA = C.DATA
RD = pd.Timestamp(C.EXPORT_DATE)
PLANTED = pd.read_csv(C.ROOT / "tests" / "planted_issues.csv")


def planted(code, source=None):
    p = PLANTED[PLANTED["issue_code"] == code]
    if source:
        p = p[p["source"] == source]
    return int(p["count"].sum())


# ---- files and keys -----------------------------------------------------------------------------------------
EXPECTED_FILES = [
    "core_hris/core_staff_export.csv", "core_hris/core_contracts_export.csv", "core_hris/core_appraisals_export.csv",
    "jira/jira_recruitment_export.csv", "historical/Staff_Snapshots_2022.xlsx", "historical/Staff_Snapshots_2023.xlsx",
    "historical/Staff_Snapshots_2024.xlsx", "historical/Staff_Snapshots_2025_Jan.xlsx",
    "historical/Vacancy_Log_2022_2024.xlsx", "historical/Surge_Log_2022_2024.xlsx",
    "historical/Expatriation_Log_2022_2024.xlsx", "historical/Leavers_Log_2022_2024.xlsx",
    "reference/staff_category_mapping.xlsx", "reference/gn_gs_nationality.xlsx", "reference/country_list.xlsx",
    "reference/tracker_column_map.xlsx", "reference/vacancy_label_mapping.xlsx",
]


@pytest.mark.parametrize("rel", EXPECTED_FILES)
def test_source_file_exists(rel):
    assert (DATA / rel).stat().st_size > 0


def test_one_tracker_per_field_country():
    names = {p.stem.replace("NS_tracker_", "") for p in (DATA / "country_trackers").glob("*.xlsx")}
    assert len(names) == 8
    assert {M.clean_country(n) for n in names} == set(M.ref()["countries"]["Country"]) - {M.ref()["hq"]}


def test_ids_are_pseudonymised():
    cs = M.core_staff()
    assert cs["staff_id"].str.fullmatch(r"EMP-\d{6}").all()
    assert not any("name" in c.lower() for c in cs.columns)


def test_keys_unique():
    cs, cc = M.core_staff(), M.core_contracts()
    assert cs["staff_id"].is_unique
    assert cc["contract_id"].is_unique
    j = pd.read_csv(DATA / "jira" / "jira_recruitment_export.csv")
    assert j["issue_key"].is_unique
    h = M.historical_snapshots()
    assert not h.duplicated(["staff_id", "month_end"]).any()
    t = M.trackers()
    assert t["staff_id"].is_unique
    f = M.staff_monthly()
    assert not f.duplicated(["staff_id", "month_end"]).any()


def test_date_ranges():
    h = M.historical_snapshots()
    assert h["month_end"].min() == pd.Timestamp(2022, 1, 31)
    assert h["month_end"].max() == pd.Timestamp(2025, 1, 31)
    f = M.staff_monthly()
    assert f["month_end"].min() == pd.Timestamp(2022, 1, 31)
    assert f["month_end"].max() == RD
    assert f["month_end"].nunique() == 58
    j = pd.read_csv(DATA / "jira" / "jira_recruitment_export.csv")
    assert pd.to_datetime(j["created"]).min() >= pd.Timestamp(2025, 1, 1)
    assert pd.to_datetime(j["created"]).max() <= RD + pd.Timedelta(days=1)
    assert M.core_staff()["start_date"].max() <= RD


def test_reference_mapping_is_complete():
    f = M.staff_monthly()
    assert f["staff_type"].notna().all()
    assert set(f["country"].dropna()) <= set(M.ref()["countries"]["Country"])
    assert set(f["nationality"].dropna()) <= set(M.ref()["gngs"])
    assert f["contract_type"].notna().all()
    assert set(M.vacancies()["country"]) <= set(M.ref()["countries"]["Country"])
    assert set(M.surges()["country"]) <= set(M.ref()["countries"]["Country"])


# ---- shape of the organisation ------------------------------------------------------------------------------
def test_category_shares():
    s = M.staff_monthly()
    s = s[s["month_end"] == RD]
    n = len(s)
    assert 950 <= n <= 1050
    hq = (s["population_detail"] == "Global - HQ").sum() / n
    nat = (s["population"] == "National").sum() / n
    intl = (s["staff_type"].eq("International") & (s["population_detail"] != "Global - HQ")).sum() / n
    assert 0.03 <= hq <= 0.07
    assert 0.70 <= nat <= 0.80
    assert 0.15 <= intl <= 0.25
    assert s["country"].nunique() == 8       # 7 field offices still open, plus Switzerland


def test_trend_story():
    f = M.staff_monthly()
    hc = lambda c, d: f[(f["country"] == c) & (f["month_end"] == pd.Timestamp(d))]["staff_id"].nunique()
    assert hc("South Sudan", "2025-01-31") > 1.7 * hc("South Sudan", "2023-12-31")   # scale-up through 2024
    assert hc("Afghanistan", "2025-01-31") > 50
    assert hc("Afghanistan", "2026-10-31") == 0                                      # closed in 2025
    gs = lambda d: (lambda x: (x["gn_gs"] == "GS").sum() / x["gn_gs"].isin(["GS", "GN"]).sum())(
        f[(f["month_end"] == pd.Timestamp(d)) & (f["staff_type"] == "International")])
    assert gs("2026-10-31") > gs("2022-01-31")


def test_vacancy_rate_in_plausible_range():
    vm = M.vacancy_monthly()
    f = M.staff_monthly()
    for d in ("2022-12-31", "2024-06-30", "2026-10-31"):
        d = pd.Timestamp(d)
        rate = vm[vm["month_end"] == d]["vacancy_id"].nunique() / (
            f[f["month_end"] == d]["staff_id"].nunique() + vm[vm["month_end"] == d]["vacancy_id"].nunique())
        assert 0.02 <= rate <= 0.10


# ---- planted problems ---------------------------------------------------------------------------------------
def test_country_variants_present_in_every_source():
    canon = set(M.ref()["countries"]["Country"]) | set(M.ref()["gngs"])
    cs = pd.read_csv(DATA / "core_hris" / "core_staff_export.csv")
    assert (~cs["duty_country"].isin(canon)).sum() + (~cs["nationality"].dropna().isin(canon)).sum() == planted("country_variant", "core_staff_export")
    cc = pd.read_csv(DATA / "core_hris" / "core_contracts_export.csv")
    assert (~cc["duty_country"].isin(canon)).sum() == planted("country_variant", "core_contracts_export")
    j = pd.read_csv(DATA / "jira" / "jira_recruitment_export.csv")
    assert (~j["country"].isin(canon)).sum() == planted("country_variant", "jira_recruitment_export")
    h = pd.read_excel(DATA / "historical" / "Staff_Snapshots_2023.xlsx")
    assert (~h["Location"].isin(canon)).sum() > 0
    assert "NS_tracker_DRC.xlsx" in {p.name for p in (DATA / "country_trackers").glob("*.xlsx")}


def test_duplicate_ids_between_tracker_and_core():
    dup = set(M.core_staff()["staff_id"]) & set(M.trackers()["staff_id"])
    assert len(dup) == planted("duplicate_staff_id") == C.DUPLICATES_TRACKER_CORE


def test_overlap_months_differ():
    r = M.staff_monthly().attrs["recon"].pivot(index="month_end", columns="src", values="staff_id")
    assert (r["Historical"] != r["Current"]).all()
    assert abs(r["Historical"] - r["Current"]).max() < 60      # small differences, not a different population


def test_missing_dob_and_nationality():
    cs = M.core_staff()
    f = M.staff_monthly()
    last = f[f["month_end"] == RD]
    assert 0.005 <= last["date_of_birth"].isna().mean() <= 0.04
    assert 0.001 <= last["nationality"].isna().mean() <= 0.03
    assert cs["date_of_birth"].isna().sum() == planted("missing_dob_rows", "core_staff_export")


def test_jira_ticket_problems():
    j = pd.read_csv(DATA / "jira" / "jira_recruitment_export.csv")
    v = j[j["issue_type"] == "Vacancy"]
    bad = (M.dates(v["resolved"]) < M.dates(v["created"])).sum()
    assert bad == planted("jira_resolved_before_created") == C.JIRA_RESOLVED_BEFORE_CREATED
    assert (pd.to_numeric(v["reopened_count"]) > 0).sum() + (v["status"] == "Reopened").sum() >= C.JIRA_REOPENED
    assert v["legacy_vacancy_ref"].notna().sum() == planted("legacy_vacancy_migrated")


def test_orphan_legacy_vacancies_stay_open():
    vl = pd.read_excel(DATA / "historical" / "Vacancy_Log_2022_2024.xlsx")
    j = pd.read_csv(DATA / "jira" / "jira_recruitment_export.csv")
    open_legacy = set(vl.loc[vl["Date Closed"].isna(), "Vacancy Ref"])
    orphans = open_legacy - set(j["legacy_vacancy_ref"].dropna())
    assert len(orphans) == planted("legacy_vacancy_orphan") == 6


def test_label_conflicts():
    cs = M.core_staff()
    bad = cs[cs["grade"].str.startswith("N") & (cs["staff_category"] == "International")]
    assert len(bad) == planted("label_vs_grade", "core_staff_export") == C.MISLABEL_CORE
    h = M.historical_snapshots()
    conflict = h[h["grade"].str.startswith("N") & (h["label"] == "Expat")]
    assert conflict["staff_id"].nunique() == C.MISLABEL_HIST_STAFF
    f = M.staff_monthly()
    assert set(f.loc[f["staff_id"].isin(set(bad["staff_id"])) & (f["month_end"] == RD), "staff_type"]) == {"National"}


def test_contract_end_before_start():
    assert M.core_contracts()["end_before_start"].sum() == planted("contract_end_before_start") == C.CONTRACT_END_BEFORE_START
    c = M.core_contracts()
    assert (c["end_date"].dropna() >= c.loc[c["end_date"].notna(), "start_date"]).all()      # repaired


def test_tracker_layouts_differ():
    import openpyxl
    heads = set()
    for p in (DATA / "country_trackers").glob("*.xlsx"):
        ws = openpyxl.load_workbook(p, read_only=True).worksheets[0]
        for i, row in enumerate(ws.iter_rows(values_only=True), 1):
            if any(isinstance(c, str) and c.strip().lower() in ("staff id", "id no.", "employee number") for c in row):
                heads.add((i, ws.title))
                break
    assert len(heads) >= 4


# ---- reference values ---------------------------------------------------------------------------------------
def test_expected_kpis_file_is_current():
    saved = pd.read_csv(C.ROOT / "tests" / "expected_kpis.csv")
    fresh = K.build()
    assert list(saved["kpi"]) == list(fresh["kpi"])
    assert list(saved["filter"]) == list(fresh["filter"])
    assert saved["expected_value"].to_numpy() == pytest.approx(fresh["expected_value"].astype(float).to_numpy(), abs=1e-5)


def test_expected_kpis_cover_the_headline_measures():
    saved = pd.read_csv(C.ROOT / "tests" / "expected_kpis.csv")
    assert len(saved) >= 20
    for k in ("Headcount", "Vacancy Rate", "Retention Rate (12m)", "Turnover Rate (12m)", "Avg Days to Close",
              "GS/GN Ratio", "Appraisal Completion", "Contracts Ending Within 4 Months"):
        assert k in set(saved["kpi"])


# ---- size ---------------------------------------------------------------------------------------------------
def test_data_volume():
    rows = len(M.staff_monthly())
    assert 45_000 <= rows <= 75_000, rows
    total = sum(p.stat().st_size for p in DATA.rglob("*") if p.is_file())
    assert total < 10 * 1024 * 1024, total


def test_about_25_nationalities_with_both_flags():
    g = M.ref()["gngs"]
    assert 22 <= len(g) <= 28
    assert set(g.values()) == {"GN", "GS"}
    operating = set(M.ref()["countries"]["Country"]) - {M.ref()["hq"]}
    assert operating <= {k for k, v in g.items() if v == "GS"}


# ---- quality bar at the reporting date ----------------------------------------------------------------------
def _now():
    f = M.staff_monthly()
    return f[f["month_end"] == RD]


def test_bar_international_staff_per_operating_country():
    s = _now()
    countries = M.ref()["countries"]
    active = countries[(countries["Office Status"] == "Active")]["Country"]       # offices still open at the date
    n = s[s["staff_type"] == "International"].groupby("country")["staff_id"].nunique()
    for c in active:
        if c == M.ref()["hq"]:
            continue
        assert n.get(c, 0) >= 10, (c, n.get(c, 0))


def test_bar_global_staff_total():
    assert _now().query("population == 'Global'")["staff_id"].nunique() >= 40


def test_bar_staff_per_grade():
    n = _now().groupby("grade")["staff_id"].nunique()
    assert len(n) == 11
    assert n.min() >= 10, n.to_dict()


def test_bar_international_contracts_ending_in_4_months():
    c = M.contracts()
    c = c[(c["start_date"] <= RD) & (c["end_date"].isna() | (c["end_date"] >= RD))]
    e = c[(c["staff_type"] == "International") & c["end_date"].notna() & (c["end_date"] > RD) &
          (c["end_date"] <= M.eomonth(RD, 4))]
    assert len(e) >= 15, len(e)
    assert e["grade"].nunique() >= 3, e["grade"].value_counts().to_dict()


def test_bar_open_vacancies_every_month_end():
    vm = M.vacancy_monthly()
    n = vm.groupby("month_end")["vacancy_id"].nunique()
    assert len(n) == 58
    assert n.min() >= 8, n.nsmallest(3).to_dict()


def test_bar_vacancies_closed_last_12_months():
    v = M.vacancies()
    c = v[(v["closed"] > M.eomonth(RD, -12)) & (v["closed"] <= RD)]
    assert len(c) >= 30, len(c)


def test_bar_surge_requests_per_year_with_both_fill_types():
    s = M.surges()
    for year, g in s.groupby(s["request_date"].dt.year):
        assert len(g) >= 25, (year, len(g))
        assert {"National", "International"} <= set(g["filled_by"].dropna()), year


def test_bar_exits_last_12_months_both_types():
    e = M.exits()
    e = e[(e["exit_date"] > M.eomonth(RD, -12)) & (e["exit_date"] <= RD)]
    assert len(e) >= 15, len(e)
    assert {"Y", "N"} <= set(e["voluntary"])
