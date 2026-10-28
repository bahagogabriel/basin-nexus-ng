# Stage 3D-P — Original publisher dam-identity and positional-consistency triage

28 October 2026 · Public scientific-method documentation · Basin Nexus NG.

## Purpose

The earlier MD5/CRS-checked Kouassi et al. (2026) West Africa Dams and Reservoirs Dataset, bonndata V1 (DOI `10.60507/FK2/YLDK1Y`, CC BY 4.0), yields **1,429 regional source records; 231 country-labelled Nigeria, 189 source point intersections over the 20 supplied catchment display polygons**. These are point observations in a compiled research database, not an authoritative inventory of 189 individual, surveyed, currently functioning Nigerian dam facilities.

The peer-reviewed article documents **substantial underrepresentation of small-scale structures** and mixed georeferencing quality. In one independently benchmarked watershed, only 32% of the field-observed dams appeared in the compiled data. This context **cannot** be applied as a direct correction factor to the Nigerian national inventory or to any of our 20 catchments. Sources and reporting dates vary.

Read: https://doi.org/10.5194/essd-18-7227-2026 ; dataset: https://doi.org/10.60507/FK2/YLDK1Y .

## Reproducible source-level audit

`tools/review_wa_dam_identity_2026.py` first verifies the **exact original publisher CSV MD5** `046b106da1e3a57ec2f1c461fe411b26` and the **original dam shapefile ZIP MD5** `a87f9b4ef2e96625b737ffac8595c138`, requiring the ZIP's .prj to resolve to geographic EPSG:4326. It then checks source columns Country, ID, Dam_Name, Main_Sourc, Long_X, Lat_Y (with optional Dam_Year). Only the 231 Nigeria-labelled source rows are included in detailed source QA. All output records are **aggregate diagnostics**; no source ID, name, coordinate, original row or geometry is emitted.

The audit identifies:
- Present vs absent (or generic) dam names.
- Present vs missing original main-source attribution **labels**, which do not themselves establish independent field evidence.
- Optional date-field completeness; a recorded dam year is not proof of commissioning or operational status in 2026.
- Repeated normalized names **without presuming the same structure**.
- Geodesic pair distances at 250 metres and 1 kilometre to *flag potential co-located/duplicated point records*, not automatically deduplicate dams.
- Same-name pairs within 1 kilometre and 5 kilometres, which are prioritization prompts rather than verified identity matches.
- Source-name, provenance and year presence per catchment, strictly aggregated.
- Zero independently field-verified coordinates; zero point features or confidential stakeholder records published.

The methodology uses the **WGS84 ellipsoid** for near-distance calculations and the unchanged simplified SCMP display polygons for catchment membership. Common names may describe multiple distinct dams, and multiple nearby points may belong to different barriers or reservoirs. Conversely, one facility can have name variants or an offset from its upstream impoundment. Neither exact-name nor proximity matching is sufficient on its own for physical identity or site accuracy.

## Planned output and publication separation

The source-only GitHub Action reruns all synthetic tests on pull requests and performs the actual pinned-source audit only on `main`/explicit workflow dispatch, archived **aggregate-only** without individual source records. If all checks pass, a later independent PR may publish a clearly marked *aggregate source-quality summary* alongside the existing 189 counts. A public per-facility map remains a separate decision requiring examination of positional uncertainties, representative independent site sources, licensing/attribution and user experience; never conflate such a compiled reference location with independent field verification.

Existing `site/data/public_evidence_catalogue.json` remains empty and all owner-restricted SCMP workshop claims, locations, personal data and signed materials remain unpublished. A refusal or source mismatch blocks the pipeline rather than inventing values.
