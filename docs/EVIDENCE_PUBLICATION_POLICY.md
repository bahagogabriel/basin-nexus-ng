# Basin Nexus NG — Evidence Release Contract

**Status: implementation policy; not public approval of any stakeholder record.**

Basin Nexus NG is a public geospatial knowledge atlas. Stakeholder submissions are valuable evidence but must not automatically become verified resources, functioning dams or geographically precise points.

The public index `site/data/stakeholder_coverage_index.json` documents which thematic headings exist across 20 engagement communiqués. It contains **no source quotations, attendance, signatures, personnel, private Drive links, unverified facility positions or resource observations**.

## Workflow

1. **Internal source intake:** index document, source identifier, section/table/row, report date, participating state/LGA and original claim. Store source records outside public GitHub and Pages.
2. **Internal claim reconciliation:** distinguish plans, proposals, projects under construction, abandoned assets, confirmed existing infrastructure and conflicting evidence. Keep all competing measurements and source anchors, never silently select an attractive figure.
3. **Spatial QA:** retain reported text locations separately. Only validated coordinates with documented method and uncertainty qualify for the public map.
4. **Explicit publication clearance:** assess source redistribution rights, privacy, sensitivity and consent. A publicly presented stakeholder-reported statement must be plainly labeled; independent verification is not implied.
5. **Public promotion:** generate a minimal `PublicEvidenceCollection` and run `python tools/evidence_publication_gate.py <file.json>` prior to inclusion. The existing Pages allowlist continues to exclude all evidence files until a specifically approved release stage and regression suite are introduced.

### Minimal public record

```json
{
  "record_id": "BN-EXAMPLE-ONLY",
  "catchment_ids": ["SCMP-C15"],
  "theme": "water_infrastructure",
  "record_type": "facility_report",
  "statement": "Synthetic example; not an actual dam or stakeholder claim.",
  "evidence_status": "stakeholder_reported",
  "source_reference": "Approved public attribution, when available",
  "source_locator": "Source section and paragraph number",
  "release_authorization": "PUBLIC-SYNTH-TEST-01",
  "location": null
}
```

Source provenance and context must be grounded in the original document. `release_authorization` is an identifier of a real review decision; do not invent it for actual records. The example is synthetic solely to explain the schema.

## Hard stops

- Public fields never contain personnel, private contact, signed material or source-drive IDs.
- Reported values are not interchangeable with independently verified measurements.
- Administrative/geographic intersection does not validate a facility's coordinates.
- No modeled river reach can stand in for a surveyed dam point.
- No proposed facility can be listed as operational without evidence.
- A record may be published as **stakeholder reported** *only after explicit release clearance*, with no false verification claim. Its location remains null until spatial QA is independently passed.

The validator is a defense-in-depth policy gate, not a substitute for legal permission, human publication approval or fact checking.
