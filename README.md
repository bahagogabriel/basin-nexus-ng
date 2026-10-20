# Basin Nexus NG

**Nigeria's Open Catchment Knowledge Atlas** — public geographic boundary preview, version 0.5.1.

## Status

The public site contains only the vetted **boundary preview data**: user-supplied 20 catchment polygons (simplified for visual display), names, stable identifiers, historical alias and calculated areas. No stakeholder submissions, signed materials, personal information, privately held source documents, or unverified infrastructure coordinates are published.

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

## Developing the geographic join

`tools/build_admin_crosswalk.py` is included as an integration script for validated Nigeria ADM1 and ADM2 GIS inputs. The Nigeria state/LGA crosswalk is not yet calculated or published. Prefer geoBoundaries `gbOpen` Nigeria GRID3-derived ADM1 and ADM2 under CC BY 4.0, after approval and attribution.
