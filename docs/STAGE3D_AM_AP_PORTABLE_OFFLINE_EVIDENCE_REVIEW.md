# Basin Nexus NG — Stages 3D-AM–AP: standalone offline engineering evidence reviewer kit

**29 October 2026.** This stage packages **existing, source-safe research context**, not new site discoveries. The previous Stage 3D-AI–AL publication state remains authoritative: 20 catchments, 189 original compiled references, 186 unverified opt-in preview markers, 3 withheld identities, **0 independently confirmed dams** and **0 publicly approved individual stakeholder statements**.

## Combined natural stages

**AM — Portable delivery:** Build a standalone ZIP from the verified Stage AE–AH five-case decision desk generated on *main*. The ZIP contains the actual source-bound desk, existing five original-label research reference IDs, five unsent records requests, five completely blank intake JSON templates, the minimal Python-standard-library reviewer scripts and instructions. A reviewer can extract it and run without downloading a GitHub repository, configuring ArcGIS, requesting credentials or installing GDAL.

**AN — Redacted five-case offline batch QA:** Run the included `tools/stage3d_an_offline_batch_audit.py` on a private directory, with optional case forms named `WA26-003.json`, `WA26-083.json`, `WA26-184.json`, `WA26-185.json`, `WA26-186.json`. Only these five paths are ever read. Missing forms are marked `NOT_SUBMITTED`; malformed or symlinked forms are `INVALID_PRIVATE_FORM`. Batch results report source-ID-only categories and counts. Names, URLs, private documentation, coordinates and free text are never copied to the batch report. A positive documentation-completeness result still means **ready for second *human* review only**, not independent existence, location verification or release authorization.

**AO — Reproducible original-package integrity:** The distribution includes `FILE_MANIFEST.json`, SHA-256 digests of each original script, research context, blank intake form and unsent draft. Run `python tools/stage3d_ao_verify_portable_kit.py` from the extracted root before copying a blank form elsewhere. It detects modified distributed files. This is a file-integrity check, **not a cryptographic authenticity signature or proof the publisher's physical infrastructure records are correct**.

**AP — Detached, automated usability tests:** Ten synthetic tests create the complete ZIP, extract it in a temporary directory, verify its manifest, run the *actual* supplied scripts outside GitHub, audit one blank and four missing forms, reject a modified file and attempted source-review drift, detect symlinks and validate that no private filenames or identities enter status output. PR CI runs no external dams research, files or private evidence. Main-only source CI first regenerates the source-only previous desk and then archives this standalone kit. The test and output bundle is **never uploaded into GitHub Pages `site/`**.

## How to use the kit

Extract the main-source workflow artifact ZIP, then extract the contained `stage3d_am_ap_offline_reviewer_kit_REVIEW_ONLY.zip`, open its `BasinNexusNG_OfflineReviewer_2026-10-29/` folder and read `README_FIRST.md`. Python 3.11 or later, without pip dependencies, is sufficient. On Windows use a private folder with appropriate Windows ACLs: `0600` Unix permissions do not substitute for Windows protection.

Do not edit original bundled files. Copy or initialize a blank form to a protected **separate** folder before recording field evidence. The offline CLI will never access the internet, approve a named or unnamed dam, authenticate engineering sources, or create publication rights. Any site candidate, even Gusau Barrage with documentary context, needs its exact built wall matched to an independently authenticated dated inspection or as-built record, source-family independence, defensible positional uncertainty and accountable separate editorial/release authorization.

### Next evidence checkpoint

No further compilation of satellite metadata, OSM geometry or empty approval forms is necessary. The primary next input is an authorized **Gusau Barrage as-built/barrier survey** matching WA26-003, followed by equivalent independent wall and field evidence for WA26-184/185/186 and an identity check for WA26-083. A separate secure human review, then a distinct, approved facility-release PR under existing site gates, is required. The source-unnamed records remain **Unnamed reference points**, not confirmed unnamed dams.
