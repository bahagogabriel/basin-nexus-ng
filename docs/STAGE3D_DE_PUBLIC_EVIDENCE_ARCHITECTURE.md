# Basin Nexus NG — Stages 3D-D and 3D-E: publishable evidence architecture

Date: 28 October 2026. Planned version: v1.12, conditional on green release workflows.

## Stage 3D-D: Public evidence catalogue

The atlas now includes a distinct, versioned `PublicEvidenceCollection` file at `site/data/public_evidence_catalogue.json`. The initial published collection is **deliberately empty**, because no individual SCMP stakeholder record has been approved for release. It is a separate data class from the 20 source-event metadata records; the latter remain strictly metadata-only.

The Knowledge page includes a real catalogue interface with full-text search, seven thematic classes, evidence verification-level filtering and catchment scope inherited from the existing geography/source filters. Once actual records have been approved and promoted through the release gate, the page can show the attributed statement, source locator, verification status, approved public source link and explicitly validated coordinates (if any). Its map action navigates only to the associated catchment; it does **not** draw a facility point or imply a surveyed asset. All user-controlled and record-derived text is HTML escaped; public source links must use reviewed HTTPS.

The empty state explains that withheld records do not imply absence of infrastructure, interventions or reported issues. A missing, invalid or unavailable public collection causes a distinct **catalogue unavailable** message without breaking the main catchment atlas. The user interface never reads any private Drive records.

## Stage 3D-E: Source-specific publication receipt and integrity gate

The existing Python `evidence_publication_gate.py` has stronger protections against private Google Docs/Drive URLs, email addresses, internal source markers, unknown collection fields and invalid records, while retaining its compatibility with existing synthetic validators.

A separate offline `tools/stage3d_e_release_pipeline.py` checks a proposed public-only collection against a **separate human-authored private review receipt**. Each receipt must match an exact SHA-256 canonical JSON fingerprint of the public record, its authorization ID, source-rights clearance, privacy clearance, editorial decision, named reviewer, valid nonfuture date, and independently approved spatial review when public coordinates are included. The tool accepts private input files and outputs only in a separate owner-controlled location outside the public GitHub repository. It produces a candidate export, never commits or deploys anything, and never invents approval.

The review receipt is procedural evidence, **not** a cryptographic signature or independently authenticated legal permission. Publication requires authentic institutional release rights and a deliberate code review of the exact promoted file. The automated checker cannot obtain these approvals on its own. The pre-deployment public catalogue contract deliberately rejects all nonempty catalogues in v1.12, so no future reviewer can bypass a new publication-specific pull request by changing a record alone.

## QA

- Public `site/` allowlist explicitly contains only the single new, versioned empty catalogue.
- Public release gate checks the file, all other existing boundaries, modelled reach checksums, and the confidentiality exclusions.
- Separate static tests guard zero public records and seven categories.
- Adversarial synthetic unit tests cover private-source leakage, unverified location, malformed schema, altered record after approval, missing human source-rights/privacy decisions and nonmatching review receipts.
- Browser QA checks initial zero-record messaging, responsive filtering and error isolation; separate synthetic in-memory network fixtures exercise a fictional approved record, search, verified-vs-reported displays and map navigation. These fixtures **never** enter the actual public site or catalogue.
- Production CI reruns the entire geographical map and accessibility/gesture regression suite before deploying the unchanged public URL.

## Future genuine release

Real editorial work remains in owner-restricted Drive. An institutional approver must decide which source-based statements can be redistributed, with source-specific rights/privacy and scientific context checks. A new reviewed PR must change both the public data and the explicit zero-release contract. No synthetic authorization IDs from this repository are valid proof of actual permission.
