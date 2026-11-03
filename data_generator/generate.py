"""Regenerate every source file under data/ and the reference KPI table under tests/.

    python data_generator/generate.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
import pandas as pd

import config as C
import quality_issues as Q
import recruitment as RC
import sources as S
import surges as SG
import workforce as W
import writers as WR


def main():
    rng = np.random.default_rng(C.SEED)
    emps = W.finalise(rng, W.simulate(rng))
    contracts = W.build_contracts(rng, emps)
    appraisals = W.build_appraisals(rng, emps)
    vacs = RC.build_vacancies(rng, emps)
    surges = SG.build_surges(rng)

    staff = S.staff_table(emps)
    core_staff, core_contracts, core_appr, dupes = S.core_frames(rng, staff, contracts, appraisals)
    frames = {
        "core_staff": core_staff, "core_contracts": core_contracts, "core_appraisals": core_appr,
        "trackers": S.tracker_frames(staff, appraisals, contracts),
        "hist_snap": S.historical_snapshots(staff, contracts),
        "hist_leavers": S.leavers_log(staff), "hist_expat": S.expat_log(staff),
        "hist_vac": S.vacancy_log(vacs), "hist_surge": S.surge_log(surges),
    }
    jira, orphans_seq = S.jira_frame(rng, vacs, surges, frames["hist_vac"])
    frames["jira"] = jira
    orphan_refs = set(frames["hist_vac"].loc[frames["hist_vac"]["_seq"].isin(orphans_seq), "Vacancy Ref"])

    log = Q.plant(rng, frames, staff, orphan_refs)
    frames["jira"] = S.stamp_jira(rng, frames["jira"])

    WR.write_reference()
    WR.write_core(frames)
    WR.write_jira(frames["jira"])
    WR.write_trackers(frames["trackers"])
    WR.write_historical(frames)

    out = C.ROOT / "tests"
    out.mkdir(exist_ok=True)
    pd.DataFrame(log).to_csv(out / "planted_issues.csv", index=False)

    from expected_kpis import write_expected_kpis
    write_expected_kpis(out / "expected_kpis.csv")
    print(f"staff {len(staff)}, vacancies {len(vacs)}, surges {len(surges)}, issues planted {len(log)}")


if __name__ == "__main__":
    main()
