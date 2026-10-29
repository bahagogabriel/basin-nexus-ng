# Basin Nexus NG — Stages 3D-AU–AX: bounded original-source FAO NEXT_DOWN exploration

**29 October 2026.** This four-stage leap builds on the published 20-catchment FAO AQUASTAT 2026 modeled river network and Stage AQ–AT comparison, without fetching other river datasets or touching public dam confirmation.

## Audited source graph (actual publisher-derived data)
- 20 catchments, 52,012 clipped source-feature copies from **51,906 unique original HYRIV_ID values**. Exactly 105 unique source IDs occur in multiple catchment clips. This is *not* evidence of 105 duplicated rivers or of two separate dams.
- Original publisher `NEXT_DOWN` ID classifications across the 52,012 clipped features: 51,887 next IDs available within the same selected catchment; **89** whose next original reach ID exists only in another displayed study catchment; **32** whose NEXT_DOWN targets lie outside the available 20-catchment index; and **four** source-terminal/unlinked entries.
- **33 directional catchment-pair association types** among the source-record links. Multiple source links in both directions can occur between some pairs of catchment study areas, without establishing physical upstream/downstream catchment hierarchy.
- **Zero cycles** among the source IDs available in this study. No claim is made about source links outside the clipped coverage.
- Original source reach files, registered catchment IDs, per-file byte lengths, SHA-256 digests, CC BY 4.0 and source upstream-area class totals are enforced by `tools/build_stage3d_au_av_fao_topology.py`. An inconsistent duplicated source ID, self-link or changed source digest fails verification.
- A compact, 1,272,508-byte source-only lookup file preserves exactly [original HYRIV_ID, original NEXT_DOWN (or null), 20-catchment membership mask] per unique reach. The summary identifies missing links explicitly rather than pretending the river terminates. Both files are checked into `site/data` only after real-source CI and never derived from stakeholder documents.

## Compatible stages

**AU — Publisher topology QA:** Validate all 20 original source files and reconcile 52,012 clipped copies to 51,906 unique publisher IDs. Reject source/ID disagreement and check bounded graph cycles.

**AV — Source association summary and compact index:** Derive 20-catchment link-status distributions, 33 source-linked catchment pairs, unresolved target IDs and an auditable compact lookup. Associate source-reach IDs between clips; never assert surveyed channel contact or hydrological connectivity.

**AW — On-demand bounded source-ID tracing:** A selected modeled river popup offers an optional NEXT_DOWN inspection. The browser lazy-loads the lookup only after the user requests it; it walks **at most 40 original source reach IDs**, detects cycles, and reports whether the trail hit a publisher terminal/unlinked record, a target outside the 20-catchment source index, or the safety limit. Only already-loaded segments in the selected catchment are highlighted in orange. No unreferenced across-boundary line is rendered or inferred.

**AX — Cross-catchment audit interface and release QA:** A 20-row public Data-page table shows within-catchment NEXT_DOWN, references only in other study catchments, references outside indexed coverage, and source-null/terminal counts. Each row can open the selected catchment. The public gate recomputes the exact source summary and index bytewise before deployment; independent browser QA covers lazy loading, real map reach inspection, bounded trace, tampered summary rejection, and regression of the existing atlas.

## Important scientific and licensing boundaries
`NEXT_DOWN` is a **HydroRIVERS-derived, original FAO modeled reach identifier**. The source reaches were clipped to display simplified catchment boundaries. Link counts alone do not prove spatial adjacency, hydraulic continuity, flood propagation, stream order, direction between whole catchments, model accuracy or travel distance. A NEXT_DOWN ID missing from the study is an incomplete index, never a surveyed river endpoint. Orange highlighting shows only clipped, visible source geometry and is not an authoritative river route.

Source: FAO AQUASTAT 2026 (model version dated 2026-06-15), HydroRIVERS-derived 15-arcsecond network, **CC BY 4.0**, https://data.fao.org/catalog/dataset/e22667af-3977-4e9f-b58b-67fb91b0fa87. Original `site/data/detailed_river_manifest.json` and per-catchment reach files remain unchanged. Data views retain the modelled-only disclaimers of Stage AQ–AT.

The public dam layer retains **zero independently confirmed facilities**, the optional compiled source point overlay remains **186 unverified references**, three identity disputes remain withheld, and there are still **zero** approved individual private stakeholder statements. The standalone offline dam review kit from Stage AM–AP remains available separately; no private field or source material was added.

## Next natural checkpoint
Trace results can underpin a more rigorous connection/network study only after spatial-neighbor geometric QA and independent technical review. Do not compute travel time, upstream contributing area, hydraulic routing or flood-risk decisions from these clipped source IDs alone. The dam-confirmation work remains independently gated on authenticated engineering/field evidence.
