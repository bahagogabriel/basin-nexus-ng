# Basin Nexus NG — Stages 3D-AE–AH: Surgical evidence-decision desk

**29 October 2026. Source-only review. Zero independently confirmed dams.**

Previous authoritative release: Stage AA–AD main SHA dfbec791a11f334461f77d2dccbc6ea16bb5bff2, successful production, source and browser QA. Original 20 catchments, 189 source dam references, 186 opt-in unverified source points, three withheld disputed identities, zero independently confirmed dam facilities and zero approved individual stakeholder statements are all preserved.

## Four compatible sub-stages

**AE — Prioritize evidence bottlenecks, not repetitive research.** 
1. WA26-003: highest-priority official Gusau Barrage lead. Seek dated official engineering as-built/crest survey and distinguish it from the separate August 2020 abstraction-intake coordinate. The reported 84.9 m and 246.6 m source separations are not positional accuracy or identity proofs.
2. WA26-184/185/186: seek high-resolution dated engineering/field/EO observations of actual constructed walls and independently measured positions/uncertainty. OSM-line proximity 1.8/1.8/5.4 m does not confirm independent survey or physical construction. They remain unnamed reference points.
3. WA26-083: resolve repeated Gusau label with distinct official records, not inherited names or automatic merging with WA26-003.

**AF — Audit-bound human evidence routing form.** The same 5 cases are SHA-256 bound to the exact prior AA–AD evidence file. A 12-field human-receipt template per case remains blank. This in-repository routing form can hold only HOLD or NEEDS_INDEPENDENT_REVIEW and can never approve/publicize a dam. Filled confidential evidence must be handled through a separately authorized secure human-review workflow; do not upload it to the GitHub repository or public website.

**AG — Narrow next-action queue.** Compact per-case research blocker and source-specific next request, preserving provenance and licensing.

**AH — Fail-closed release regression gates.** Explicitly reject modified original source checksum, fake confirmation, mislabelled Gusau government water-abstraction vs dam inventory, source coordinates presented as surveyed wall locations, Sentinel SCL water classes claimed as construction evidence, and approval or reviewer evidence injected into a source-only routing form.

## Automation

Script: tools/build_stage3d_ae_ah_review_desk.py
Tests: tools/test_stage3d_ae_ah_review_desk.py

On PR: synthetic unit and browser tests only. On main: existing publisher/OSM/EO verified source chain runs first; the script consumes review/stage3d_aa_ad_evidence_REVIEW_ONLY/stage3d_aa_ad_research_receipts_NOT_CONFIRMED.json and archives a separate non-public GitHub Actions review artifact. It writes no file to site/data and has no external network access of its own.

Outputs: STAGE3D_AE_AH_REVIEW_CASES_NOT_CONFIRMED.json, STAGE3D_AF_BLANK_ROUTING_FORM.json, and STAGE3D_AG_REVIEW_QUEUE.md.

**Next genuinely necessary checkpoint:** obtain dated independently corroborated, appropriately licensed physical-wall/engineering/field evidence, a measured wall location and uncertainty, source-family independence review and accountable rights/publication approval. No further automated source-only work can replace those facts. A separate explicitly reviewed facility-release pull request remains mandatory; missing published names stay Unnamed reference points, not verified Unnamed dams.
