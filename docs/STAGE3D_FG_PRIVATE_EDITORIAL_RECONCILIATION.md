# Basin Nexus NG — Stages 3D-F and 3D-G: Owner-restricted editorial reconciliation

Release date: 28 October 2026. Public production version remains **v1.12**, with no new individual stakeholder records. This stage ships private-review automation code only and is not an evidence-publication release.

## Actual private reconciliation conducted

- Revisited 20 principal institutional SCMP catchment communiqués across five owner-only extraction registers: 1,927 source-linked text lines.
- Matched all 88 Stage 3C pilot candidates by exact original source-line ID, source ID, wording, topic section, extracted locator and catchment link. Sixteen selected excerpts are plausible list introductions/incomplete clauses; all source rights, privacy and public release decisions remain blocked.
- Created an **owner-only** full editorial review workbench with 88 individual packets and surrounding same-section extracted lines, original attribution fields, task priorities and empty reviewer decision slots. Important: source-line neighbors are not verified complete paragraphs or PDF/table cell anchors; these require checking against original documents.
- Validated the previous Stage 3B risk list of **206** unique flagged source-line IDs against the same principal registers (95 HIGH, 111 MEDIUM; these describe preliminary review-work priority, not factual credibility).
- Created a separate owner-only priority review document with exact selected original excerpts, adjacent same-section extracted lines, category-specific checks, and explicit status/rights/privacy holds.
- Overlap: 14 flagged source IDs also appear in the 88-pilot selection; the two workbenches cover **280 distinct extracted source-line candidates**, not 294 distinct claims and not 280 verified infrastructure facilities.
- All 206 priority items retain no independently validated asset point and no public release authorization. Screening-code totals may overlap: QUANTITY_UNIT_REVIEW 40; SECURITY_OR_SENSITIVITY_REVIEW 49; INTERVENTION_STATUS_CONTEXT 45; REPORTED_ADMIN_GEOGRAPHY_ONLY 42; INFRASTRUCTURE_IDENTITY_STATUS 79; MINERAL_CLAIM_INDEPENDENT_CHECK 6.
- These output documents remain inside the **owner-only Stage 3B private review folder**, not GitHub. Private Drive IDs are intentionally omitted from this public repository documentation.

## Reproducible private automation

`tools/stage3d_f_editorial_workbench.py` reads the restricted 88-pilot export and repeated Stage 3B principal registers. It rejects missing/multiple source IDs, wording/locator/catchment mismatch, unexpected clearance states or coordinates, and produces source-linked private JSON and text reviewer packets **outside** the public repo. No summaries, permissions, status verification or GPS points are invented.

```sh
python tools/stage3d_f_editorial_workbench.py /secure/private_88_pilot.txt \
  --source-register /secure/principal_kano.txt \
  --source-register /secure/principal_sokoto.txt \
  --source-register /secure/principal_kwara.txt \
  --source-register /secure/principal_lokoja.txt \
  --source-register /secure/principal_gombe.txt \
  --out-private-json /secure/new_stage3df_packet.json \
  --out-private-text /secure/new_stage3df_review.txt
```

`tools/stage3d_g_priority_queue.py` accepts the restricted Stage 3B priority queue and the same five source registers; validates all source IDs, catchment links, hold states, nonexistence of coordinates, and six controlled risk-code categories. It generates separate source-context packets and aggregate-only status for owner review.

```sh
python tools/stage3d_g_priority_queue.py /secure/private_source_triage.txt \
  --source-register /secure/principal_kano.txt \
  --source-register /secure/principal_sokoto.txt \
  --source-register /secure/principal_kwara.txt \
  --source-register /secure/principal_lokoja.txt \
  --source-register /secure/principal_gombe.txt \
  --out-private-json /secure/new_stage3dg_packet.json \
  --out-private-text /secure/new_stage3dg_review.txt
```

The tool outputs with original excerpts are themselves restricted. Do not attach them to GitHub issues, commit them to code, or store them in public Actions artifacts. CI only runs synthetic exercises with fictional source text and fake IDs; it cannot access or grant institutional source permission.

## What's outstanding

1. Confirm source page/paragraph/table cell anchors against original documents (text line numbers are not physical page numbers).
2. Resolve substantive claim splitting, duplicates, inconsistent original versions, incomplete fragments and the **eight known dam capacity conflict groups** with original physical workbook sheet/cell identity. Keep conflicting values separate until verified.
3. Independently check mineral units, location statements, security-sensitive details, temporal/project status, and possible false relationships caused by flattened tables.
4. Prepare faithful *human-reviewed* paraphrases; record explicit rights/privacy decisions and reviewer accountability, including independent validation for any coordinate.
5. Only then consider an authentic source-specific public release PR through the existing reviewed public evidence gate. As of this stage, v1.12's public evidence catalogue remains **zero records**.

## QA boundaries

The source line counts refer to extracted spans, not unique facilities or independently verified claims. The research atlas still has 20 hydrological catchments, 52,012 catchment-clipped FAO-modeled river reach geometries, GRID3 provisional state/LGA intersections, and the metadata-only 20-catchment SCMP workshop source index. No public data, maps, geometry, record catalogue or approved rights were changed in Stages 3D-F/G.
