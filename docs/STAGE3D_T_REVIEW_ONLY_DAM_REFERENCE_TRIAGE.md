# Stage 3D-T — Automated triage of compiled West Africa dam *references* (NOT verified dams)

**Date:** 28 October 2026. **Input:** exact original-source-only candidate artifact from Stage 3D-R/S. **No change to public web layers, confirmed dam register, stakeholder release, or the existing 20 catchment polygons.**

## Purpose and evidence boundary

The 2026 Kouassi et al. *West Africa Dams and Reservoirs Dataset* (University of Bonn bonndata; DOI https://doi.org/10.60507/FK2/YLDK1Y; CC BY 4.0) is compiled research, not field-verified Nigerian infrastructure. Its publisher CSV MD5 is `046b106da1e3a57ec2f1c461fe411b26` and original Shapefile ZIP MD5 is `a87f9b4ef2e96625b737ffac8595c138`; original source PRJ verified EPSG:4326 in the prior Stage 3D-R workflow.

The source-only review artifact holds **189 Nigeria-labelled references intersecting the 20 simplified catchment display polygons: 71 originally named, 118 unnamed**. The opt-in **public** reference layer has **186** after holding out three disputed named identities. The separate independently confirmed dam register still contains **zero records**. The term **"Unnamed reference point"** never denotes a physically confirmed **"Unnamed dam"**.

## What this stage actually checks

`tools/triage_wa_dam_compiled_references.py` validates the exact candidate schema and publisher hash lineage, per-record source-only provenance, stable reference IDs, WGS84 point bounds, missing-name semantics and zero existence/position confirmations. It verifies the 189/71/118 baseline and reconstructs the pinned SHA-256 `2dc9c81925ea2ed6b2cb82f13410868a96ccc93d1897f3eda6040e924c9dd82a` for the previously published 186 display references, excluding only the three explicitly held source identities. Any mismatch stops the workflow.

It then calculates WGS84 ellipsoidal distances among *source reference coordinates*, flags neighboring points within 250 m or 1 km, normalized repeated names, and same-name positions within 5 km. It does **not** merge nearby points, equate matching names with an identical facility, validate coordinate uncertainty, conclude existence or infer engineering capacity or operational status. Nearest-reference distances in the queue are rounded to 10 m only to prioritize checks; **these numbers are not geolocation accuracy estimates**.

## Reproducible initial queue from the original review artifact

| Queue | References | Interpretation |
| --- | ---: | --- |
| P0 — WITHHELD_IDENTITY | 3 | Published source names Souapiti, Mambilla and Kafin Zaki have separate, already documented identity/existence conflicts. They remain absent from the public point layer. |
| P1 — NEARBY_OR_REPEATED_NAME | 16 | Needs site-level reconciliation because of source point proximity or repeated normalized name; includes unnamed neighboring points. No automatic duplicates. |
| P2 — UNNAMED_SOURCE | 108 | No original publisher source name and not otherwise flagged P0/P1; not independently confirmed unnamed dams. |
| P3 — NAMED_SOURCE | 62 | Original source name present, but independent physical existence, identity, point accuracy and status have not been verified. |
| **Total** | **189** | **Zero confirmed facilities.** |

These are *triage groupings*, not authenticity, safety or risk scores. Membership may change if the original published source or algorithm is deliberately revised in a new audited PR. Counts were reproduced on 28 October 2026 from GitHub Actions 40740216075's original 189-point candidate artifact; the CI run introduced in this stage must be independently checked before claiming a new successful fetch.

## Safe automated workflow and tests

- The `wa-dam-source-preflight.yml` pull-request workflow runs the **new synthetic tests** alongside existing synthetic source checks, without downloading or exposing the real compiled source.
- On a merged push to `main` or explicit manual dispatch, the workflow again fetches and verifies the **publisher-pinned originals**, regenerates the original candidate artifact, then generates a separate **review-only triage queue** as an Actions artifact named `west-africa-2026-source-review-triage-NOT-CONFIRMED`.
- The review queue includes public CC BY 4.0 source reference names/point coordinates solely as research identifiers. It is **not** written to `site/data` or copied into public Pages, nor does it contain restricted stakeholder materials. Public site files remain controlled by the existing strict deployment allowlist.
- Synthetic tests reject source-hash drift, false confirmed/position flags, invented operational statuses, unexpected private columns, mismatched missing-name flags, invalid or repeated coordinates. Tested for proximity, distant repeated names, non-merging and withholding.

## The next real evidence checkpoint — Stage 3D-U

A reviewer must examine P0/P1 source identities first and obtain **independent**, dated site-specific evidence for any future confirmed dam admission: physical constructed structure (rather than a project proposal), dependable location method and uncertainty, source independence and provenance, accountable assessor, rights/privacy and explicit public-release authorization. Review P2/P3 in batches as independent evidence becomes available. The public opt-in compiled references remain explicitly unverified in the meantime.

**No source match, nearest-neighbor distance, recognizable dam name, unsigned statement or satellite-image appearance alone qualifies a point for the confirmed-dam layer.** Do not change either zero-record public release gate without the required evidence, reviewer receipt and new PR.
