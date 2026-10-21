# Basin Nexus NG

**Nigeria's Open Catchment Knowledge Atlas** — public geographic boundary preview, version 0.9.

## Status

The public site contains only the vetted **boundary preview data**: user-supplied 20 catchment polygons (simplified for visual display), names, stable identifiers, historical alias, calculated areas, plus a separate Natural Earth national boundary reference. No stakeholder submissions, signed materials, personal information, privately held source documents, or unverified infrastructure coordinates are published.

## GitHub Pages deployment (continuous publishing)

1. The dedicated public repository is now at https://github.com/bahagogabriel/basin-nexus-ng.
2. In the repository **Settings → Pages → Build and deployment → Source**, select **GitHub Actions** once. The included workflow validates the public asset allowlist and deploys **only `site/`** on each push to `main` (plus manual dispatch).
3. Inspect the URL shown in the Pages deployment record. The usual address is `https://bahagogabriel.github.io/basin-nexus-ng/` if no custom domain applies; it is not considered live until verified.
4. Going forward, push approved updates to main; GitHub Actions tests and publishes them. Refresh the same URL after the workflow finishes (Ctrl+Shift+R if cached).

**Deployment note:** Publishing is not verified until the Pages workflow succeeds and the live URL is checked.

## Map interaction fix (v0.5.1)

Polygon clicks and touch taps now select and zoom to the clicked catchment, while map dragging continues to pan. Pointer capture is assigned to the original press target (not the outer SVG), and keyboard-focus styling follows the polygon outline instead of drawing a rectangular box. Verified locally in headless Chromium on desktop and touch layouts; a dependency-free static regression gate also runs before Pages deployment.

## Local preview

Running `site/index.html` directly as `file://` may prevent the browser from reading JSON assets. Serve with:

```sh
cd site
python -m http.server 8080
```

Visit `http://localhost:8080/`.

## Data sources and QA

- Original spatial input: owner-supplied shapefile `20_Catchments` from the SCMP project, validated working GeoPackage (`SCMP_20_Catchments_Validated.gpkg`).
- GeoJSON is a **visualisation derivative** reprojected to WGS 84, simplified in EPSG:6933 at 300 m tolerance with topology preservation; max single-catchment area difference 0.03%.
- Areas stored in registry from the prior EPSG:6933 calculation; source boundary accuracy is not independently established.
- Benue–Mada current name; Okwa–Mada remains an alias, not another catchment.
- State/LGA crosswalk, infrastructure point mapping and stakeholder data publication need separate verification.
- Source working GIS and review data **must not** be committed into the public Pages repo without explicit release checks.

See `site/data/build_report.json` for reproducible geometry metadata. The data may require attribution or institutional release permission before production use; this is a reviewable public-boundary preview.

## Publish policy (project default)

For every subsequent Basin Nexus NG iteration: produce tests, check for confidential source material, commit *approved public assets* to this repository, verify the GitHub Pages build and share the **same live site URL** and commit SHA. Maintain source-sensitive evidence and working geometries outside the public site.

## Nigeria political boundary and study scope (v0.6)

The underlying stakeholder engagement study focuses **mainly on Northern Nigeria**, not all of Nigeria. The 20 **hydrological** catchments are shown unmodified, including sections extending beyond Nigeria's political borders.

The dashed national outline is a **Natural Earth Admin 0 Countries 1:110m** small-scale reference (public domain). It does not define cadastral, treaty, or administrative authority and must not be used as a surveyed/legal border. [Natural Earth source](https://github.com/nvkelso/natural-earth-vector/blob/master/geojson/ne_110m_admin_0_countries.geojson). It is toggleable on the atlas map.

An EPSG:6933 polygon-overlay screening indicates 10 of 20 catchments extend across Nigeria's outline at this scale. This is an indicative **mapping QA screen**, not verified international-area statistics. The check uses generalized country boundaries and web-simplified catchments; state/LGA joins and precise jurisdictional analysis are still pending. The source boundary's geographic accuracy and publication permission will require appropriate project review.

## Stage 2C — Provisional State and LGA Spatial Join (v0.7)

Data now include 102 catchment–state and 754 catchment–LGA geometric intersections, calculated against the 2022 GRID3 Nigeria ADM1 (37) and ADM2 (774) administrative boundaries distributed by geoBoundaries gbOpen (CC BY 4.0). Source dataset SHA-256 checksums and study-catchment hash are embedded in the public crosswalk JSON. Area overlaps were computed in EPSG:6933 from **web-simplified** catchments, not the full-resolution project Geopackage. These provisional observations must **not** be treated as official allocations or precise international boundaries. No original stakeholder-submitted evidence or personal information is published.

The profiles list state shares as percentages of **total** catchment area. International portions remain outside Nigeria and do not get assigned to states. The directory can be searched by catchment, state or LGA. The simplified admin polygons themselves are not yet a switchable map layer; the preliminary spatial relationships and downloadable tables are provided for transparent review.

## Stage 2D — state and LGA map overlays (v0.8)

- Optional state/FCT boundary display: 37 2022 GRID3-derived polygons, source-pinned via geoBoundaries; shown by default.
- Optional LGA boundary display: lazy-loaded 495 distinct intersecting LGA polygons (not all Nigeria), **clipped visually** to the selected catchment; off by default.
- Both are simplified EPSG:6933 geometry derivatives, for display only. They do not change catchment boundaries or the separate analytically calculated catchment–administrative crosswalk.
- State and LGA boundaries are **provisional**, CC BY 4.0 with GRID3 / geoBoundaries credit; they are not legal/current administrative determinations.
- Admin0 country outline remains a separate, coarse-scale Natural Earth 1:110m context layer.
- The JSON QA metadata contains pinned source hashes, feature counts, and maximum area differences resulting from simplification. These display geometries are generated and geometry-tested in the automated administrative-layer workflow.

## Developing the geographic join

`tools/build_admin_crosswalk.py` is included as an integration script for validated Nigeria ADM1 and ADM2 GIS inputs. The Nigeria state/LGA crosswalk is not yet calculated or published. Prefer geoBoundaries `gbOpen` Nigeria GRID3-derived ADM1 and ADM2 under CC BY 4.0, after approval and attribution.

## Stage v0.9: tablet and desktop map interaction

The interactive geographic panel uses one HTML5 Canvas instead of rebuilding 20 catchment, 37 state and intersecting LGA SVG paths for each pointer movement. Polygon paths are cached, with requestAnimationFrame-controlled redraw and device-pixel-ratio capped at 1.5 for efficient touch-screen rendering. Native Pointer Events support mouse/stylus dragging, two-contact touch pinch-to-zoom and two-finger translation; mouse wheel and on-screen buttons remain operational.

When LGAs are enabled, they have high-contrast gold boundaries **inside the selected catchment** and display accessible pop-up details (LGA name, state and approximate within-catchment area) when tapped. At suitable zoom levels, non-overlapping LGA labels are displayed. All counts, boundaries, source attribution, and review status are unchanged. Browser QA covers actual mouse drag, synthetic two-pointer gesture, taps and LGA selection; deploy uses the same GitHub Pages URL.
