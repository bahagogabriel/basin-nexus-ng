# Basin Nexus NG — Stages 3D-BC–BF: three large clipped river endpoint gaps reconciled to original FAO 2026 modeled source

**29 October 2026.** Four naturally compatible phases close the narrow **model-geometry discrepancy** left by Stage 3D-AY–BB. No new hydrological reach universe or field record was added. Public source: FAO AQUASTAT Rivers, global edition 2026 (published 2026-06-15), original WFS `aquamaps:river_network`, HydroRIVERS-derived modeled network, **CC BY 4.0**.

## Audited results — all three of three original model endpoints coincide

| Study catchment | Original upstream HYRIV_ID | Original NEXT_DOWN | Prior clipped distance | Original uncut WFS distance | Nearest displayed upstream clipped endpoint to original shared model junction | Nearest displayed downstream clipped endpoint |
|---|---:|---:|---:|---:|---:|---:|
| Yedseram (SCMP-C19) | 10505946 | 10506074 | 10,983.5 m | **0.0 m** | 5,581.5 m | 5,763.6 m |
| Gulbin-Ka (SCMP-C04) | 10566530 | 10567236 | 4,805.2 m | **0.0 m** | 2,882.7 m | 3,911.4 m |
| Yedseram (SCMP-C19) | 10568272 | 10568127 | 4,885.1 m | **0.0 m** | 2,499.8 m | 3,391.0 m |

The original publisher WFS returned precisely six requested, uncut features. Every upstream record agrees on its original `NEXT_DOWN` relation. Exact model endpoints coincide at WGS84 [13.4062, 13.5396], [3.5937, 11.7104], and [15.2979, 11.6396] respectively (longitude, latitude). The simplified study-area clipped fragments exclude those shared source endpoints, producing the apparent distance gaps. **The discrepancy is a display-clipping artifact within this modeled network, not evidence that a physical river is disconnected.** It does not authenticate the source model in the field.

## Four complementary stages

**3D-BC — Six narrowly bounded original publisher calls.** The source script `tools/build_stage3d_bc_original_uncut_fao_review.py` makes exactly one WFS CQL query per named source ID, max 3 features/query, rejects non-GeoJSON/excessively large/mismatched/ambiguous results, and records source SHA256 for each original WFS response and all original public modeled features. No bulk re-download of 80,478 bbox model reaches, external-source substitution, upstream speculation or manual source copying.

**3D-BD — Source-vs-clip reconciliation.** `tools/build_stage3d_bd_bf_uncut_source_resolution.py` re-reads the immutable 20-catchment source-linked and endpoint-gap manifests, checks pinned clipped river GeoJSON SHA256, and measures the missing original source junction in both clipped map segments. It fails closed if the original publisher `NEXT_DOWN` ID changes, source IDs are missing, original model endpoints are no longer coincident or previous clipped gaps drift.

**3D-BE — Public, transparent three-case follow-up.** A concise Data & downloads section shows the three original publisher pairs, their >500m previously displayed clipping distances and their **0m original model endpoint match**, with source attribution and clear disclaimers. It offers map navigation to Yedseram/Gulbin-Ka, and downloadable model-only case summary. The model source snapshot of exactly six WFS features is retained under `research/source_qa/` for scientific reproducibility, not published as a new field-verified river layer.

**3D-BF — Deployment, offline and browser QA.** Source and browser synthetic tests, original six-WFS-record tests, the strict public-only file allowlist, a complete original-source-to-public-summary rebuild at every Pages deployment, intentional tampered-summary rejection, map navigation and source model scientific/nonpromotion flags. The full publisher WFS retrieval is intentionally **separate** from Pages deployment, so the public site remains buildable from the preserved and checksummed six-feature original-source snapshot without network calls to FAO.

## Important scientific boundary

The successful original-model endpoint check does **not** verify hydraulic flow on the ground, a field survey, positional accuracy, water-transfer speed, upstream contributing area, actual channel junction elevation, or a new dam site. It only resolves the three large **clipped feature geometry discrepancies in this public model**. The atlas continues to show clipped source reaches, without drawing new bridging geometry. The 33 cross-catchment NEXT_DOWN record pair types remain *source associations*, not independently validated hydrological routes between whole catchment polygons.

The original 20 catchments and 52,012 derived display reach features remain byte-for-byte unchanged. Dam research references remain 189 original intersections, 186 opt-in unverified markers, three disputed identities withheld, **0 independently confirmed dams**. Public released individual SCMP stakeholder statements remain **0**. No restricted files, person-level stakeholder assertions or private evidence were copied.

## Next scientific work

Do not revisit these three gaps as open river discontinuities unless upstream source records change. The next genuinely new step would be a bounded geometry/topology direction audit for the **89 clipped-to-other-catchment NEXT_DOWN links**, ideally using original source geometry, source orientation, cross-boundary intersection and unique-ID deduplication; do not claim a verified full-catchment upstream/downstream hierarchy without defensible geometry and independent review.

### Reproduction

```bash
python tools/build_stage3d_bd_bf_uncut_source_resolution.py \
 --check \
 --six-original research/source_qa/FAO_2026_SIX_ORIGINAL_MODELED_REACHES_NOT_SURVEYED.geojson \
 --output site/data/fao_three_original_gap_resolution.json
python tools/validate_public_release.py
```

Publisher catalogue: https://data.fao.org/catalog/dataset/e22667af-3977-4e9f-b58b-67fb91b0fa87.

The public six-original scientific snapshots in the repository constitute a model-source retrieval. Never call them surveyed river infrastructure.
