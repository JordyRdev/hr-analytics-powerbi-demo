"""Plant realistic problems into the exported frames and record what was planted.

The log is the ground truth for tests/test_generated_data.py and docs/data-quality.md.
"""
from datetime import date, timedelta

import numpy as np
import pandas as pd

import config as C
import reference as R
import workforce as W
from sources import COUNTRY_LAYOUT

CANON = {c[0] for c in R.COUNTRIES}


def _variant(rng, name):
    opts = R.COUNTRY_VARIANTS.get(name)
    return opts[int(rng.integers(0, len(opts)))] if opts else name


def _vary(rng, series, p=0.06):
    """Replace some canonical country names by a variant spelling; return new series and count."""
    vals = series.copy()
    n = 0
    for i, v in enumerate(vals):
        if isinstance(v, str) and v in R.COUNTRY_VARIANTS and rng.random() < p:
            vals.iloc[i] = _variant(rng, v)
            n += 1
    return vals, n


def plant(rng, f, staff, orphans):
    log = []

    def add(code, source, description, count):
        log.append(dict(issue_code=code, source=source, description=description, count=int(count)))

    ids = list(staff["staff_id"])

    # 1 missing date of birth and nationality (same people in every source)
    miss_dob = set(rng.choice(ids, size=int(C.MISSING_DOB_SHARE * len(ids)), replace=False))
    miss_nat = set(rng.choice(ids, size=int(C.MISSING_NATIONALITY_SHARE * len(ids)), replace=False))
    add("missing_dob", "all", "Staff with no date of birth", len(miss_dob))
    add("missing_nationality", "all", "Staff with no nationality", len(miss_nat))
    cs = f["core_staff"]
    cs.loc[cs["staff_id"].isin(miss_dob), "date_of_birth"] = None
    cs.loc[cs["staff_id"].isin(miss_nat), "nationality"] = None
    for c, t in f["trackers"].items():
        t.loc[t["staff_id"].isin(miss_dob), "date_of_birth"] = None
        t.loc[t["staff_id"].isin(miss_nat), "nationality"] = None
    for me, s in f["hist_snap"].items():
        s.loc[s["Staff No"].isin(miss_dob), "Birth Date"] = None
        s.loc[s["Staff No"].isin(miss_nat), "Nationality"] = None
    f["hist_leavers"].loc[f["hist_leavers"]["Staff No"].isin(miss_nat), "Nationality"] = None
    add("missing_dob_rows", "core_staff_export", "CORE rows with no date of birth", cs["date_of_birth"].isna().sum())
    add("missing_dob_rows", "country_trackers", "Tracker rows with no date of birth",
        sum(t["date_of_birth"].isna().sum() for t in f["trackers"].values()))
    add("missing_dob_rows", "historical_snapshots", "Snapshot rows with no birth date",
        sum(s["Birth Date"].isna().sum() for s in f["hist_snap"].values()))

    # 2 duplicate IDs between trackers and CORE, some with conflicting grade
    tr_ids = set().union(*[set(t["staff_id"]) for t in f["trackers"].values()])
    dup = sorted(set(cs["staff_id"]) & tr_ids)
    add("duplicate_staff_id", "core_staff_export / country_trackers", "Staff IDs present in both CORE and a tracker", len(dup))
    flip = set(dup[:10])
    n = 0
    for c, t in f["trackers"].items():
        m = t["staff_id"].isin(flip)
        for i in t[m].index:
            g = t.at[i, "grade"]
            if g != "N1":
                t.at[i, "grade"] = f"N{int(g[1]) - 1}"
                n += 1
    add("duplicate_conflicting_grade", "core_staff_export / country_trackers",
        "Duplicate IDs where the tracker grade differs from the CORE grade", n)

    # 3 staff category labelled International on a national grade
    nat_dupes = cs[cs["grade"].str.startswith("N")]["staff_id"].tolist()
    bad = set(nat_dupes[: C.MISLABEL_CORE])
    cs.loc[cs["staff_id"].isin(bad), "staff_category"] = "International"
    add("label_vs_grade", "core_staff_export", "National-grade staff labelled International", len(bad))
    first_snap = f["hist_snap"][date(2022, 1, 31)]
    all_nat = sorted(set().union(*[set(s.loc[s["Grade"].str.startswith("N", na=False), "Staff No"]) for s in f["hist_snap"].values()]))
    bad_h = set(rng.choice(all_nat, size=C.MISLABEL_HIST_STAFF, replace=False))
    rows = 0
    for me, s in f["hist_snap"].items():
        m = s["Staff No"].isin(bad_h)
        s.loc[m, "Category"] = "Expat"
        rows += int(m.sum())
    add("label_vs_grade", "historical_snapshots", "National-grade staff labelled Expat (staff)", len(bad_h))
    add("label_vs_grade_rows", "historical_snapshots", "Snapshot rows carrying that label", rows)

    # 4 contract end before start
    cc = f["core_contracts"]
    cand = []
    for sid, g in cc.groupby("staff_id"):
        g = g.sort_values("start_date")
        for j in range(len(g) - 1):
            r = g.iloc[j]
            if pd.notna(r["end_date"]) and pd.notna(r["granted_months"]):
                if r["end_date"] == W.edate(r["start_date"], int(r["granted_months"])) - timedelta(days=1):
                    cand.append(g.index[j])
    pick = rng.choice(cand, size=C.CONTRACT_END_BEFORE_START, replace=False)
    for i in pick:
        cc.at[i, "end_date"] = cc.at[i, "start_date"] - timedelta(days=int(rng.integers(5, 61)))
    add("contract_end_before_start", "core_contracts_export", "Contracts whose end date is before the start date", len(pick))

    # 5 overlap months: legacy file differs from CORE in Dec 2024 and Jan 2025
    left = staff[(staff["end"] >= date(2024, 9, 1)) & (staff["end"] <= date(2024, 11, 30))]
    stale_ids = list(left.sample(n=C.OVERLAP_STALE_ROWS, random_state=int(rng.integers(0, 2**31 - 1)))["staff_id"])
    src = f["hist_snap"][date(2024, 8, 31)]
    stale = src[src["Staff No"].isin(stale_ids)]
    for me in (date(2024, 12, 31), date(2025, 1, 31)):
        s = f["hist_snap"][me]
        drop = rng.random(len(s)) < C.OVERLAP_MISSING_SHARE
        add("overlap_missing_in_legacy", "historical_snapshots", f"Staff present in CORE but missing from the legacy snapshot {me:%b %Y}", int(drop.sum()))
        s = s[~drop]
        extra = stale.copy()
        extra["Snapshot Date"] = me
        f["hist_snap"][me] = pd.concat([s, extra], ignore_index=True)
        add("overlap_stale_in_legacy", "historical_snapshots", f"Leavers still listed in the legacy snapshot {me:%b %Y}", len(extra))

    # 6 JIRA data problems
    j = f["jira"]
    vac_done = j[(j["issue_type"] == "Vacancy") & (j["status"] == "Done") & j["legacy_vacancy_ref"].isna() & j["resolved"].notna()].index
    rb = rng.choice(vac_done, size=C.JIRA_RESOLVED_BEFORE_CREATED, replace=False)
    for i in rb:
        j.at[i, "resolved"] = j.at[i, "created"] - timedelta(days=int(rng.integers(1, 13)))
    add("jira_resolved_before_created", "jira_recruitment_export", "Tickets resolved before they were created", len(rb))
    rest = [i for i in vac_done if i not in set(rb)]
    ro = rng.choice(rest, size=C.JIRA_REOPENED, replace=False)
    for i in ro:
        j.at[i, "reopened_count"] = int(rng.integers(1, 3))
        j.at[i, "resolved"] = min(j.at[i, "resolved"] + timedelta(days=int(rng.integers(3, 21))), C.EXPORT_DATE)
    open_v = j[(j["issue_type"] == "Vacancy") & j["status"].isin(["Open", "In Progress"]) & j["legacy_vacancy_ref"].isna()].index
    ro2 = rng.choice(open_v, size=5, replace=False)
    for i in ro2:
        j.at[i, "status"] = "Reopened"
        j.at[i, "reopened_count"] = 1
    add("jira_reopened", "jira_recruitment_export", "Tickets reopened at least once (incl. 5 currently reopened)", len(ro) + len(ro2))
    add("legacy_vacancy_migrated", "jira_recruitment_export", "Vacancies open at cut-over that were re-created in JIRA with a legacy reference",
        int(j["legacy_vacancy_ref"].notna().sum()))
    add("legacy_vacancy_orphan", "historical vacancy log", "Vacancies open at cut-over never re-created in JIRA (stay open in the model)", len(orphans))

    # 7 country spelling variants
    counts = {}
    for key, col in [("core_staff", "duty_country"), ("core_staff", "nationality"), ("core_contracts", "duty_country"),
                     ("jira", "country"), ("hist_vac", "Country"), ("hist_surge", "Country"),
                     ("hist_expat", "Posted To"), ("hist_expat", "Nationality"),
                     ("hist_leavers", "Location"), ("hist_leavers", "Nationality")]:
        f[key][col], n = _vary(rng, f[key][col])
        counts[(key, col)] = n
    for c, t in f["trackers"].items():
        t["nationality"], n = _vary(rng, t["nationality"])
        counts[("tracker", c)] = counts.get(("tracker", c), 0) + n
    n_snap = 0
    for me, s in f["hist_snap"].items():
        for col in ("Location", "Nationality"):
            s[col], n = _vary(rng, s[col])
            n_snap += n
    add("country_variant", "core_staff_export", "Cells with a non-standard country spelling (duty country, nationality)",
        counts[("core_staff", "duty_country")] + counts[("core_staff", "nationality")])
    add("country_variant", "core_contracts_export", "Cells with a non-standard country spelling", counts[("core_contracts", "duty_country")])
    add("country_variant", "jira_recruitment_export", "Cells with a non-standard country spelling", counts[("jira", "country")])
    add("country_variant", "country_trackers", "Tracker nationality cells with a non-standard spelling (the DRC tracker file name is a variant too)",
        sum(v for k, v in counts.items() if k[0] == "tracker"))
    add("country_variant", "historical_snapshots", "Cells with a non-standard country spelling (location, nationality)", n_snap)
    add("country_variant", "historical logs", "Cells with a non-standard country spelling (vacancy, surge, expatriation, leavers logs)",
        counts[("hist_vac", "Country")] + counts[("hist_surge", "Country")] + counts[("hist_expat", "Posted To")] + counts[("hist_expat", "Nationality")]
        + counts[("hist_leavers", "Location")] + counts[("hist_leavers", "Nationality")])

    # 8 text dates
    add("text_dates", "Staff_Snapshots_2022.xlsx", "Snapshot rows with the birth date stored as text (dd/mm/yyyy)",
        sum(len(s) for me, s in f["hist_snap"].items() if me.year == 2022))
    add("text_dates", "country_trackers", "Trackers (layout B) storing all dates as text (dd/mm/yyyy)",
        sum(len(t) for c, t in f["trackers"].items() if COUNTRY_LAYOUT[c] == "B"))
    return log
