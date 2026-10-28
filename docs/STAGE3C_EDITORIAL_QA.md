# Stage 3C-B — Private editorial readiness QA and safe public source discovery

Date: 28 October 2026. Public release: v1.8.1 metadata-only interface enhancement.

## Current evidence boundary
The existing 20-catchment SCMP engagement index is public metadata, not a source-authorized stakeholder claim catalogue. The private 88-candidate Stage 3C pilot remains **HOLD**. No institutional release permission, privately sourced quotation, verified facility location or individual content has been granted or added to the public site.

## Public changes
The Knowledge index now allows combinations of catchment/alias search, four source headings, meeting year and **host city**, plus one-click reset. Host cities are workshop venues and must never be interpreted as locations of catchments or physical facilities. The underlying catchment boundaries, provisional administrative layers, modeled river networks and source index structure are unchanged.

## Private Stage 3C review utility
The script `tools/stage3c_private_editorial_qa.py` accepts either a JSON array of candidate objects or a plain-text export of the owner's private Google Doc containing one JSON record per line. Input and output **must reside outside the public GitHub repository** and are refused otherwise. Example:

```sh
python tools/stage3c_private_editorial_qa.py /secure/PRIVATE_pilot.txt --out /secure/PRIVATE_editorial_qa.json
python -m unittest discover -s tools -p 'test_stage3c_private_editorial_qa.py' -v
```

Its output contains only totals, controlled thematic names, workshop-city names and QA-code counts: missing source anchors, duplicate identifiers, incomplete/context-dependent fragments, missing editorial paraphrases, pending reviewer decisions, source rights/privacy hold, unvalidated coordinates and any improper release flags. It does not write original statements, IDs, names, coordinates, internal links or reviewer narratives. All records are considered unapproved; zero public authorizations can arise from running the utility.

Results are **screening flags, not proof of completeness or scientific/rights validation**. The expression-based fragment check is intentionally conservative and may miss subtle missing context or raise false positives. Human editorial, source-rights and privacy reviews remain mandatory before any individual claim is released. Do not auto-complete or invent permission values.

## Protected review sequence
1. Read complete original paragraphs/tables and retain exact private source anchors; reviewer should fix candidate sections that only contain headings or incomplete list introductions.
2. Reconcile the eight unresolved dam capacity groups and any version conflicts without choosing arbitrary values.
3. Draft faithful paraphrases and attribute as *reported in the SCMP institutional stakeholder engagement*, without treating participation as universal institutional endorsement.
4. Evaluate source permissions, sensitive details, evidence quality and location method; keep unverified coordinates null.
5. Only an auditable, genuinely authorized batch may be considered by the existing evidence publication gate; separate user/institution approval cannot be synthesized by scripts.

CI exercises synthetic adversarial tests and public browser QA. CI never reads the private pilot.
