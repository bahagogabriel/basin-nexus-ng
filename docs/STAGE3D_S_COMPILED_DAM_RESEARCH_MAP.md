# Basin Nexus NG — Stage 3D-S: Opt-in compiled 2026 dam *research references*, not a verified dam map

28 October 2026. This stage is a cautious, optional public-reference layer and **does not publish any independently confirmed dam facility**. Its purpose is to let researchers explore what the *source* mapped, alongside our unchanged 20 catchments, without falsely treating source coordinates as surveyed site positions.

## Original source and checks

Kouassi et al. (2026), *West Africa Dams and Reservoirs Dataset*, University of Bonn bonndata V1, DOI https://doi.org/10.60507/FK2/YLDK1Y (CC BY 4.0). Original publisher CSV MD5 `046b106da1e3a57ec2f1c461fe411b26` and Shapefile ZIP MD5 `a87f9b4ef2e96625b737ffac8595c138`. Original .prj confirmed EPSG:4326. Direct source QA: GitHub Actions 40740216075, review artifact `west-africa-2026-public-source-research-candidates-unverified`. 1,429 regional source rows; 231 labelled Nigeria, of which 189 compiled source points intersect at least one supplied simplified SCMP study-catchment polygon (71 have source-reported names and 118 are unnamed in source). Those 189 **are not independently verified physical dams**.

The source-only preparatory candidate artifact was inspected before release and matched the existing 20-catchment aggregate count audit. All names and coordinates in the compact web preview were taken from these public CC BY 4.0 compiled point records, not from private SCMP stakeholder files. The full 186-item preview payload has a source-derived SHA-256 integrity test after three reviewed exclusions.

## Disputed names withheld from the optional map (three, not erased from original QA totals)

1. **Souapiti** — source label placed within the Nigeria-labelled reference subset, but the actual Souapiti hydroelectric dam is documented in **Guinea**, including by Guinea's Ministry of Energy and Hydraulics (https://mahh.gov.gn/) and the World Bank's country reporting. The Nigerian reference point remains unconfirmed and is not shown as a dam.
2. **Mambilla** — public Nigerian State House (18 September 2026) and African Union/PIDA references describe a historically delayed **hydropower project**, not an established completed dam at this compiled source point. 2026 delivery discussions do not independently establish completed infrastructure.
3. **Kafin Zaki** — the Upper Benue RBDA federal Eyemark portal continues to label the dam's redesign/EIA project as not started (updated September 2026); other agency and press records describe a long-delayed incomplete structure. Neither constitutes confirmation of a completed reservoir/dam at the published point.

These are reviewed named source-record mismatches. Other points are NOT silently presumed accurate merely because they have not yet been flagged. Do not subtract them from the original *source-level* 189 count, which remains the reproducible spatial intersection result. The optional **display** is 186 source-only reference points, of which 68 retain original names and 118 have no source name.

## Public map behaviour

- **Default off**. An explicit mapbar button and a Layers entry control the research-reference layer.
- Named original-source points are amber; unnamed original-source points are grey. On click, the card shows **source-reported name** or **Unnamed reference point**, catchment, published source link/licence and an explicit nonverification warning. No unknown name is invented.
- The map never labels any of these 186 features as a **confirmed dam**. No current operating state, capacity, precision score, field survey or independent existence confirmation is attributed to the source.
- When the layer is hidden it has no visible map markers and no hit-test priority; existing watercourse, LGA, pan, zoom and touch gestures remain active.
- When a catchment is selected, only that catchment's compiled research source points remain visible. Three withheld records are never drawn. The separate `site/data/confirmed_dam_sites.json` remains 0 records.
- The Data page provides the original 189-source count, quality completeness, three reviewed exclusions, original DOI, and opt-in research preview download. Aggregates and point previews must not be conflated.

## What remains outstanding

Actual verified unnamed physical dam sites still require independent evidence of a dam wall or existing structure (not an unbuilt proposal), a documented trustworthy positional verification method plus uncertainty, source independence, rights and accountable review. This stage deliberately admits zero such records because none has passed all gates. For the 118 currently unnamed source points, "Unnamed reference point" is a source-metadata condition, **not** proof of an existing unnamed dam.

The following remains independent of this layer: the 20 institutional SCMP communiqué source-index records, 0 individually approved stakeholder claims, 52,012 catchment-clipped FAO modeled river reaches and all existing maps.

## Test gates

`tools/test_compiled_dam_preview.py` checks exact published source SHA-256, original file MD5s, country/intersection baselines, 20 catchment counts, name completeness, explicit 3-record quarantine, and 0 confirmed/dam public claims. Existing production allowlist, privacy checks, WGS84 reference, browser, touch and source-candidate tests must all pass. The research-preview source position is not a quality-guaranteed coordinate; this is an explicitly described source-visualization service, not an authoritative GIS facility survey.
