# Basin Nexus NG — Stage 3D-W: dam-reference lineage and historical satellite catalog research

**29 October 2026 · research-only development.** This is an automated evidence-acquisition *planning* step, not an independently verified dam inventory, a physical dam-wall survey, or visual satellite interpretation.

## Inputs and retained baseline

- Original Kouassi et al. (2026) compiled West Africa dam source, University of Bonn bonndata, DOI https://doi.org/10.60507/FK2/YLDK1Y , CC BY 4.0: **189** source records intersecting the 20 SCMP display polygons; 71 source-named, 118 source-unnamed. Original publisher MD5 and pinned **186** public research-preview SHA-256 remain mandatory.
- The optional public compiled-source layer remains **186** unverified points (68 with source names, 118 without); **three disputed named identities** remain withheld. The independently confirmed dam collection and released individual stakeholder evidence are both **zero**.
- The original Stage 3D-U 19-case reviewer workbench remains *HOLD*, with all location/existence/rights/reviewer receipts blank. The Stage 3D-V ODbL research comparison reported five priority references near an OpenStreetMap \`waterway=dam\` way and carries its own date and provenance.

## Exact five Stage V context leads (not dam confirmation)

| Reference | Source-reported name | Nearest OSM *way* (crowdsourced, ODbL) | Source point to way representative center |
| --- | --- | --- | ---: |
| WA26-003 | Gusau | https://www.openstreetmap.org/way/272558892 | 184 metres |
| WA26-083 | Gusau | https://www.openstreetmap.org/way/272558893 | 789 metres |
| WA26-184 | NULL / Unnamed reference point | https://www.openstreetmap.org/way/571289117 | 17 metres |
| WA26-185 | NULL / Unnamed reference point | https://www.openstreetmap.org/way/571289118 | 3 metres |
| WA26-186 | NULL / Unnamed reference point | https://www.openstreetmap.org/way/571289120 | 9 metres |

These are **not** geospatial positional-accuracy statistics: the OSM way center is *not* a surveyed dam-wall position. Three point references near three OSM ways are **not** automatically three verified physical dams; neither are the two Gusau records a confirmed duplicate.

## Stage W automated, bounded research workflow

\`tools/build_stage3d_w_lineage_eo_discovery.py\` first checks both independently persisted public-source review objects, ensures their 19 source IDs/names and statuses align, verifies exact original publisher hashes and pinned research map digest, checks the five expected OSM way mappings, and refuses any record suggesting confirmation or release.

For each of five points, it requests the specific OSM way history from the [OpenStreetMap API v0.6](https://wiki.openstreetmap.org/wiki/API_v0.6) and extracts only edit/version timestamps, \`source*\` tag **keys**, and a flag if the explicit source tag mentions the 2026 publisher. It never exports OSM editor identities, free-text comments, user IDs or changeset descriptions. **A missing source tag does not prove independent lineage**; an older edit predating the publication date is likewise not proof of source independence, because the 2026 compiled dataset can incorporate older records.

It then searches the [Element 84 Earth Search STAC API](https://element84.com/earth-search/) for **Sentinel-2 Collection 1 Level-2A** item metadata intersecting each original source reference coordinate. It uses only two explicit review periods:

- \`historical_2019\`: 1 January–31 December 2019
- \`recent_2026\`: 1 January–29 October 2026

The query is limited to 40 items per case and period. Up to three low-scene-cloud metadata links are shortlisted per period, with acquisition time and a publisher STAC item link. The image pixels are **not downloaded, screened, interpreted, or classified**. Scene-wide \`eo:cloud_cover\` **is not point-level cloud cover**, and an archived scene's existence does not prove an operating or completed structure. The historical period should be supplemented with older aerial or engineering records whenever needed; its selection is an initial catalog screen, **not a known construction baseline**.

Earth Search provides STAC metadata for [Sentinel-2](https://earth-search.aws.element84.com/v1/collections/sentinel-2-c1-l2a). Under the [Copernicus Sentinel data notice](https://cds.climate.copernicus.eu/licences/ec-sentinel), imagery is openly available subject to source terms and without guarantees of suitability. OpenStreetMap data are © OpenStreetMap contributors under ODbL, https://www.openstreetmap.org/copyright . ODbL features remain separately attributed research context, not a silently merged CC BY public GIS facility dataset.

## Failure mode and publication gate

OSM history 404/timeout or catalogue failure becomes \`LOOKUP_UNAVAILABLE_NOT_INDEPENDENT\` or \`CATALOG_UNAVAILABLE_NOT_NO_IMAGERY\`, **not** no dam/no satellite data. A clean STAC response without eligible scene metadata becomes \`NO_USABLE_CATALOG_ITEMS_NOT_NO_IMAGERY\`. No status is an automated asset confirmation.

PR builds run **synthetic tests only**. The existing on-main publisher intake regenerates Stage U and V review objects, then runs Stage W history/STAC metadata lookups. All Stage W output is archived in **review-only GitHub Actions artifacts**, not the deployed site directory. The strict Pages file allowlist remains unchanged. Independent browser QA also tests the new source gates using synthetic records and checks all existing public interactions.

The next site-level evidence step will inspect correctly georeferenced **image pixels** and dated project/construction/field records, investigate structural existence and geolocation uncertainty, assess independence of source lineages, and obtain accountable human editorial/rights authorization before any separate public confirmed-dam release PR. **No new confirmed or unnamed dam appears from Stage W alone.**
