# Staff categorisation rules

Meridian Field Research (MFR) reports its workforce on two levels:

- **Staff Type**: National or International. Used for contract and grade analysis.
- **Population**: Global, International or National. Used for headcount reporting.

HQ staff are a subset of Global. Where a chart needs HQ on its own (gender split), it uses
**Population Detail**, which has four members: `Global - HQ`, `Global - Field`, `International`, `National`.

All rules are applied in Power Query against `data/reference/staff_category_mapping.xlsx`. Nothing is hard-coded in the
model, so a change to the mapping file changes the report after a refresh.

## Inputs

| Field | Where it comes from |
|---|---|
| Grade | CORE export, country trackers, legacy snapshots |
| Duty country | Same sources, cleaned with `reference/country_list.xlsx` |
| Unit / team | Same sources |
| Source label (`staff_category` in CORE, `Category` in legacy snapshots) | Free text maintained by HR. Not trusted. |

## Rules, in order

| # | Rule | Result |
|---|---|---|
| R1 | Staff Type comes from the grade scale: `N1`-`N5` are National, `G1`-`G6` are International. | `Staff Type` |
| R2 | If the grade is missing, map the source label through the legacy label table (below). | `Staff Type` |
| R3 | If the duty country is flagged `Is HQ` in the country list (Switzerland), the person is HQ staff. | `Global - HQ` |
| R4 | If Staff Type is International and the unit is flagged `Global` in the unit table, the person is Global field staff, whatever the duty station. | `Global - Field` |
| R5 | Any other International staff. | `International` |
| R6 | Any other National staff. | `National` |

R3 to R6 are evaluated top to bottom and the first match wins. A National grade in a Global unit stays National (R6 is
reached only if R4 does not match, and R4 requires Staff Type = International).

## Mapping tables

`Grade_StaffType`

| Grade | Staff Type | Band |
|---|---|---|
| N1, N2 | National | Support |
| N3, N4 | National | Professional |
| N5 | National | Management |
| G1, G2 | International | Support |
| G3, G4 | International | Professional |
| G5, G6 | International | Management |

`Unit_Scope` marks `Global Research Unit` and `Global Support Unit` as Global. All other units are Country or HQ units.

`Legacy_Labels` (used only by R2)

| Legacy label | Staff Type |
|---|---|
| Expat | International |
| HQ-based | International |
| Local | National |
| National | National |
| International | International |

## Label versus grade conflicts

Some records carry a label that disagrees with the grade, for example a record labelled `International` (or `Expat`) with
an `N3` grade. The grade wins (R1). Each conflict is written to `DQ_Issues` under the check `Category label vs grade`,
so HR can correct the source. The counts are in `docs/data-quality.md`.

## Worked examples

| Grade | Label | Country | Unit | Staff Type | Population Detail |
|---|---|---|---|---|---|
| G4 | International | Switzerland | People & Culture | International | Global - HQ |
| G4 | International | Somalia | Global Research Unit | International | Global - Field |
| G3 | International | Somalia | Programmes | International | International |
| N3 | Local | Somalia | Programmes | National | National |
| N3 | International | Kenya | Programmes | National | National (conflict logged) |
| blank | Expat | Iraq | Logistics & Supply | International | International (via R2) |

## Expatriate flag

A record is flagged `Is Expatriate` when Staff Type is International, the duty country is not the HQ country, and the
nationality differs from the duty country. HQ staff are not counted as expatriates.
