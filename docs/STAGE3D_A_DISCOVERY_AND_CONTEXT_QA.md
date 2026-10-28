# Basin Nexus NG — Stage 3D-A state discovery and Stage 3C-C private context integrity

Date: 28 October 2026. Release: v1.9, subject to successful production GitHub Actions.

## Public source-safe geographic discovery

The Knowledge page now combines catchment name/alias, four source section themes, engagement year, host city, and a **state/FCT geographical overlap** filter. The last dimension uses the previously released `site/data/admin_crosswalk_provisional.json`, specifically the 2022 GRID3 via geoBoundaries approximate polygon intersections, not an invented administrative assignment.

The same catchment can be returned for multiple states. The filtered card displays an approximate, rounded km² intersection for the selected state and repeatedly labels the calculation as provisional. **Overlap does not prove that workshop participants came from that state, that stakeholder statements are about that state, or that a resource or infrastructure asset is located there.** Workshop host-city metadata is a wholly separate dimension.

All 20 catchment IDs, map boundaries, modelled FAO rivers, 2022 administrative layers, source-coverage metadata allowlist and evidence-release policy are preserved. The change does not introduce any actual individual stakeholder claim or mapped asset.

## Private context-integrity QA

`tools/stage3c_source_context_qa.py` is a reproducible, generic reviewer utility. It accepts the private 88-candidate editorial pilot and repeated restricted 3B principal source-line register exports. It verifies source-ID and original candidate ID pairing, exact statement wording, section, extracted locator, and catchment reference, then checks the next two source-line records for same-section context when a likely fragment is found.

Example, in an owner-restricted environment **outside the public repository**:

```sh
python tools/stage3c_source_context_qa.py /secure/private_88.txt \
  --source-register /secure/private_kano_lines.txt \
  --source-register /secure/private_sokoto_lines.txt \
  --source-register /secure/private_kwara_lines.txt \
  --source-register /secure/private_lokoja_lines.txt \
  --source-register /secure/private_gombe_lines.txt \
  --out /secure/private_context_qa.json
```

It refuses any input or output inside the public repository, refuses overwriting, emits only aggregate counts, and hard-codes zero new public approvals. Neither source excerpts nor identifiers are printed or written to the QA result. GitHub CI only tests synthetic input and does not access or upload restricted Drive content.

The heuristic checks **adjacent extracted source lines only**, not full original page/paragraph tables. Exact source matching verifies traceability, not truth, publication permission, location validity or complete textual context. Human rights/privacy/editorial review and independent location QA are still required for actual publication.

## QA and acceptance

The GitHub Pages prepublication workflow executes the new synthetic integrity suite, existing stakeholder privacy safeguards, original geometry/network validators, JavaScript syntax checks and desktop/tablet/phone browser tests. The parallel PR browser QA checks State/FCT filters for grounded examples (Plateau, Niger and FCT), combined-filter reset and unchanged catchment map controls.

This feature is an incremental geographical discovery experience; the complete thematic evidence catalogue remains gated by record-specific clearance.
