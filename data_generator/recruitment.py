"""Vacancies derived from the simulated hires, plus cancelled and still-open positions."""
from datetime import date, timedelta

import numpy as np

import config as C
import workforce as W


def _choice(rng, options, weights):
    w = np.array(weights, dtype=float)
    return options[int(rng.choice(len(options), p=w / w.sum()))]


HARD = {"South Sudan": 1.3, "Afghanistan": 1.25, "Syria": 1.2, "DR Congo": 1.15}


def _anchors(e):
    if e["kind"] == "National":
        return C.NATIONAL_ANCHORS[e["country"]]
    if e["kind"] == "International":
        return C.INTERNATIONAL_ANCHORS[e["country"]]
    return C.HQ_ANCHORS


def build_vacancies(rng, emps):
    out = []
    hires = [e for e in emps if e["start"] >= C.START]
    for e in hires:
        st = "National" if e["grade"].startswith("N") else "International"
        lead = int(rng.integers(5, 41))
        closed = e["start"] - timedelta(days=lead)
        median = {"National": 50, "International": 85}[st] * (0.95 if e["kind"] == "HQ" else 1.0)
        median *= HARD.get(e["country"], 1.0) * (1.3 if e["grade"] in ("N5", "G5", "G6") else 1.0)
        dur = max(7, int(rng.lognormal(np.log(median), 0.55)))
        opened = closed - timedelta(days=dur)
        a = _anchors(e)
        grow = W.target_at(a, e["start"]) - W.target_at(a, W.edate(e["start"], -12))
        p_new = 0.65 if grow > 0.03 * max(W.target_at(a, e["start"]), 1) else 0.12
        reason = "New Position" if rng.random() < p_new else "Replacement"
        cand = _choice(rng, ["External", "Current staff", "Former staff"], [0.68, 0.20, 0.12])
        if cand == "Current staff":
            outcome = "Internal Mobility"
        else:
            outcome = "National Recruitment" if st == "National" else "External Recruitment"
        plan_lead = int(rng.normal(40 if st == "National" else 65, 10))
        out.append(dict(country=e["country"], grade=e["grade"], staff_type=st, opening_reason=reason,
                        opened=opened, planned_start=opened + timedelta(days=max(plan_lead, 20)),
                        planned_months=_choice(rng, [6, 12, 18, 24], [0.2, 0.45, 0.1, 0.25] if st == "National"
                                               else [0.1, 0.4, 0.15, 0.35]),
                        closed=closed, outcome=outcome, candidate_type=cand, filled_by=st,
                        status="Done"))
    # cancelled positions, spread like the real vacancies
    n_cancel = int(0.09 * len(hires))
    for _ in range(n_cancel):
        t = hires[int(rng.integers(0, len(hires)))]
        st = "National" if t["grade"].startswith("N") else "International"
        opened = date(2021, 11, 1) + timedelta(days=int(rng.integers(0, (C.EXPORT_DATE - date(2021, 11, 1)).days)))
        out.append(dict(country=t["country"], grade=t["grade"], staff_type=st,
                        opening_reason="New Position" if rng.random() < 0.4 else "Replacement",
                        opened=opened, planned_start=opened + timedelta(days=int(rng.integers(30, 80))),
                        planned_months=_choice(rng, [6, 12, 24], [0.3, 0.5, 0.2]),
                        closed=opened + timedelta(days=int(rng.integers(25, 170))),
                        outcome="Cancelled Position", candidate_type=None, filled_by=None, status="Cancelled"))
    # apply the export cut-off
    keep = []
    for v in out:
        if v["opened"] > C.EXPORT_DATE:
            continue
        if v["closed"] is not None and v["closed"] < C.START:
            continue
        if v["closed"] > C.EXPORT_DATE:
            v.update(closed=None, outcome=None, candidate_type=None, filled_by=None, status="Open")
        keep.append(v)
    keep.sort(key=lambda v: (v["opened"], v["country"], v["grade"]))
    for i, v in enumerate(keep, 1):
        v["seq"] = i
        v["time_to_done_hours"] = round(float(rng.lognormal(np.log(20), 0.8)), 1)
    return keep
