# Basin Nexus NG — Stage 3D-Z: local-clear optical scene optimization

**29 October 2026. Review-only, no dam confirmation.**

## Why this stage was necessary

The complete 3D-X/Y live GitHub main-branch run (initial release SHA `73356c3bd86ae2b22f40c4806b96e4b31fdb8459`) successfully sampled **10/10** Sentinel-2 RGB+SCL chips for five source-reference IDs, with an image reviewer board. But the **central 25 × 25 SCL clear fractions** were:

| Research reference | 2019 | First selected 2026 |
|---|---:|---:|
| WA26-003 | 1.0000 | 1.0000 |
| WA26-083 | 0.9856 | 0.9952 |
| WA26-184 | 1.0000 | 0.0560 |
| WA26-185 | 1.0000 | 0.1952 |
| WA26-186 | 1.0000 | 0.3312 |

These are **valid center pixels classified clear by SCL classes 4/5/6/7**, not percentages of a verified dam structure. The original image selector stopped at the first *downloadable* scene, even when that scene had poor site-specific visibility.

## Stage 3D-Z reproducible correction

The Stage X/Y extraction now considers up to **three** prior Stage W metadata-shortlisted scenes for each source point/epoch. Each candidate is sampled from actual COG RGB and SCL pixels on the same aligned review window. It scores candidates first by **local center SCL-clear fraction**, then center valid pixel count, then overall valid coverage, and only lastly the STAC **tile-level** cloud percentage. When a sampled candidate has center-clear ≥0.85 **and** ≥500 valid center pixels (out of 625), sampling stops; otherwise it considers the remaining shortlisted scenes and keeps the highest-ranked valid observation.

The reviewer JSON records all attempted scene IDs, number of usable sampled options, the original scene metadata, the chosen scene and whether the local clarity target was achieved. It never invents cloud-free coverage or automatically constructs a multi-date radiometric mosaic. If all shortlisted images are unavailable, the status remains **PIXELS_UNAVAILABLE_NOT_NO_IMAGERY**. If the local clarity target cannot be met, the selected image is still described truthfully as a *cloud-obscured review candidate*, not an authoritative scene.

The original publisher source SHA/MD5, the five research IDs and both original/OSM source licences remain guarded. All confirmed-dam, physical-position and human-approval flags remain false or null. No public site assets or map layers are altered.

## Review guidance

Review 2019 and 2026 images **at their exact acquisition dates**. Seasonal turbidity, optical differences, plant cover, shadows, clouds, viewing geometry and data processing may explain color differences. An SCL water classification is not a dam-wall detection. It is not sound to compare raw surface reflectance between 2019 and 2026 without radiometric baseline harmonization. No automated temporal change, construction-date estimate, dam count or independent positional-accuracy estimate is generated.

All contact sheets and audit records remain under GitHub Actions **review-only artifacts**, which have their own retention period. The next distinct evidence milestone is independent, qualified interpretation of the observed pixels combined with engineering/site records and defensible coordinates/uncertainty; a separate reviewed release PR remains mandatory for adding any confirmed named or unnamed dam.
