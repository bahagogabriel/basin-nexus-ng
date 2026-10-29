# Basin Nexus NG — Stage 3D-V: OpenStreetMap contextual source comparison (research only)

**Date:** 29 October 2026. **Scientific status:** review leads only; **0 independently confirmed dams**, **0 individual stakeholder statements approved for publication**. Maintain the already published **186 opt-in unverified compiled reference points** (68 original source named and 118 original source unnamed), **3 withheld disputed identities**, and original **189-record** source total over the 20 unchanged catchment polygons.

## Why this check is separate from the original source

Stage 3D-U prepared a 19-record source-only priority review packet, based on the original 2026 Kouassi et al. bonndata *West Africa Dams and Reservoirs Dataset* (CC BY 4.0, DOI https://doi.org/10.60507/FK2/YLDK1Y). The original published CSV and Shapefile ZIP were MD5-verified in the preceding source intake, and the public 186-reference digest is pinned. Public documentary context for **Kafin Zaki, Mambilla and Souapiti** does not establish the actual physical identity or surveyed position of their original Nigeria-labelled points. These **remain withheld** from the optional source map.

Stage V adds a second **research-only source**, crowdsourced OpenStreetMap (OSM), to help identify places needing engineering, field and Earth-observation review. Its tags are *not* independent proof of physical construction: contributors may have used the same compiled dataset, mapped a proposal, mislabelled an impoundment, or positioned a feature approximately.

OSM attribution: **© OpenStreetMap contributors**, **Open Database License (ODbL)**, https://www.openstreetmap.org/copyright . Do not collapse OSM ODbL features into the CC BY 4.0 source dataset or publish an OSM-derived database without appropriately handling ODbL terms. **This review-only derived report remains outside the Pages site**.

## Reproducible automated source-check contract

File: \`tools/build_stage3d_v_osm_context_review.py\` with synthetic tests \`tools/test_stage3d_v_osm_context_review.py\`. The tool first validates the **actual** source-only Stage U 19-reference packet, including its source MD5 lineage, pinned 186-record digest, exact 3 withheld case IDs/names, every empty human confirmation field, and \`HOLD_UNVERIFIED\` status.

One bounded Overpass API query (not 19 separate public server requests) fetches up to **3,000 m around each of the 19 compiled points** for OSM objects tagged \`waterway=dam\`, \`water=reservoir\`, or \`landuse=reservoir\`. It uses \`out center\` and caps the input JSON response size and feature count. Returned features retain the exact OSM object type/ID/link, name if present, OSM snapshot timestamp, source label and licence, tag meaning, geodesic distance to the **OSM representative point**, and a name-equality *hint* only; this is never a facility identity match.

**Important geometry constraint:** for OSM ways/relations, \`out center\` reports a representative polygon/feature center; this is **not the dam wall**, a structure coordinate or an estimate of the reference-point's accuracy. A reservoir outline is not an independently confirmed dam. A close \`waterway=dam\` tag is likewise not proof that a built barrier exists, is operational, is the same facility as a bonndata reference, or has independently determined source lineage.

When the public Overpass server times out or rejects the query, the tool produces \`QUERY_UNAVAILABLE\` and \`SEARCH_UNAVAILABLE\` per source reference, with candidate counts **null**, never \`0\`. When a valid timestamped OSM response contains no relevant features within the comparison radius, the recorded status is \`NO_OSM_TAGGED_FEATURE_OBSERVED_NOT_ABSENCE\`: incomplete OSM coverage does *not* prove no dam exists. A valid response does not imply comprehensive OSM coverage.

## Safety/CI and publication boundaries

On a pull request: only synthetic tests run; the workflow does **not** query OSM or fetch the original real dam source. On \`main\` or a deliberately invoked source-intake workflow: pin and revalidate the original published sources, regenerate the exact 189/71/118 and 19-workbench baselines, then execute the single bounded OSM comparison, archiving its **review-only JSON** in GitHub Actions under \`review/\`, never \`site/data/\`. External HTTP failure becomes a recorded **unavailable** check, not an automatic source-clean score. Source data are public; **no restricted workshop/stakeholder files, positions or text** are involved.

Strict public release allows only the unchanged site files; none of these OSM leads is a confirmed dam. The existing confirmed register remains **0** by policy until independently reviewed, source-independent, dated proof of completed physical structure and position method/uncertainty, rights clearance and accountable human approval are documented in a separate release PR. The wording **"Unnamed reference point"** remains distinct from a rigorously confirmed **"Unnamed dam"**.

## Next research checkpoint

Use this bounded comparison to *prioritize* the 19 cases. For sites with candidate OSM context, an independent specialist must investigate source-tag lineage, actual construction status, wall location versus impoundment outline and dated EO/field/engineering evidence. For cases without a tag match or on an unavailable source, retain them in the review queue. No datum from this stage can automatically change official dam counts or published map classification.

OSM tag semantics: https://wiki.openstreetmap.org/wiki/Tag:waterway%3Ddam and https://wiki.openstreetmap.org/wiki/Tag:water%3Dreservoir .
