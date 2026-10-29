# Basin Nexus NG — Combined Stages 3D-AY–BB: original modeled river-endpoint geometry QA

**29 October 2026.** This is a four-stage improvement to the existing independently tested Stage AU–AX FAO `HYRIV_ID` / `NEXT_DOWN` source-link audit. It uses **only the existing 20 immutable SHA-256-pinned FAO AQUASTAT 2026 clipped modeled river GeoJSONs**. No new surveys, dam evidence or public stakeholder claims are added.

## Stages completed

**AY — Numerical geometry screening.** The stand-alone Python standard-library tool `tools/build_stage3d_ay_az_fao_endpoint_qa.py` regenerates the previously verified 51,906-original-ID source graph, validates its public source file byte signatures, then extracts each clipped LineString/MultiLineString part's two endpoints in WGS84. For every source ID with an in-index publisher `NEXT_DOWN` ID, it measures the **minimum great-circle distance between endpoints available in ANY of the 20 clipped catchment copies**. This is a distance-screening measure, not a source feature-length estimate, physically directed junction test, GNSS positional error or guarantee of topological validity. It cannot infer the other side of source features not present within these 20 catchments.

**AZ — Cross-catchment and source integrity QA.** Classify each of 52,012 clipped reach copies as `endpoint_le_50m`, `endpoint_50_to_500m`, `endpoint_gt_500m`, `next_id_not_in_index`, or `source_terminal_or_unlinked`. Maintain a separately source-bound compact 51,906-entry (one per unique source reach) endpoint-gap lookup. Reconcile exact count totals and the existing 33 directional catchment-pair source-association classes. Publisher source identity, source hashes, original NEXT_DOWN relationships, CC BY 4.0, and all original river data are retained.

**BA — Accessible public source-geometry audit.** The Data page now includes a 20-catchment geometry-screening table with click-through to original catchment maps, explicit coverage caveats and downloadable source QA JSON. Missing/unlinked next IDs are reported separately rather than misrepresented as true channel ends.

**BB — Bounded trace annotation and release safeguards.** The existing user-triggered, source-ID-only reach inspection remains capped at 40 source IDs and 20-catchment coverage. The separate geometry-gap index is **lazy-loaded only if a user starts a trace**; gap bands for the selected trace are descriptive, while the existing orange map overlay continues to highlight only original clipped reach geometry already loaded for the selected catchment. Browser QA includes a real clicked reach, source graph and endpoint lookup loaded on demand, malformed summary rejection and unchanged map/browser operation. The public release gate fully rebuilds and byte-for-byte validates the source-model endpoint summary and compact index before GitHub Pages deployment.

## Actual pinned-source results

| Original compiled/model geometry classification | Clipped reach records |
|---|---:|
| Next source ID endpoint minimum **≤50 metres** | **51,973** |
| Minimum between **50 and 500 metres** | **0** |
| Minimum **>500 metres** | **3** |
| NEXT_DOWN points **outside the 20-study-catchment index** | **32** |
| Source **terminal/unlinked** | **4** |
| **Total clipped reach copies** | **52,012** |

Exactly **three original modeled source-linked reach copies** have endpoint-gap measurements greater than 500 metres, appearing in **Gulbin-Ka (1)** and **Yedseram (2)**. This is a targeted QA flag, **not** evidence of a physically broken river. The source model is HydroRIVERS-derived (roughly 15-arcsecond scale), and clipping may create/remove endpoints relative to the uncut original river. Extremely close endpoints do **not** independently prove hydraulically connected field channels; source topology, coincident GIS geometry, spatial accuracy and actual field continuity are separate validation questions.

In addition, the previous source-led 33 catchment-pair `NEXT_DOWN` record associations remain **research relations**, not a verified flow route between complete catchments. The algorithm does not generate across-catchment connector lines, trace river length, estimate water transfer, delineate subbasins or claim an established upstream/downstream catchment order.

## No change to protected outputs

- 20 SCMP catchment geometries and 52,012 original clipped FAO modeled reaches preserved.
- Original 189 bonndata compiled dam-reference intersections and optional 186 **unverified** research points preserved; three disputed names remain withheld.
- Confirmed-dam collection remains **0**. Individually released stakeholder statements remain **0**. Stage AM–AP reviewer-only kit remains separate.
- Source licence: FAO AQUASTAT 2026, HydroRIVERS-derived, **CC BY 4.0**. Original pinned source: https://data.fao.org/catalog/dataset/e22667af-3977-4e9f-b58b-67fb91b0fa87.

## Recommended next checkpoint

Focus **only** on the three >500-m source endpoint-gap cases in Gulbin-Ka and Yedseram, inspecting the full uncut publisher reaches and the actual shared network-node topology where available. This is a bounded scientific QA task, not a reason to rerun broad research or claim validated physical river connectivity. If available source geometry is insufficient, mark the gap unresolved and do not invent a bridging route.
