"""Surge (emergency deployment) requests, 2022 to the export date."""
from datetime import date, timedelta

import numpy as np

import config as C
import reference as R
import workforce as W


def _choice(rng, options, weights):
    w = np.array(weights, dtype=float)
    return options[int(rng.choice(len(options), p=w / w.sum()))]


def build_surges(rng):
    rows = []
    for me in W.month_ends(C.START, C.EXPORT_DATE):
        ms = date(me.year, me.month, 1)
        lam = 6.0 + (2.5 if me.year == 2024 else 0.0) + (1.0 if me.month in (3, 4, 9, 10) else 0.0)
        for _ in range(int(rng.poisson(lam))):
            w = dict(R.SURGE_COUNTRY_WEIGHTS)
            if me.year == 2022 and me.month >= 3:
                w["Ukraine"] *= 2.5
            if me.year == 2024:
                w["Haiti"] *= 2.0
            if me.year == 2024 and 7 <= me.month <= 9:
                w["Bangladesh"] *= 2.5
            if me >= date(2025, 3, 1):
                w["Niger"] = 0.0
            country = _choice(rng, list(w), list(w.values()))
            created = ms + timedelta(days=int(rng.integers(0, (me - ms).days + 1)))
            nat_p = 0.30 + 0.05 * (created.year - 2022) + 0.05 * (created.year >= 2025)
            fill_type = "National" if rng.random() < nat_p else "International"
            grade = _choice(rng, ["N3", "N4", "N5"] if fill_type == "National" else ["G3", "G4", "G5"], [0.35, 0.4, 0.25])
            months = _choice(rng, [1, 2, 3, 4, 6], [0.15, 0.25, 0.3, 0.15, 0.15])
            planned = created + timedelta(days=int(rng.integers(7, 31)))
            r = rng.random()
            status = "Cancelled" if r < 0.08 else "Filled"
            filled = created + timedelta(days=max(5, int(rng.lognormal(np.log(24), 0.5))))
            if status == "Cancelled":
                filled = None
            elif filled > C.EXPORT_DATE:
                status, filled = "Open", None
            rows.append(dict(country=country, grade=grade, created=created, planned_start=planned,
                             planned_months=months, filled=filled, filled_by=fill_type if status == "Filled" else None,
                             status=status, target_type=fill_type))
    rows.sort(key=lambda r: (r["created"], r["country"]))
    for i, r in enumerate(rows, 1):
        r["seq"] = i
    return rows
