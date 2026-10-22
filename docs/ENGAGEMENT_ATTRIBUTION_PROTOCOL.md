# Institutional stakeholder evidence: attribution and release protocol

**Public baseline:** The map is v1.7. The Knowledge page shows engagement event metadata and source-section coverage for 20 catchments. Individual source reports, names, coordinates and raw claims remain private pending documented clearance.

## Attribution means origin, not certification

A report can be sourced to a **Strategic Catchment Management Plan (SCMP) institutional stakeholder engagement** attended by representatives of relevant institutions. This does **not** mean every participating institution endorsed every statement. Display the relationship accurately.

When a future statement is permitted to be made public, its attribution should use this pattern:

- **Evidence:** Stakeholder-reported (unless a distinct independent verification is documented).
- **Source:** SCMP institutional stakeholder engagement communiqué — *[catchment]*.
- **Engagement period:** Taken from the corresponding communiqué, not inferred from cloud file timestamps.
- **Source locator:** Public-safe section/paragraph or table-row reference. Private file IDs and Drive links are not public citations.
- **Meaning:** Attribute as “participants reported” or “engagement participants identified”, not as a ministry-certified fact.
- **Reported location:** State/LGA/community only when explicitly supported and privacy-reviewed; an unverified asset's map coordinates stay null.
- **Status:** Proposed, designed, incomplete, completed, abandoned or unknown as supported by source; never infer operation simply because a structure was mentioned.

### Release boundary

The user's preference to include stakeholder data with honest attribution does **not** by itself establish redistribution rights over every third-party submission. Institutional/source rights, privacy, sensitive locations, source-context review, ambiguity checks, an accountable approval decision and any spatial QA remain mandatory before an individual public record is published. Existing `docs/EVIDENCE_PUBLICATION_POLICY.md` and `tools/evidence_publication_gate.py` remain authoritative.

Signed copies, names and contact details, attendance records, raw source passages, private Drive IDs and internal registers remain outside public GitHub and Pages. The source event index is metadata only, and uses documented meeting dates/host cities from communiqués instead of pretending claims have already been released.

### Approved record pattern (synthetic illustration only)

> A participant described a hypothetical water project in a study area.
>
> Source: SCMP institutional stakeholder engagement, example catchment, example year.
>
> Evidence status: Stakeholder-reported; independent confirmation pending.
>
> Location: Not verified; no map point.

The illustration is **not** an actual stakeholder observation.

## Event metadata lineage

The date range and host city for each of the 20 indexed catchments were checked against its principal communiqué's introduction (Kano September 2024, Sokoto February 2025, Ilorin August 2025, Lokoja August 2025 and Gombe late August/early September 2025). These date windows describe engagement sessions, not dates on which claimed assets or conditions were observed.

The 88 candidate source paragraphs in the owner's private Stage 3C editorial pilot are held for source/context/privacy/rights review only and are deliberately excluded from `site/` and public GitHub history.

## Automated regression

- `python tools/test_engagement_source_contract.py`: confirms source metadata contains all 20 catchments but **zero** public cleared records, original claims, coordinates or private fields.
- `python tools/test_public_knowledge_index.py`: checks the dates, cities, topics, year distribution and public Knowledge UI.
- Existing `tools/validate_public_release.py`, the publication approval gate and the full Pages browser QA continue to run unchanged.
