# Basin Nexus NG

**Nigeria's Open Catchment Knowledge Atlas** — public source-attributed engagement metadata and geospatial atlas **v1.12**. Stage 3B private evidence intake and QA tooling is in development; no individual stakeholder record or facility location is approved for public release.

## Status

The public atlas includes 20 simplified catchment polygons and areas, provisional 2022 GRID3 state/LGA overlays, 2026 FAO AQUASTAT modeled river-reach networks by catchment, and Natural Earth political/major-water reference layers. It does **not** publish confidential stakeholder submissions, signed materials, personal information, unverified facility coordinates or privately held documents. The source and scientific limitations for each published dataset are documented, and the release remains an exploratory—not statutory or surveyed—geographic atlas.

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

## Stage 2E-A — major rivers and waterbodies (v1.0)

The public atlas includes Natural Earth 1:50m water geography (public domain; source pinned to `ca96624a56bd078437bca8184e78163e5039ad19`). Automated EPSG:6933 selection against a 20km buffered union of the 20 catchments retained five river features and two lake/reservoir features. One degenerate *global-source* river feature was logged and excluded. Full original catchment polygons are unchanged.

The hydro layers show **only overview-scale major rivers and large waterbodies**. They are not a comprehensive stream network, nor a verified dam/irrigation infrastructure inventory. The selected-catchment profile data remain provisional and unaffected. Users can toggle rivers and lakes independently, inspect water feature names and see source warnings. Dams and stakeholder asset observations stay out of public mapped asset layers until their locations are verified.

## Stage 2E-B — Natural Earth 1:10m upgraded water geography (v1.1)

Preflight against the 20-buffered-catchment domain found 17 1:10m river features (vs. five at 1:50m) and two major lake/reservoir features. The 1:10m revision adds overview coverage of Gongola, Hadejia, Kaduna, Sokoto and other named rivers. Natural Earth remains map-scale reference data; it cannot represent small rivers, detailed drainage, asset conditions or surveyed dam positions. Original 1:50m release is recoverable from repository history. Source quality, pin and SHA-256 metadata are preserved in `site/data/hydro_reference_metadata.json`.

## Automated builder → Pages handoff

The Pages workflow also runs after successful hydrology or administrative map-layer build workflows. This is essential because data commits made by the workflow's GitHub token do not themselves start normal push-triggered workflows. Failed source-generation runs do not pass the handoff. The Pages job still applies its public-asset allowlist, geometry, JavaScript and publication-safety checks before uploading the site.

## Stage 2E-C — catchment river focus (v1.2)

The river drawing defaults to a **selected-catchment-only** mode, with Canvas clipping of the existing 1:10m Natural Earth major river linework to the selected hydrological polygon. A control can switch back to regional context, preserving the main river continuities for orientation. The geometry source and catchment boundaries are unchanged. River hit-testing respects the selected catchment; switching the mode does not destroy touch/pan/zoom or LGA interactions. This is an *overview-only* display and does not imply a complete per-catchment stream network. A catchment with no visible Natural Earth line still contains unmapped streams and tributaries.

A detailed network from a scientific hydrography source (e.g., HydroRIVERS, subject to its terms) must be processed with topology, river order, catchment clipping and QA before being introduced as the complete river system.

## Stage 2E-D — Actual selected-catchment river networks (v1.3)

FAO AQUASTAT 2026 WFS returned 80,478 bounded source candidates; 51,906 unique modeled reaches intersect the study's 20 catchments. After clipping, 52,012 reach geometries were assigned to the 20 distinct catchment files. The 20 files carry source IDs, NEXT_DOWN and drainage areas and are published only after strict source count, checksum, ownership and licence QA. The source dataset is described by FAO as CC BY 4.0 and modeled at 15 arcseconds, based on HydroRIVERS. These are not named/surveyed streams. This dataset is distinct from the Natural Earth regional overview.

The map loads **only the selected catchment's** river file, groups segments into Canvas Path2D collections by reported upstream drainage area (>=1000, 100–999, <100 km²), and caches at most two catchments. This is a cartographic hierarchy, not Strahler order. The regional option still uses Natural Earth. All map gestures, administrative overlays and stakeholder publication boundaries are preserved. Errors display an explicit message rather than a false empty catchment.

## UX-A — clearer map navigation and layout (v1.4)

The public interface now gives the map more desktop width and uses a compact Layers disclosure for administrative boundaries, lake/rivers and labels. Immediate water controls retain the per-catchment/regional selector and river-detail select; 'Main + tributaries' is the **initial visual preference only**, with all 52,012 source-derived clipped river reaches unchanged and 'All mapped reaches' available. The map legend is collapsible and starts folded on narrow phone layouts. A Focus catchment action and named active catchment summary improve navigation; the tablet breakpoint places the map at full width and keeps touch input intact. UX review is tracked in `docs/UX_AUDIT_2026-10-21.md`. No geographic asset data are modified.

## UX-B — regional-first launch (v1.5)

Opening the atlas now shows all 20 catchments without selecting any one catchment. The default water context is Natural Earth regional major rivers; no detailed 2026 FAO catchment river file is downloaded until selection. The right panel introduces the whole study and makes clear how to explore. Selecting a polygon or directory row focuses that catchment, switches automatically to its modeled FAO river network and displays its detailed profile. The **All catchments** button restores the exact regional viewport, clears selection and any pop-ups, and cancels in-progress fetches. Catchment-only LGAs, river scope and detail controls are disabled until relevant. The legend begins collapsed. Source provenance, administrative intersections and existing geographic datasets are unchanged.

The release browser suite now verifies the absence of any preselected catchment, lack of eager detailed-river loading, presence of an introductory profile, transition to selected catchment detail, and the All catchments return path at both desktop and tablet viewports. The phone screenshot documents the regional-first layout before any interaction.

## UX-C1 — directory synchronisation and unobtrusive map guidance (v1.6)

On map or directory selection, the currently selected catchment is scrolled into view in the directory when not already visible. The user can still search and scroll manually. Returning to overview resets directory and profile scroll positions. The large persistent instruction box is replaced with a collapsible Map guide. In-panel navigation links to modeled rivers, national boundary context, provisional states/LGAs, and evidence publication status. Changes are interface-only; no scientific or geometry outputs are edited. Release browser QA covers desktop/tablet selections, profile navigation, river loading, touch gestures, and phone layout.

## Stage 3A — SCMP stakeholder source-coverage index (v1.7)

Twenty institutional engagement communiqués have been located and read, one for each catchment. Each contains the source headings Natural Resources, Threats and Challenges, Socioeconomics, and Policies. This release publishes **only that thematic source-availability metadata**, with no raw documents, stakeholder claims, private Drive URLs, signatures, names, or unverified facility coordinates. Intervention records remain pending manual extraction where dispersed under other headings. The public Knowledge index supports topic/catchment searching and links back to the relevant map; scientific source and asset verification remain distinct activities.

## Stage 3C-B — editorial QA and Knowledge discovery (v1.8.1)

The public Knowledge index now supports a host-city filter (Kano, Sokoto, Ilorin, Lokoja, Gombe), combined with existing year, source-theme and catchment search filters, plus an accessible Reset filters control. These are **meeting host cities**, not facility locations or catchment geocentres. All 20 source events remain metadata-only.

The private editorial pilot receives `tools/stage3c_private_editorial_qa.py`, a conservative, aggregate-only QA utility and adversarial synthetic tests. Private inputs/outputs must be outside the public repository; no source wording or candidate IDs are emitted to terminal reports. The tool never grants or implies public release permission. See `docs/STAGE3C_EDITORIAL_QA.md`.

## Stage 3D-A — State/FCT geographic discovery (v1.9)

The public Knowledge index now filters the 20 catchment/source-event profiles using **provisional state/FCT catchment polygon intersection**. State options come from the previously published 2022 GRID3/geoBoundaries crosswalk, with rounded overlap areas. This is **not** workshop participation, source geography or facility positioning. All original source restrictions remain. Private synthetic-only source-context QA validates pilot/source pairing and refuses public-repository inputs. See docs/STAGE3D_A_DISCOVERY_AND_CONTEXT_QA.md.

## Stage 3D-B — public geographic and modeled-water reference explorer (v1.10)

The source-metadata Knowledge page now supports a state-constrained, crosswalk-grounded **LGA filter** (495 distinct provisional LGAs, including overlapping catchments); each card shows mapped catchment area, count of FAO AQUASTAT modeled river reaches and number of intersecting LGAs, with expandable provenance and uncertainty. Sort by catchment name, mapped area or FAO modeled reach count. Export a CSV for the *current filtered public reference summary* (no private source words, IDs, attendance or facility coordinates). Changing state clears an incompatible LGA selection, and Reset clears every filter and sort.

These reference counts are not evidence of water discharge, water-quality monitoring, infrastructure facilities, stakeholder participation or official catchment jurisdictions. The export contains only values already published in the accepted registry, provisional GRID3 crosswalk, FAO 2026 river manifest and public SCMP meeting-event metadata. Public source-coverage index remains explicitly metadata-only; zero individual claims cleared.

The release adds a strict geometry/water/CSV metadata contract validator and extended desktop/tablet phone browser/download regression. See `docs/STAGE3D_B_REFERENCE_EXPLORER.md`.

## Stage 3D-C — thematic reference and evidence-readiness lenses (v1.11)

The Knowledge index now supports four distinct thematic views over the **same filtered public catchment set**: (1) FAO AQUASTAT modeled river reaches grouped by upstream drainage-area thresholds (<100, 100–<1,000 and ≥1,000 km²), with per-catchment counts and a transparent total for the selected set; (2) indicative cross-border geographical footprint and top three state/FCT polygon intersections; (3) documented SCMP engagement workshop provenance by 2024/2025 event year; and (4) infrastructure/intervention **publication readiness**, displaying zero public authorizations rather than inventing facilities. A cross-border filter uses the pre-existing geometry-derived `outsidePct > 0.5` threshold. The filtered CSV now includes upstream-drainage reach-class counts.

These model groupings are **not** measured discharge, river width/length or asset inventories. Group totals are based on *catchment-clipped* reach geometries; cross-catchment overlap is not deduplicated. Source presence is not individual claim verification. The infrastructure view means no individually cleared records have been published, **not** that no facilities exist. No private statements, coordinates, permissions, attendance lists or signed documents were added. See `docs/STAGE3D_C_THEMATIC_LENSES.md`.

## Stages 3D-D + 3D-E — Approved-only evidence catalogue and review receipts (v1.12)

The Knowledge page now contains a **separate public evidence catalogue**, with statement search, seven thematic classes, verification-level filtering, source attribution, related catchment navigation and an explicit absent/unavailable distinction. This feed is versioned in `site/data/public_evidence_catalogue.json` and contains **zero records today**, because no individual restricted stakeholder material is approved for public disclosure. Unlike the public 20-catchment workshop index, actual statements cannot be displayed based only on a communiqué's existence. The atlas does not plot unvalidated facility coordinates, and the catalogue never reads private Drive sources. An inaccessible feed fails closed without disabling geographic exploration.

A future editorial promotion process is implemented in `tools/stage3d_e_release_pipeline.py`: reviewed candidate text and a **separate**, human-authored source-rights/privacy/editorial/spatial decision receipt stay outside this public repository. Every record must match the exact SHA-256 of its public-facing contents, pass the existing public evidence schema validator and have consistent authorization. Review signatures and rights decisions are not authenticated by the code; real institutional permission and a fresh, specifically reviewed release PR remain necessary. Synthetic tests ensure a claim cannot be promoted solely by a "PUBLIC" string, and in v1.12 the production gate enforces the initially empty catalogue. See `docs/STAGE3D_DE_PUBLIC_EVIDENCE_ARCHITECTURE.md`.


## Stages 3D-F/G — owner-only evidence editorial workbenches (private, no public evidence change)

All 88 Stage 3C pilot candidates and 206 Stage 3B high/medium-priority source-line candidates have now been matched to the complete 1,927 principal extracted line register. **Fourteen source-line IDs overlap**, so these are 280 distinct line candidates, not 294 independent claims or assets. Two owner-only Google Docs review packets are stored within the existing restricted Stage 3B folder; **no original text, source IDs, reviewer decisions, raw extracts or restricted document links are in this repository**.

The reusable local tools `stage3d_f_editorial_workbench.py` and `stage3d_g_priority_queue.py` recreate traceable internal packets from owner-controlled exports; both refuse private inputs/outputs inside the public repository, refuse overwriting, fail on mismatched source identity or unexpected publication states, and create **no** release authorizations or map points. GitHub Actions runs synthetic adversarial tests only. The public geographic atlas and v1.12 zero-record evidence catalogue remain unchanged. Original page/table anchoring, eight dam-capacity conflicts, rights/privacy clearance and verified spatial claims remain editorial/scientific tasks. See `docs/STAGE3D_FG_PRIVATE_EDITORIAL_RECONCILIATION.md`.
