# Basin Nexus NG — Combined Stages 3D-AA/AB/AC/AD: independently sourced review lead reconciliation

**29 October 2026. Publication decision: HOLD; ZERO individually independently confirmed dams.**

## Source and publication baseline

The original Kouassi et al. 2026 CC BY 4.0 publisher-source data have 189 compiled Nigeria-labelled SCMP catchment intersections, 71 source-named, 118 source-unnamed. An opt-in **unverified research-source** map displays 186 (68 original names + 118 unnamed) and withholds the disputed three names Souapiti, Mambilla and Kafin Zaki. The source research points are not a government-certified facility inventory. The confirmed dam register remains **zero** and approved public individual stakeholder statements remain **zero**. All restricted SCMP texts are excluded.

## AA — OSM **way geometry** reconciliation, not wall survey

Earlier Stage V measured point-to-OSM *way center* distance for five research cases (two Gusau, three Plateau). These are not wall measurements. Stage AA requests only the exact five OSM way IDs' node geometry from the OSM API \`/way/{id}/full\`, checks \`waterway=dam\` remains tagged, and computes closest approach between the original compiled reference and the **digitized OSM line** in a local azimuthal-equidistant metric projection. This is an improved *map digitization proximity* diagnostic and **not** a surveyed dam-wall coordinate, a facility match, independent existence proof, or positional accuracy assessment. If the OSM API is unavailable or a way tag changes, the state is \`UNAVAILABLE_NOT_NO_DAM\`. Coordinates and OSM lines remain in review-only ODbL-attributed files, not published Pages layers.

Five fixed source cases: WA26-003 / way 272558892; WA26-083 / way 272558893; WA26-184 / way 571289117; WA26-185 / way 571289118; WA26-186 / way 571289120. No automatic merging of two Gusau entries or three clustered Plateau references.

## AB — genuine documentary context, separate coordinate types

A valuable **newly located** official source adds context for the Gusau case, with two deliberately non-interchangeable coordinates:

1. [Nigeria Federal Ministry of Water Resources, *National Dam Inventory*, Gusau Barrage](https://dams.ng/permanent_assets/dams.pdf), item visibly listed under **Gusau Barrage**, location **N12.14638, E6.66952**, reported earthfill, completed 1991. The web PDF's complete publication date was **not independently verified**. Original WA26-003 compiled reference is **N12.1464, E6.6703** — about **84.9 m** from the inventory record. This supports a plausible **named infrastructure lead**, not independent proof that the two point records or the OSM digitized barrier are the same surveyed structure.
2. [Federal Nigeria Integrated Water Resources Management Commission / JIL Engineering Associates, *Development of Sustainable Water Footprint in Nigeria*, final report **August 2020**](https://niwrmc.gov.ng/wp-content/uploads/2026/01/Final-Water-Footprint-Report-for-IWRM.pdf), 2020 surface-water abstraction table, **Gusau Dam: N12°08′48.5″, E6°40′21.1″**, converted to **N12.14680556, E6.67252778**. This is an **abstraction intake coordinate**, not an independently surveyed dam wall. It is approximately **246.6 m** from the original source reference point. The URL path includes 2026; this does **not** change the 2020 report preparation date.

A 2016 academic field sampling account also distinguishes **Damba Dam** and **Wanke Road Dam** in the wider Gusau area, but it does not furnish reviewed coordinates that reliably match the separate WA26-083 source point; it **must not be used to automatically name WA26-083**. Source: [International Journal of Science for Global Sustainability, 2016](https://fugus-ijsgs.com.ng/index.php/ijsgs/article/download/263/226/227).

The government lists are *documentary leads*. Neither source's independence from the 2026 compiled dataset has yet been provenance-audited and no observation date, ground-photo/survey receipt, uncertainty or accountable facility-match decision is available. The federal report concerns a water abstraction point that could be displaced from the barrier. The production gate cannot be satisfied by copying these document coordinates into confirmed site records.

## AC — historical Sentinel SCL temporal description, not reservoir change

All five original compiled-source reference points already have ten actual 2019/2026 Sentinel-2 true-colour and SCL pixel chips acquired in Stage X/Y/Z with site-center cloud QA; **all ten optimally selected windows met the 85% clear target**. Stage AC extracts exact source dates and *central SCL class-6 water fraction among SCL clear pixels* from these archived pixel QA artifacts and reports the **descriptive 2026-minus-2019 change in percentage points**. The source dates differ by season (late November/December 2019 vs October 2026); SCL is a scene classifier and can vary with phenology, water level, processing and residual cloud/shadow. The percentages are not delineated surface-water area, reservoir storage, dam construction date, a barrier detector, an engineering result or cross-era harmonized spectral change. Null QA remains null, never zero.

## AD — unified accountable independent-evidence receipt package

A final review-only machine-readable evidence matrix preserves all five IDs, their **original** source point coordinates, OSM geometry-proximity observations where available, official documentary leads (only WA26-003 is explicitly coordinate-context linked), original Sentinel acquisition dates and SCL descriptions, and **12 intentionally null human evidence receipt fields per case (60 blank receipts)**. No field supplies an automated positive verdict. The reviewer still needs independent proof of physical barrier existence, defensible wall survey location and measured uncertainty, status at an identified date, independent document/source provenance, rights/privacy and named accountable public release approval. Unnamed source label is *not* a confirmed unnamed dam.

## CI and output contract

\`tools/build_stage3d_aa_ad_evidence_reconciliation.py\` and its synthetic tests execute in original-source GitHub Actions. On PR: synthetic tests only (no real OSM downloads), alongside the existing browser tests. On merged \`main\`: the code consumes four verified source-only research files previously regenerated by the publisher intake: Stage U 19-case packet, Stage V OSM context, Stage W history/scene metadata, Stage Z **actual RGB+SCL pixel QA**; then checks bounded OSM line geometry and produces:

- \`review/stage3d_aa_ad_evidence_REVIEW_ONLY/stage3d_aa_ad_research_receipts_NOT_CONFIRMED.json\`
- \`review/stage3d_aa_ad_evidence_REVIEW_ONLY/stage3d_aa_osm_digitized_lines_ODbL_NOT_SURVEYED.geojson\`
- \`review/stage3d_aa_ad_evidence_REVIEW_ONLY/STAGE3D_AA_AD_REVIEW_MATRIX.md\`

All live output is in a separately named *review-only* GitHub Actions artifact. No \`site/data/\` modifications are authorized. The exact main SHA must have successful publisher-source intake, independent desktop/tablet browser tests and production site deployment before claiming this combined stage fully complete.
