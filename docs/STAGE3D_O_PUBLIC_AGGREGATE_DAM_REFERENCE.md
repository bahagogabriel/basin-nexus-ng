# Basin Nexus NG — Stage 3D-O: Public aggregate 2026 dam-reference catchment counts

Date: 28 October 2026.

## Source provenance and actual independent acquisition

Kouassi et al. (2026), *West Africa Dams and Reservoirs Dataset*, University of Bonn bonndata V1, CC BY 4.0, DOI `10.60507/FK2/YLDK1Y`. Original CSV DOI `10.60507/FK2/YLDK1Y/WKZDRQ` and MD5 `046b106da1e3a57ec2f1c461fe411b26`; original shapefile ZIP DOI `10.60507/FK2/YLDK1Y/PQBMFO` and MD5 `a87f9b4ef2e96625b737ffac8595c138`. Both files verified in *actual* automated source-acquisition run 40726268716. The source ZIP's physical .prj was parsed with pyproj and confirmed as WGS84 EPSG:4326. Original csv encoding is cp1252.

From **1,429 West African dam source rows**, the published `Country` field labels **231** Nigeria. All 231 have numerically valid longitude/latitude fields, no duplicate source IDs, no exact repeated coordinate pairs at seven decimals. Shapely `covers` against the 20 **existing simplified SCMP display** polygons yielded:
- 189 Nigeria-labelled source rows intersect **one or more** of the displayed study catchments;
- 42 did not intersect the catchment polygon set;
- 18 catchments have at least one source-point match; Gaji-Lamurde and Yedseram have none;
- In this specific dataset and polygon set, no Nigeria-labelled source point intersected more than one catchment, and none fell exactly on a polygon boundary.

The 189 matches are **spatially intersecting positions from a compiled source**. They are not 189 independently field-verified physical dams, 189 working reservoirs, a complete inventory of Nigerian dams, or 189 newly approved stakeholder facility records. The source paper warns that small-scale structures may be underrepresented and georeferencing may be inconsistent.

## Public artifact and UI

`site/data/wa_dams_2026_catchment_reference_counts.json` contains the 20 counts and the full method, source licence, original checksums, CRS validation, no-duplicate checks and limitation statement. It contains no original dam-name strings, source facility IDs or coordinates. The Data page displays a clearly attributed source summary and an accessible expandable 20-row count table plus a JSON download. Individual source-points remain unavailable on the public map.

Counts in original `site/data/catchments.geojson` ID order:

| ID | Reference source points |
|---|---:|
| SCMP-C01 | 2 |
| SCMP-C02 | 12 |
| SCMP-C03 | 0 |
| SCMP-C04 | 1 |
| SCMP-C05 | 21 |
| SCMP-C06 | 33 |
| SCMP-C07 | 3 |
| SCMP-C08 | 6 |
| SCMP-C09 | 1 |
| SCMP-C10 | 10 |
| SCMP-C11 | 1 |
| SCMP-C12 | 1 |
| SCMP-C13 | 10 |
| SCMP-C14 | 17 |
| SCMP-C15 | 26 |
| SCMP-C16 | 10 |
| SCMP-C17 | 9 |
| SCMP-C18 | 5 |
| SCMP-C19 | 0 |
| SCMP-C20 | 21 |
| **Total** | **189** |

## Boundaries and caution

The supplied catchment polygons are simplified display derivatives, not legal catchment delineations. A source record with no intersection may be located outside the studied polygons or may suffer positional error. A zero does **not** mean the catchment contains no dam. Regional datasets can repeat sources or share positional ancestry, and simple no-exact-duplicate checks do not establish unique facility identity. No corroboration against field surveys, engineering owners, current asset operation, dam capacity definitions or restricted stakeholder statements has occurred.

Publication of source facility points on a map is a separate future editorial/scientific decision. This aggregate release leaves the v1.12 **approved individual stakeholder evidence catalogue empty** and does not require or imply permission to release any of the private workshop source material.

## Automated acceptance

`tools/test_wa_dam_reference_counts.py` checks all 20 totals against the document, the source MD5s and licence, verifies zero individual records/coordinates and source-index separation, and checks every table row in the public HTML. Existing public allowlist, responsive/browser/map/GIS and private-source safeguards are still mandatory. Any changes to the source dataset, match method, new source points or public map need a new reviewed PR.
