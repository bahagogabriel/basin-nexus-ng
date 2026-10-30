# Stage S21 — Basin Nexus NG public-atlas experience plan
Status: implementation branch, 30 October 2026

## Purpose
Create a visitor-first geographic atlas, without losing source statements, technical records, datasets or original GIS work. This design explicitly **does not** include a mandatory onboarding tour.

## Work packages and acceptance criteria

### S21A — Information architecture
- Four catchment profile tabs: Overview (default), Resources, Sources, Technical.
- Overview shows actionable navigation without long raw statements.
- Keep original seven technical jump links inside Technical, and retain source-specific search under Sources.
- Any deep link from global resource searches opens Resources; clicking a map symbol opens Resources and its provenance.
- Preserve profile tab during asynchronous river loading; reset to Overview when selecting a new catchment.

### S21B — Independent thematic views
- Display an exclusive single resource category: Minerals, Crops, Ecology, Water, Pressures, or explicit All.
- Filter by individual resource name within the category.
- Keep basemap river, lakes, catchment boundaries and LGAs independent of the resource-category filter.
- Never filter the underlying research/source catalogue simply because the map theme changes.

### S21C — Distinguishable map symbols
- Use meaningful resource type codes (e.g. Au gold, Li lithium, Fe iron ore) with a deterministic collision-free legend registry.
- Render one glyph for each unique resource type within a named LGA, avoiding category-wide number badges.
- Spread marker glyphs in screen space with visible dashed guide-lines to their LGA reference. Such offsets are schematic, **never surveyed site positions**.
- Preserve every underlying source record; when no collision-free marker can fit at current zoom, show the number omitted and advise zooming or filtering. Never silently convert omitted records to invented coordinates.
- Document source limitation and allow people to open full record details.

### S21D — Voluntary guide and credit
- Permanent Start here top tab, explanatory first steps and evidence interpretation.
- No first-visit modal, no forced walkthrough and no automatic onboarding.
- Subtle footer credit: Designed by Samuel Bahago Gabriel, linking to bahagogabriel.com.
- About page identifies creator and accurately describes current published material, limitations and project purpose.

### S21E — Validation and deployment
- Preserve existing 20 study-area polygons, 52,012 clipped river geometries, original 3,277 stakeholder statements and 764 source-attributed LGA records (including 15 original published-plan pilot records).
- Keep independently confirmed dam catalogue empty until appropriate verification.
- Run existing publication, geographic source and Chromium interactive browser checks.
- Test category exclusivity, resource-type filter, guide navigation, compact profile and source preservation on desktop/mobile.
- Merge only on successful CI and confirm the Pages production workflow.

## Out of scope for S21
- No independent physical existence approval for dam, mining, agricultural or ecology reference points.
- No fake GPS locations or changes to original catchment geometry.
- Full community-level survey verification and source boundary reconciliation remain separate later tasks.

## Release checkpoints
1. Thematic symbols and profile navigation in PR.
2. Unit/source QA PASS.
3. Desktop/mobile Chromium QA PASS.
4. Merge to main and Pages deployment PASS.
