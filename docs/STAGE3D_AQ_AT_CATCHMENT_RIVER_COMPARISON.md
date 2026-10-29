# Basin Nexus NG — Combined Stages 3D-AQ to AT: River-network comparison

**29 October 2026.** This combined leap uses **only existing FAO AQUASTAT 2026 modeled river reaches**, rather than adding more unreviewed dams or repeating remote source research.

## What was built

**AQ — Source-pinned comparative geography.** The original river manifest already contains 51,906 unique source reaches intersecting 20 catchment shapes and **52,012 clipped displayed reaches**. A new validated JSON and CSV give each catchment its exact stable ID, registered area, clipped source-reach count, counts in the three **upstream-drainage-area** bands, the share assigned to the >=1,000 km² class and a transparent count of modeled reaches per **1,000 km² of registered catchment area**.

**AR — Interactive Data catalogue comparison.** Added sortable and searchable 20-catchment comparison table, three-band composition strip, accessible labels, and direct links to download the JSON, CSV and original river manifest. No full 20 river-network files are eagerly loaded to render the comparison.

**AS — Map/profile integration.** Clicking a catchment in the comparison selects and focuses its existing map polygon and loads its existing FAO reaches on demand; catchment profiles show a precisely labelled count-based metric with a link back to the full comparison table.

**AT — Scientific and release QA.** JSON/CSV generation and published files are validated against the original FAO manifest, registered source areas, per-catchment source-reach counts and class totals, source license and stable IDs. Browser QA covers actual search, sorting, map navigation, profile link and rejection of deliberately tampered comparative JSON. The GitHub Pages allowlist admits only these two source-safe new files; confirmed dams and stakeholder release policy are untouched.

## Critical metric boundaries

The count of river **reaches** is not the count of named or unique rivers. Clipping can split a single underlying source river between or within multiple catchments. The area-normalized value is a count of **clipped source modeled segments per 1,000 km²**, not measured stream length per km², not hydrological drainage density, and not a formal flood hazard index. The large/medium/small bands use source upstream area >=1,000 / 100–999 / below 100 km² and are **not Strahler stream orders**. The underlying reaches come from an approximately 15 arcsecond HydroRIVERS-derived FAO model and can omit small or seasonal channels.

Some of the 20 catchments have transboundary footprints. The source area used for normalization is the full existing registered study catchment area, *not* its Nigerian-only share. No independently measured flow, observed flood risk, surveyed stream, dam, hydroengineering facility or privately sourced stakeholder claim is inferred.

Source: FAO AQUASTAT detailed river network (2026-06-15), CC BY 4.0, https://data.fao.org/catalog/dataset/e22667af-3977-4e9f-b58b-67fb91b0fa87. Existing original manifest `site/data/detailed_river_manifest.json` remains the authoritative source of source-reach counts and file hashes.

No original detailed-reach GeoJSON, admin boundaries, catchment geometries or previous evidence workbenches are modified. The public confirmed-dam ledger remains **0**. Independently confirmed dam mapping requires separate field/engineering evidence and rights-aware human review; the portable private review kit from Stage AM–AP remains available.

## Next actions after release

Continue improving substantive catchment geography and usability while waiting for genuinely independent dam-wall field/as-built records. Any new cross-catchment connectivity, stream order or hydrologic-routing claims must first be reconciled against original source topology, across catchment cuts and with separate technical validation; do not infer these from the count dashboard.
