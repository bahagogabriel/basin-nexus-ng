# Basin Nexus NG — Stages 3D-AI–AL: Offline evidence intake, source-family checks and unsent requests

**29 October 2026.** This is a focused completion of the infrastructure-evidence workflow, not a new dam discovery campaign. Baseline: GitHub main `74f19e87e87c6337e29f686c3a17edb09a70d742` with 20 SCMP catchments, 189 CC BY 4.0 compiled source references, 186 opt-in unverified research markers, three disputed labels withheld, and **zero independently confirmed dam facilities** or released individual stakeholder statements.

## Four compatible development stages

**AI — Offline private evidence input.** `tools/stage3d_ai_ak_private_evidence_intake.py` supports two operations: create a *blank* review JSON from an immutable source-desk fingerprint, and evaluate a user-edited private JSON. It requires that all filled evidence and any completeness reports remain **outside the repository**. It never makes an HTTP call, opens the actual referenced documents, uploads data, or transmits any user/reviewer information. New file creation is exclusive with Unix 0600 permissions. The raw private JSON may contain a reviewer name, institutional affiliation or confidential evidence locators; do **not** commit it, attach it to public issues, or upload it to GitHub Actions.

**AJ — Structural source-family and position consistency checks.** The offline checker requires explicit source-ID and source-family links for physical existence and wall-position evidence, typed position methods drawn from the existing hardened confirmed-dam policy, dates, coordinate ranges, GNSS/authority/independently reviewed EO method and uncertainty. The checker checks *declarations*, not historical truth or independence of the source families. A claimed government inventory point, separate water abstraction point, OSM way and 2019/2026 Sentinel-2 SCL pixels cannot silently become a surveyed wall receipt. A form that looks complete is only **DOCUMENTATION COMPLETE FOR SECOND HUMAN REVIEW — NOT VERIFIED**, never independently confirmed.

**AK — Redacted private-review disposition and non-release gate.** The result contains only the reference ID, source-desk SHA256, count of submitted documents and source families, categorical missing-evidence codes, and hard-coded flags that independently verified facility, independently verified wall, release authorization and public site updates are **false**. It contains no evidence-file paths, names, reviewer identity, comments, or coordinates. Attempts to forge approval/release authorization, change source-desk digest, add extra private fields, or write a private report into the public repo fail. A second accountable reviewer must *actually inspect* all original records and survey/engineering material, establish true independence and scientific status, and separately clear rights/privacy before any future facility-specific release PR. The existing confirmed site release gate remains locked to zero public sites.

**AL — Narrow source-bound records requests.** `tools/build_stage3d_al_evidence_request_kit.py` generates **five drafts, none sent**: a specific Gusau Barrage as-built/survey/identity-reconciliation request for WA26-003; a separate identity request for WA26-083; and three unnamed source-reference wall/existence requests (WA26-184, WA26-185 and WA26-186). Every draft explicitly marks original coordinates as compiled *research points, not surveyed wall coordinates*. It also produces five empty case-bound offline intake JSON templates and a short how-to. The main GitHub Actions artifact contains only these **blank/unsubmitted** materials and no actual private evidence.

## Operation with a downloaded public-source review desk

Use the source-only file `STAGE3D_AE_AH_REVIEW_CASES_NOT_CONFIRMED.json` from the verified prior GitHub Actions review artifact. In a private folder **outside the repository**, with local permissions and access controls appropriate for sensitive records:

```bash
python tools/stage3d_ai_ak_private_evidence_intake.py \
  --desk /path/to/STAGE3D_AE_AH_REVIEW_CASES_NOT_CONFIRMED.json \
  --case WA26-003 --init --out /private/path/WA26-003.json

# Fill the private form only after obtaining genuine evidence.
python tools/stage3d_ai_ak_private_evidence_intake.py \
  --desk /path/to/STAGE3D_AE_AH_REVIEW_CASES_NOT_CONFIRMED.json \
  --case WA26-003 --review-input /private/path/WA26-003.json \
  --out /private/path/WA26-003-REDACTED-status.json
```

On Windows, replace `/private/path` with a protected directory outside the checked-out repository. Windows filesystem permissions are governed by the operating system; Unix 0600 mode alone does not configure Windows ACLs.

No documents or review approvals have been received at this stage. The draft letters are **not sent** and are not official engineering records. The correct current result remains **zero confirmed dams, zero authorized publication changes**. No map/data layer or restricted SCMP statement is changed.

## QA and release requirements

PR and independent browser Actions execute only synthetic records and tests; the on-main source-intake job regenerates the existing AA–AH source evidence first and then generates the blank request/template artifact. The offline filled-record processing **never runs in GitHub CI**. Source and site safeguards continue to be tested. The next meaningful checkpoint is a real independent government engineering/as-built survey or licensed field/higher-resolution EO evidence for the five identified cases, coupled with accountable human review. No more source compilation is needed to begin those evidence requests.
