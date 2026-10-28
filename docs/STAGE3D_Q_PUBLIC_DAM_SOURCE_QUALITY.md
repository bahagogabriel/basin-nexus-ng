# Basin Nexus NG — Stage 3D-Q: Transparent published reference quality

28 October 2026. This stage publishes **only aggregate source-attribute quality**, never individual dam points or stakeholder records.

## Independent original-source audit completed

Live GitHub Actions run `40733789032` acquired and matched the exact original Kouassi et al. 2026 bonndata dam CSV and original dam Shapefile ZIP. Source CSV MD5: `046b106da1e3a57ec2f1c461fe411b26`; original ZIP MD5 `a87f9b4ef2e96625b737ffac8595c138`; source .prj EPSG:4326, licence CC BY 4.0. Source: https://doi.org/10.60507/FK2/YLDK1Y; journal methodology: https://doi.org/10.5194/essd-18-7227-2026.

**Country-labelled source records:** 231 Nigeria; 84 with usable Dam_Name; 147 without a usable name; 231 with a Main_Sourc label (a label is NOT independent geospatial validation); 76 with recognizable Dam_Year; 155 without. Five exact normalized-name groups recur across 11 source rows; there are 10 geodesic point pairs closer than 1 km, including one pair of similarly named entries. One pair is within 250 metres; 15 source rows have at least one other source point closer than 1 km. These are potential-source-review flags, **not established duplicate facilities**; neither nearby position nor repeated name proves sameness.

**Within the 20 supplied simplified catchment display polygons:** 189 published compiled source point intersections, of which 71 have a usable name, all 189 have an original Main_Sourc label, and 62 have a recognizable year; 42 Nigeria-labelled records do not intersect the study polygon set. No individual dam identity, physical uniqueness, structure operating status, current reservoir capacity or survey-grade coordinate has been verified by this project. The original article describes significant underrepresentation of small and recently constructed infrastructure; no catchment can be called dam-free on the basis of a zero source match.

## Publication

`site/data/wa_dams_2026_source_quality.json` contains national and within-study completeness totals plus **only** 20 by-catchment count summaries. This does NOT include Dam_Name values, source point identifiers, WGS84 latitude/longitude or original CSV rows. It carries the original publisher MD5s, source DOI, licence, timestamp, QA run and explicit NO_POINT_LAYER status.

The Knowledge **Infrastructure research references** lens shows for each selected catchment the number of compiled reference points, how many are named and how many have a recognizable source year. Existing search/area/admin filters preserve the result subset; users can order by compiled source count or named-source count. The standard public metadata CSV export appends these three descriptive counts, with empty fields if the source-quality file is missing or fails its integrity check. The page fails closed without losing map usability or claiming there are no assets.

The Data page presents national and catchment completeness figures, an explanation of possible duplicates and a source-quality JSON download next to the previously released 20-catchment aggregate count table.

No original point has been published on the atlas map, and **the approved individually reviewed stakeholder evidence catalogue still has zero records**. No restrictions or permissions are inferred from original workshop data.

## QA, caveats and future work

`tools/test_wa_dam_source_quality.py` prevents publication of individual coordinates/names, asserts the real original 231/84/76 and catchment 189/71/62 audited completeness, validates all 20 by-catchment counts against the prior reference-count dataset, checks exact source MD5s and the zero approved-stakeholder record state. PR and production CI run the full GIS/browser/privacy suites, including an interactive thematic-source sorting and CSV integrity check.

**Future Stage 3D-R:** build an auditable source record identity review for the named entries by cross-referencing independently published engineering agency registries, positional uncertainty, update date and publication rights. Only a distinctly marked compiled **reference** layer may ever be considered for public map overlay, with a clear original DOI, licence, uncertain position and no assertion that the dam is active or surveyed. The original 147 unnamed Nigeria-labelled rows require higher scrutiny for identity and should not be silently given invented names.
