# Stage 3D-N — Licensed dam-source spatial candidate audit (research only)

28 October 2026. **This does not release dam locations or change the approved stakeholder publication status.**

## Confirmed primary source acquisition

The original bonndata CSV of Kouassi et al. (2026), DOI `10.60507/FK2/YLDK1Y/WKZDRQ`, was downloaded by GitHub Actions run 40725165877 on 28 October 2026. Publisher and computed MD5 both equal `046b106da1e3a57ec2f1c461fe411b26`. The file uses Windows cp1252 rather than pure UTF-8, contains **1,429 regional rows**, and the field `Country` contains **231 rows labelled Nigeria**. The original longitude and latitude header names are **Long_X** and **Lat_Y**. Source metadata reports CC BY 4.0. Thus, 231 is a source-country row count, **not** the number of verified or unique dams within Nigeria, nor a count within the 20 catchments.

The CSV exposes fields such as Dam_Name, Dam_Year, Res_Vol, Res_Vol_T, Res_Area, and Main_Sourc, but their exact measurement definitions and positional accuracy need source-dictionary and engineering review; none is promoted into the public evidence catalogue.

## New reproducible review-only overlay

`tools/review_wa_dam_catchments_2026.py` performs:
1. Fetch the exact, MD5-verified original 2026 CSV, and independently fetch the corresponding published original dam shapefile ZIP. Expected ZIP DOI `10.60507/FK2/YLDK1Y/PQBMFO`, publisher MD5 `a87f9b4ef2e96625b737ffac8595c138`.
2. Inspect the ZIP's physical `.prj` file using pyproj and **stop unless it resolves to EPSG:4326**; the CSV's Long_X/Lat_Y values are not interpreted as geographic degrees without this check.
3. Validate 20 supplied, simplified SCMP WGS84 catchment polygons. Parse source latitude/longitude as numbers, flag missing/invalid coordinates, repeated source IDs and exact repeated coordinate pairs.
4. For Nigeria-labelled source rows, compute candidate point-in-polygon overlaps using Shapely `covers` (includes boundary), retaining counts by catchment. A source row may intersect more than one overlapping catchment; summed intersection counts are **not unique dam counts**.
5. Save ONLY a separate **aggregate QA report** in GitHub Actions artifacts, never raw source text, facility names, individual IDs, coordinates or source CSV/ZIP. No map layer or table is published.

The source geometry and source-country classifications have their own limitations. Even if a point is inside the SCMP polygon, it is still a **compiled dataset position**, not an independently surveyed facility. Accuracy may differ by source and size; some dams or small ponds may be absent. A country label mismatch, coastline displacement or boundary overlap needs independent review.

### Publication boundary

The public Data page and source-registry JSON now note the independently verified *231 source rows labelled Nigeria*, with no catchment count asserted before overlay QA. All public individual stakeholder records remain **zero**. No coordinates or entity matching from owner-restricted sources are in public GitHub.

Any later public water-infrastructure layer needs an explicit separate PR documenting the source's point-level lineage/uncertainty, possible duplicates, field-verification status, and the geometry-matching policy, plus full accessibility, performance and rights checks.

## Testing

Synthetic tests cover EPSG:4326 vs projected CRS, wrong original ZIP hash, bad/missing source locations, shared/overlapping catchment membership, invalid source ID reuse, exact coordinate duplicates, country filtering, boundary inclusion and zero public export. GitHub's source-only workflow runs these tests with pinned `shapely==2.1.2` and `pyproj==3.7.2`. The existing Pages production workflow and privacy gates continue unchanged.

## Next review

Retrieve the aggregate QA artifact on completion, inspect the **actual** original ZIP CRS and number of candidate overlaps, then decide whether to advance to a specifically-labelled **compiled public reference overlay** with independently checked sample sites. No numerical capacity conflict or mineral reserve is resolved by spatial intersection alone.
