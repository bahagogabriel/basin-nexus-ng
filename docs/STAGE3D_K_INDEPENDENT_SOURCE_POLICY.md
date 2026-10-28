# Basin Nexus NG — Stage 3D-K: Source independence, evidence scope and time-validity gate

Date: 28 October 2026. This is a **research-integrity workflow release** with no new individual public evidence. Public atlas remains v1.12.

## Why an independent-source gate is required

Source-line agreement does **not** by itself establish scientific truth. Two repeated detailed inventory worksheets may be copied versions of one record, rather than two observations. A government promotional web page that repeats the same mineral inventory/quantity language may have a common primary source, rather than independently estimating ore grade or reserves.

Similarly:
- A procurement notice supports procurement **intent** at a dated point in time, not completed construction, completed rehabilitation or operational status.
- A project tracker supports its specific as-of-date status, not status at a later date without a current update.
- An independent paper that collects a sample from a named geological site supports the geographic occurrence and stated sampling date at the paper's documented scope; it does not confirm all neighboring localities or present-day extraction.
- A planned impoundment is not necessarily a completed dam. A completed rehabilitation activity is not an independent performance test of a dam, and a discontinued distribution scheme does not establish the disappearance of the underlying reservoir.
- A storage figure requires its exact capacity definition, unit, source design stage and observation date; **gross**, **live**, **design** and **unspecified** storage are not interchangeable.
- Mineral prospectivity, occurrence, measured resource, indicated resource, reserve, production and economic viability are different technical classes. A claimed "MT" quantity or state promotional brochure cannot by itself establish a defensible reserve estimate.

## Reusable public-source-neutral validator

`tools/stage3d_k_provenance_triage.py` accepts tightly constrained, synthetic-identifier evidence comparisons, grouped by *source lineage*. It outputs only source counts, non-identifying flags and a review status. No original source text, URLs, names, coordinates, private identifiers, quantities or authorization is emitted into its public CI logs.

Supported result states are:
- `NO_EXTERNAL_EVIDENCE_LINKED` — no supporting record present.
- `PARTIAL_OR_HISTORICAL_CONTEXT_ONLY` — only limited, general, derivative, dated or uncorroborated records.
- `INDEPENDENT_SPECIFIC_SOURCE_PRESENT_REVIEW_REQUIRED` — a **human-tagged** independent source appears to support the same dimension and can be reviewed, but no factual verification or release rights are assumed.
- `CONFLICT_HOLD` — an identified documentary contradiction requires reconciliation before any promoted statement.

Every result returns `publication_decision: HOLD`, `rights_cleared: 0`, `mapped_positions: 0`. In particular, even an apparent independent report cannot automatically satisfy source redistribution rights, current asset operation, correct capacity definitions or physical point coordinates.

## Validation methods and limitations

The closed schema distinguishes source kind, independence key, same-origin/suspected shared source, specific vs regional/intention support, ISO observation dates and measurement definitions. An operational or construction-status snapshot more than **365 days old** is flagged historical relative to the target review date; this threshold is a conservative **triage rule**, not a scientific fact about how often dams change status. A nominally recent but uninspected record still cannot establish current status.

The validator does not fetch sources, authenticate official domains, check institutional signatures, compare source text, award rights or deduplicate entities. It accepts only synthetic IDs in CI. Owner-controlled real source evidence and citation details remain outside the public repository.

The linked private Stage 3D-K review programme is checking owner-supplied dam/mineral tables against separately dated government or academic sources. Web-derived official documents are cited in the **restricted** audit, but cannot override missing source permissions or establish sites from a state-wide commodity map.

## Acceptance gates

`tools/test_stage3d_k_provenance_triage.py` contains synthetic tests covering repeated source lineage, copy/derivative promotions, mineral reserve/grade category, old procurement vs current operation, capacity-definition incompatibilities, future-dated sources, internal-private-field rejection and automatic publication denial.

GitHub pull-request CI and the independent production Pages workflow both rerun this gate and all existing GIS, privacy and browser tests. `site/data/public_evidence_catalogue.json` remains zero records; no source statement/facility point is released.
