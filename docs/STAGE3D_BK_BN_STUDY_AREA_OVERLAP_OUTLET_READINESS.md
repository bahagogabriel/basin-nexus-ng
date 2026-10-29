# Basin Nexus NG — Combined stages 3D-BK–BN: original study-area overlap and outlet-readiness source screening

**29 October 2026.** Continuation after successful Stages 3D-BG–BJ (PR #38), preserving exact source lineage and existing mapped polygons. Study-area boundary proximity screening is **not outlet mapping** and does not authorize a hydrologic flow hierarchy.

## Four compatible stages

**BK — Original catchment geometry and overlap test.** Re-read the exact SHA-256-pinned original 20 SCMP catchment polygons; project copies into **EPSG:6933 equal-area** for area screening only, retaining unmodified WGS84 source files. Evaluate **190 unordered study-area pairs**; **42** have positive overlap. Sum of study polygon areas **987,456.50 km²**, unique combined footprint **987,420.55 km²**, *double-counted* overlap screen **35.96 km²**. These are area-screen statistics based on the available generalized polygons, not government-certified watershed outlet areas or a mutually exclusive hydrological partition. Some tiny overlap slivers are decisive for apparent topology in a clipped map.

**BL — Source-linked modeled river boundary preflight.** Scan all 20 original FAO AQUASTAT 2026 HydroRIVERS-derived modeled clipped river files, validate them against each published SHA-256, and reconcile each publisher HYRIV_ID / NEXT_DOWN identifier with the original 51,906-unique-ID graph. Inspect exactly **125 clipped source records**: **89** with a modeled next ID found only in other display study area(s), **32** whose next ID is outside the 20-area lookup, and **4** source terminal/unlinked. Screen nearest available clipped segment *endpoint* to original polygon boundary using a 250-metre descriptive band, never implying subbasin outlets. **121 / 125** fall within 250 m of the study boundary; **65 / 125** clipped modeled source fragments intersect a displayed study polygon boundary. This is source-geometry screening, not a surveyed downstream channel crossing.

**BM — Transparent public atlas explorer.** Added a Data & downloads table for each of the 20 catchments, with count of overlapping other study areas, 125 modeled exit lead totals and source-link class breakdown; added a searchable per-source 125-row table with ID/catchment search, source category filter, modeled distance to boundary, map navigation, research-only JSON and CSV downloads, CC BY 4.0 FAO attribution and conspicuous zero-confirmed-outlets text. **No new map point pins, inferred true outlet locations, or fabricated interbasin flow paths.**

**BN — Independent research, browser and release QA.** CI regenerates exactly the original study polygon and FAO geometry-derived results; tests enforce source SHA-256, 89/32/4 category reconciliation, 190 pairs, 42 overlaps, 125 records, 0 field-verified outlets and copy-safe CSV. Chromium regression tests verify actual 20-catchment table, 125-row detailed search and filters, Yedseram's 25 source records (12 links to another catchment, 9 next IDs outside source index, 4 terminal), navigation and corrupted model-source rejection. Strict GitHub Pages publication allowlist includes only the two source-derived new JSON/CSV assets, requires deterministic reconstruction, and preserves existing evidence and dam release checks.

## Scientific caution and next action

The polygons are **study-area reference geometry**, not independently validated hydrologic partition boundaries or physical drainage divides, especially around overlaps, narrow contact edges and original clipped features. An internal missing NEXT_DOWN ID is a source-index coverage limitation; a terminal/unlinked source entry is not a surveyed basin outlet. Model endpoints near a study boundary do not prove physical flow, field GPS accuracy, channel permanence or outlet position. Neither 42 positive-overlap pairs nor 35.96 km² duplicate area alone establishes what the proper nested watershed hierarchy should be.

The next defensible hydrological step requires **original outlet or control-point evidence** or a new approved DEM-based watershed delineation with explicit stream-burning, outlet selection, hydrography alignment and validation; it must be kept separate from model-source previews and documented as preliminary until verified. The present release is deliberately **outlet-readiness screening**.

## Immutable baselines

- Original 20 SCMP catchment reference polygons and original 52,012 clipped FAO modeled reach features unchanged.
- Prior 89 source cross-study links, 92 destination memberships, 33 source-association pair types and three reconciled original FAO clipped endpoint gaps intact.
- Source remains FAO AQUASTAT 2026, HydroRIVERS-derived river network, CC BY 4.0; source catalogue: https://data.fao.org/catalog/dataset/e22667af-3977-4e9f-b58b-67fb91b0fa87
- Dam compilation **189 intersections**, **186 opt-in unverified research markers**, three identity disputes withheld; **0 independently confirmed physical dam sites** and **0 individually approved stakeholder evidence records**. Source-only review records must never be promoted to verified infrastructure.

## Reproduce

```bash
python -m pip install 'shapely==2.1.2' 'pyproj==3.7.2'
python -m unittest discover -s tools -p 'test_stage3d_bk_bn_overlap_outlet_screen.py' -v
python tools/build_stage3d_bk_bl_overlap_outlet_screen.py --check --output site/data
python tools/validate_public_release.py
```

CI artifacts use source-bounded outputs and the public site contains only approved source-derived aggregate/model-screen data.
