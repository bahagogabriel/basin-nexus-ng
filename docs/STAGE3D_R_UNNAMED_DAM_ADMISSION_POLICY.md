# Basin Nexus NG — Stage 3D-R: Unnamed dams and evidence-tier admission policy

Date: 28 October 2026.

## Decision: confirmed unnamed physical structures belong on the confirmed infrastructure layer

A dam does **not** need a known proper name to be scientifically eligible for display. But there must be sufficient *independent* evidence that (1) the structure physically exists, and (2) the plotted position reasonably represents that dam or barrier, with appropriate uncertainty. Where an independently supported dam has no reliable name after documented search, its public card must read **"Unnamed dam"**, optionally with catchment identification. This is not an invented official toponym.

Keep these distinct layers and terms:

| Display tier | Allowed content | Map behaviour |
|---|---|---|
| Confirmed dam / known name | Existence independently substantiated, named by reliable agency/source, position validated, correct rights | Explicit verified-status marker; report verification method/date and uncertainty |
| Confirmed dam / name unknown | Same rigorous independently substantiated structure and position, no reliably established proper name | **Unnamed dam** with evidence/uncertainty/review fields; no inferred name, active/operational claim or capacity |
| Compiled research reference | Independently published regional compilation, validated file licence/checksum/CRS, but site existence or point accuracy **not independently confirmed** | Only in a separate **opt-in research-reference layer**, visibly distinct from confirmed facilities. Unnamed source records must be labelled "Unnamed reference point", never "Unnamed dam" |
| Unassessed, contradictory or missing physical evidence/position | Source absent, ambiguous, mismatched or unsafe | Hold from the confirmed map until corroboration; no invented coordinates |

A name on a compiled record is not proof of correctness. An unnamed structure can nevertheless be confirmed if independently corroborated. Do not automatically promote entries from a published dataset, private workshop table, OpenStreetMap alone or a single derived satellite classification. If physical verification is supported by independent engineering documentation and appropriately reviewed earth-observation imagery, preserve the image date, mapping method, spatial uncertainty, independent source family and reviewer. Reviewer-entered verification is a recorded decision, not an automatic algorithmic guarantee of scientific truth.

## Research candidate generation

The exact original Kouassi et al. (2026) WADR dam CSV (CC BY 4.0) is first checked against MD5 `046b106da1e3a57ec2f1c461fe411b26` and the paired original Shapefile ZIP against MD5 `a87f9b4ef2e96625b737ffac8595c138`; physical PRJ must identify EPSG:4326. `tools/build_wa_2026_dam_candidate_review.py` then clips *only* the 231 Nigeria-labelled publisher entries to the supplied 20 catchment display polygons and produces a preliminary 189-point licensed research review dataset, each point explicitly labelled **compiled source, unverified**. It retains only source DOI, source name if genuinely present, source-row identity pseudonym, catchment and location; it does not manufacture names, confidence scores, operational status, capacities or independent confirmation.

The output is initially a **review artifact only**, separate from `site/data`. Before public preview, inspect actual source records/geometry and source attribution, match the original 189/71 audited counts, check name and coordinate anomalies, validate the UI and carry through CC BY 4.0 attribution. The public Data page's existing aggregate 20-catchment source quality is unaffected.

## Confirmed facility release criteria

For individual confirmations, a specific, reviewer-approved evidence receipt must contain:
- Source-specific physical existence evidence, date and original source citation; distinguish a water body, a proposed project and a dam wall;
- A position validation method (survey/authoritative geospatial inventory or methodologically reviewed satellite interpretation), observation date, scale and explicit positional uncertainty, verified in the same coordinate reference;
- Documented source independence/lineage and resolution of conflicting identity;
- Proper name support **or a documented "name not found" review outcome**;
- Rights, privacy, public redistribution permissions and scientific editorial signoff.

The verified facilities ledger initially has **zero** records; even a CC BY 4.0 assembled point does not automatically satisfy independent field confirmation. No private SCMP claim may enter the public layer without the separate restricted-source publication gate.

## Next checkpoint

After the published-source research artifact has been inspected and automated QA passes, create an opt-in *compiled research reference* map for the 189 source points with an explicit nonverification warning. The confirmed-dam map layer remains empty until individual proof is available. Do not infer absence of dams from the 20-catchment reference source's two zero-count catchments.
