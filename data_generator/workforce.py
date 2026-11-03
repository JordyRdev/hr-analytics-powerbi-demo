"""Month-by-month simulation of the MFR workforce: hires, exits, contracts, appraisals."""
import calendar
from datetime import date, timedelta

import numpy as np

import config as C
import reference as R


def eom(d):
    return date(d.year, d.month, calendar.monthrange(d.year, d.month)[1])


def edate(d, n):
    m = d.year * 12 + d.month - 1 + n
    y, mo = divmod(m, 12)
    mo += 1
    return date(y, mo, min(d.day, calendar.monthrange(y, mo)[1]))


def month_ends(first, last):
    out, d = [], eom(first)
    while d <= last:
        out.append(d)
        d = eom(d + timedelta(days=1))
    return out


def _idx(s):
    y, m = s.split("-")
    return int(y) * 12 + int(m)


def target_at(anchors, me):
    """Linear interpolation between (YYYY-MM, headcount) anchors, flat outside."""
    x = me.year * 12 + me.month
    pts = [(_idx(a), v) for a, v in anchors]
    if x <= pts[0][0]:
        return pts[0][1]
    for (x0, v0), (x1, v1) in zip(pts, pts[1:]):
        if x <= x1:
            return v0 + (v1 - v0) * (x - x0) / (x1 - x0)
    return pts[-1][1]


def _choice(rng, options, weights):
    w = np.array(weights, dtype=float)
    return options[int(rng.choice(len(options), p=w / w.sum()))]


def _new_employee(rng, kind, country, start, initial=False):
    e = {"kind": kind, "country": country, "start": start, "end": None, "exit_reason": None, "voluntary": None}
    st = "National" if kind == "National" else "International"
    grades = R.GRADES
    if kind == "HQ":
        e["grade"] = _choice(rng, ["G1", "G2", "G3", "G4", "G5", "G6"], [0.06, 0.1, 0.2, 0.28, 0.24, 0.12])
    else:
        gw = C.GRADE_WEIGHTS[st]
        e["grade"] = _choice(rng, list(gw), list(gw.values()))
    # contract type of the first contract
    if kind == "National":
        e["ctype"] = _choice(rng, ["Fixed-term", "Short-term", "Consultancy"], [0.70, 0.22, 0.08])
    elif kind == "International":
        e["ctype"] = _choice(rng, ["Fixed-term", "Short-term", "Consultancy"], [0.80, 0.08, 0.12])
    else:
        e["ctype"] = _choice(rng, ["Open-ended", "Fixed-term", "Short-term", "Consultancy"], [0.30, 0.55, 0.10, 0.05])
    # unit
    if kind == "HQ":
        e["unit"] = _choice(rng, R.HQ_UNITS, R.HQ_UNIT_WEIGHTS)
    elif kind == "International" and rng.random() < C.GLOBAL_UNIT_SHARE:
        e["unit"] = R.GLOBAL_UNITS[int(rng.integers(0, 2))]
    else:
        e["unit"] = _choice(rng, R.COUNTRY_UNITS, R.COUNTRY_UNIT_WEIGHTS)
    # gender
    f = C.GENDER_FEMALE_SHARE[kind]
    r = rng.random()
    e["gender"] = "Other" if r < 0.006 else ("Female" if r < 0.006 + f else "Male")
    # nationality
    if kind == "National":
        e["nationality"] = country if rng.random() < 0.98 else R.GS[int(rng.integers(0, len(R.GS)))]
    else:
        gs_p = C.GS_SHARE_HQ if kind == "HQ" else C.GS_SHARE_BY_YEAR[min(max(start.year, 2021), 2027)]
        if kind == "International" and initial:
            gs_p = C.GS_SHARE_BY_YEAR[2021]
        if rng.random() < gs_p:
            if kind == "International" and rng.random() < 0.04:
                e["nationality"] = country          # international contract, local passport
            elif rng.random() < 0.4:
                e["nationality"] = R.GS_COMMON[int(rng.integers(0, len(R.GS_COMMON)))]
            else:
                pool = [g for g in R.GS if g != country]
                e["nationality"] = pool[int(rng.integers(0, len(pool)))]
        else:
            w = list(R.GN_WEIGHTS)
            if kind == "HQ":
                w[0] *= 4
            e["nationality"] = _choice(rng, R.GN, w)
    # date of birth
    mean, sd = C.AGE_MEAN_SD[kind]
    ref = date(2021, 12, 31) if initial else start
    age = float(np.clip(rng.normal(mean, sd), 22, 62))
    e["dob"] = ref - timedelta(days=int(age * 365.25))
    return e


def simulate(rng):
    """Return the list of employee dicts (no IDs, no contracts yet)."""
    segs = [("National", c) for c in C.NATIONAL_ANCHORS] + \
           [("International", c) for c in C.INTERNATIONAL_ANCHORS] + [("HQ", C.HQ_COUNTRY)]

    def anchors(kind, country):
        if kind == "National":
            return C.NATIONAL_ANCHORS[country]
        if kind == "International":
            return C.INTERNATIONAL_ANCHORS[country]
        return C.HQ_ANCHORS

    season_mean = sum(C.MONTH_SEASONALITY.values()) / 12
    emps, active = [], {s: [] for s in segs}
    first_me = eom(C.START)
    for s in segs:
        n = int(round(target_at(anchors(*s), first_me)))
        for _ in range(n):
            tenure = int(min(rng.exponential(3.0), 7.5) * 365.25) + 10
            e = _new_employee(rng, s[0], s[1], date(2021, 12, 31) - timedelta(days=tenure), initial=True)
            emps.append(e)
            active[s].append(e)

    for me in month_ends(C.START, C.SIM_END):
        ms = date(me.year, me.month, 1)
        ndays = (me - ms).days + 1
        for s in segs:
            kind, country = s
            lst = active[s]
            base = target_at(anchors(*s), me)
            tgt = max(0, int(round(base + (rng.normal(0, 0.012 * base) if base > 0 else 0))))
            rate = C.ANNUAL_EXIT_RATE[kind] / 12 * C.MONTH_SEASONALITY[me.month] / season_mean
            elig = [e for e in lst if e["start"] + timedelta(days=C.MIN_TENURE_DAYS) <= me]
            k = int(rng.binomial(len(elig), min(rate, 1.0))) if elig else 0
            leavers = list(rng.choice(len(elig), size=k, replace=False)) if k else []
            leaving = [elig[i] for i in leavers]
            forced = max(0, len(lst) - len(leaving) - tgt)
            rest = [e for e in elig if e not in leaving]
            forced_list = []
            if forced and rest:
                idx = rng.choice(len(rest), size=min(forced, len(rest)), replace=False)
                forced_list = [rest[i] for i in idx]
            for e, is_forced in [(x, False) for x in leaving] + [(x, True) for x in forced_list]:
                lo = max(ms, e["start"] + timedelta(days=C.MIN_TENURE_DAYS))
                hi = me - timedelta(days=1)
                span = max((hi - lo).days, 0)
                d = lo + timedelta(days=int(rng.integers(0, span + 1)))
                e["end"] = d
                if is_forced and country == C.CLOSING_COUNTRY and me >= date(2025, 2, 1):
                    e["exit_reason"], e["voluntary"] = "Office closure", "N"
                elif is_forced:
                    e["exit_reason"] = "End of project funding" if rng.random() < 0.7 else "Redundancy"
                    e["voluntary"] = "N"
                else:
                    col = 2 if kind == "National" else 3
                    pick = _choice(rng, R.EXIT_REASONS, [r[col] for r in R.EXIT_REASONS])
                    e["exit_reason"], e["voluntary"] = pick[0], pick[1]
                lst.remove(e)
            need = tgt - len(lst)
            for _ in range(max(0, need)):
                sd = ms + timedelta(days=int(rng.integers(0, ndays)))
                e = _new_employee(rng, kind, country, sd)
                emps.append(e)
                lst.append(e)
    return emps


def finalise(rng, emps):
    """Mask anything after the export date, assign IDs and build contract chains."""
    keep = []
    for e in emps:
        if e["end"] is not None and e["end"] > C.EXPORT_DATE:
            e["end"], e["exit_reason"], e["voluntary"] = None, None, None
        keep.append(e)
    keep.sort(key=lambda e: (e["start"], rng.random()))
    for i, e in enumerate(keep, 1):
        e["staff_id"] = f"EMP-{i:06d}"
    return keep


def _duration(rng, ctype, kind, grade, start):
    if ctype == "Fixed-term":
        if kind == "National":
            return _choice(rng, [6, 12, 24], [0.30, 0.45, 0.25])
        recent = start >= date(2025, 1, 1)
        if grade in ("G3", "G4") and not recent:
            return _choice(rng, [6, 12, 24], [0.30, 0.55, 0.15])
        return _choice(rng, [6, 12, 24], [0.12, 0.55, 0.33]) if recent else _choice(rng, [6, 12, 24], [0.15, 0.55, 0.30])
    if ctype == "Short-term":
        return _choice(rng, [1, 2, 3, 4, 6], [0.1, 0.2, 0.3, 0.2, 0.2])
    return _choice(rng, [2, 3, 4, 6], [0.2, 0.3, 0.3, 0.2])


GRADE_ORDER = {"National": ["N1", "N2", "N3", "N4", "N5"], "International": ["G1", "G2", "G3", "G4", "G5", "G6"]}


def build_contracts(rng, emps):
    rows, n = [], 0
    for e in emps:
        st = "National" if e["grade"].startswith("N") else "International"
        cur, grade, ctype = e["start"], e["grade"], e["ctype"]
        e["_first_grade"] = grade
        first = True
        while True:
            n += 1
            cid = f"CTR-{n:06d}"
            if ctype == "Open-ended":
                rows.append(dict(contract_id=cid, staff_id=e["staff_id"], contract_type=ctype, grade=grade,
                                 duty_country=e["country"], team=e["unit"], start_date=cur, end_date=e["end"],
                                 granted_months=None, is_first=first))
                break
            dur = _duration(rng, ctype, e["kind"], grade, cur)
            end = edate(cur, dur) - timedelta(days=1)
            truncated = e["end"] is not None and end >= e["end"]
            if truncated:
                end = e["end"]
            rows.append(dict(contract_id=cid, staff_id=e["staff_id"], contract_type=ctype, grade=grade,
                             duty_country=e["country"], team=e["unit"], start_date=cur, end_date=end,
                             granted_months=dur, is_first=first))
            first = False
            if truncated or end > C.EXPORT_DATE:
                break
            cur = end + timedelta(days=1)
            if rng.random() < 0.12:
                order = GRADE_ORDER[st]
                i = order.index(grade)
                if i < len(order) - 1:
                    grade = order[i + 1]
            if ctype in ("Short-term", "Consultancy") and rng.random() < 0.25:
                ctype = "Fixed-term"
        e["grade_now"], e["ctype_now"] = grade, ctype
    return rows


def build_appraisals(rng, emps):
    base = {c: float(np.clip(rng.normal(0.80, 0.07), 0.55, 0.95)) for c in R.FIELD_COUNTRIES + [C.HQ_COUNTRY]}
    rows, n = [], 0
    for e in emps:
        if e["start"] > C.EXPORT_DATE:
            continue
        dates = [e["start"] + timedelta(days=int(182 + rng.integers(0, 40)))]
        k = 1
        while edate(e["start"], 12 * k) <= C.EXPORT_DATE:
            dates.append(edate(e["start"], 12 * k) + timedelta(days=int(rng.integers(-20, 60))))
            k += 1
        for d in dates:
            if d < date(2024, 1, 1) or d > C.EXPORT_DATE:
                continue
            if e["end"] is not None and d >= e["end"]:
                continue
            p = base[e["country"]] + 0.03 * (d.year - 2025)
            if rng.random() < p:
                n += 1
                rows.append(dict(appraisal_id=f"APR-{n:06d}", staff_id=e["staff_id"], appraisal_date=d,
                                 cycle=d.year))
    return rows
