# Stage 3B — Private stakeholder evidence review

This repository contains **review tooling only**. Never put institutional submissions, names, attendance, signatures, contact details, private Drive IDs, raw text, location estimates or claim-register extracts in Git history, Actions artifacts or the public `site/` folder.

## Review phases

1. Enumerate every source and its versions in restricted Drive storage; separate signed copies, attendance, archives and transient files. Keep the canonical 20 catchment IDs from `site/data/registry.json`.
2. Extract each claim with an internal ID, exact source ID and section/table-row locator, unchanged original wording, theme, record type, reported administrative geography, date/status and units. A stated location is not an independently validated coordinate.
3. Reconcile by source, LGA/community and date—not name alone. Preserve contradictory numbers, source units and intervention states. Leave unknown statuses unknown.
4. Audit the private JSON register outside the checkout:

```sh
python tools/stage3b_private_qa.py /secure/claims.json --out /secure/new-qa-report.json
python -m unittest discover -s tools -p 'test_stage3b_private_qa.py' -v
```

The generated QA file contains counts and diagnostic codes only; it is **not** public metadata approval. An output report never certifies truth or legal rights. The utility refuses private inputs and reports located within the public repository and refuses to overwrite existing reports.

5. Human reviewers must separately establish source rights, privacy clearance, scientific accuracy, record-by-record release authorizations and location validation. The existing `tools/evidence_publication_gate.py` and `tools/validate_public_release.py` remain mandatory; passing automated checks alone cannot authorize publication.

**Stage 3B remains a private working stage.** The public Knowledge index remains metadata-only. No unapproved claim, source document or asset point can be published.
