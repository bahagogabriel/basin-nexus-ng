# Basin Nexus NG — Stages 3D-L and 3D-M: Public reference discovery and reproducible external-source preflight

**Baseline:** 28 October 2026, 20 SCMP catchments; approved individual stakeholder evidence: zero. This is a research-source and data-governance improvement; not an infrastructure inventory or authorization to release precise positions.

## Newly independently located public source routes

### 1. West Africa Dams and Reservoirs Dataset (Kouassi et al., 2026)

Publisher: bonndata, University of Bonn, dataset V1, released **26 February 2026**. Dataset DOI: `10.60507/FK2/YLDK1Y`. Journal study: *Earth System Science Data* (1 October 2026), DOI `10.5194/essd-18-7227-2026`. Reported **West Africa-wide** totals: 1,429 dam point entries and 1,258 reservoir polygons, across West Africa; **not** counts inside any of the 20 Nigerian SCMP catchments. Data-use licence at publisher: **CC BY 4.0**. Entry precision/coverage is variable; authors warn of underrepresentation of small-scale structures and inconsistent georeferencing. These are compiled source points, **not field-validated coordinates at each Nigerian facility**.

- Dataset: https://bonndata.uni-bonn.de/dataset.xhtml?persistentId=doi%3A10.60507%2FFK2%2FYLDK1Y
- Primary published data article: https://essd.copernicus.org/articles/18/7227/2026/
- Pinned publisher CSV DOI: `10.60507/FK2/YLDK1Y/WKZDRQ`, published MD5 `046b106da1e3a57ec2f1c461fe411b26` (255 kB, regional point dataset).
- Pinned CSV URL accessed by script: Dataverse `api/access/datafile/:persistentId/` with the exact source persistent identifier. The publisher data file must match both checksum and count before a summary is considered valid.
- Reservoir polygon archive separately available at `10.60507/FK2/YLDK1Y`. Polygon CRS, geometry quality, point/reservoir linking and source definition are not yet reviewed; do not project them from guessed metadata.

### 2. NGSA primary mineral geoscience systems

The Nigeria Geological Survey Agency describes the **National Mineral Occurrence Database** (Microsoft Access) covering commodity, state, type, grade, reserve, geology and mineral association. NGSA also describes its read-only **Nigerian Mineral Resources Decision Support System** (NMRDSS). These pages **do not supply a reviewed, licensed download of primary source records** for this atlas. Website descriptions and possible screenshot map points do not establish an independently verified field sample, tonnage/reserve or reuse permission.

- https://ngsa.gov.ng/database/
- https://ngsa.gov.ng/decision-support-system/
- https://ngsa.gov.ng/geodata-centre/

### 3. Independently compiled NGSA-map-derived records

A third-party GitHub/Zenodo 2026 resource compilation reports 974 map-derived occurrence rows (https://github.com/whoisolaxtra/nigeria-mineral-resources-database). It is explicitly not an official structured NGSA database or independent geology survey. The compiler's published CC BY 4.0 does **not necessarily convey rights to redistribute the underlying NGSA 2023 map or guarantee positional/interpretive accuracy**; establish rights and source-lineage before considering inclusion. Do not treat map symbols as mineral reserve estimates.

## Mandatory engineering and geoscience distinctions

- Independent source DOI, licence and data file integrity are separate checks from *site identity*, actual geographic position and current operation.
- Published country label and coordinate source precision are not validated geospatial intersections. No country total, national inventory or catchment count may be asserted until the source file is actually inspected and a reviewed spatial method executed.
- A field-verified position requires independent site-level coordinate methods, review and time appropriateness; publisher's assembled point locations remain *compiled map reference positions*.
- A dam capacity without a consistent definition (gross, live, design etc.) must not override the eight owner-restricted conflicts.
- A derived mineral-occurrence map cannot independently verify site-specific ore reserve quantities.

## Automation and acceptance

`tools/preflight_wa_dams_2026.py` accepts a *previously obtained exact-source CSV* or downloads the **pinned** original with bounded network retries. It verifies the publisher MD5, expected 1,429 rows, stable bounded schema, safe country field detection and emits only an aggregate report. It **cannot** publish dam locations, raw names, individual source rows, claims, coordinates or stakeholder links. Country labels are classified as preliminary and no coordinate overlay is performed.

GitHub Actions workflow `.github/workflows/wa-dam-source-preflight.yml` runs synthetic tests for every PR and attempts the real licensed source download on main; archives only the aggregate QA JSON. Failure of the remote download or a changed checksum is a legitimate **blocking status**, not a reason to infer data. The existing Pages production workflow tests the public source-registry integrity and the empty approved evidence catalogue.

**Next stage after successful source preflight:** inspect the source data dictionary, confirm CRS, row uniqueness and known positional issues; compute Nigeria-only candidates, catchment intersection with source-lineage QA, duplicate/cross-catchment relationships and explicitly uncertain point visualizations—only after scientific review. A separate public-data PR should document attribution and boundary methodology. No original 20-catchment geometry, 2025 LULC mosaic (another project), private GIS outputs or existing live page data has been rewritten here.
