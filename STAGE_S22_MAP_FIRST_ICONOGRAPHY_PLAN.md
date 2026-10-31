# S22 — Map-First Simplification & Iconographic Resources
Date: 31 October 2026
Based on deployed S21 (commit 27fae96).

## User requirements implemented
1. Barite/Baryte combined as one canonical display name, while raw source names remain unchanged.
2. Drop the per-resource dropdown. Each selected category displays all its mapped resource types.
3. A single **Layers** drawer controls themes, river detail, lakes, boundaries, labels, reference-dam overlay, and overview/LGA resource visibility.
4. Remove the large above-map symbol key and duplicate Start Here dock. The guide remains in main navigation.
5. Make the map the primary visual area at desktop and mobile sizes.
6. Replace abbreviated-letter circles with purpose-drawn vector pictograms for the named minerals, crops, ecology, pressures, water, and dam references. Each marker retains a distinct LGA-based reported occurrence identity.
7. Right profile only contains **Overview** and **Resources**. A collapsible States & LGAs panel is inside Overview; Sources and Technical tabs are removed from the visitor profile.
8. Keep original source statements and technical data in the repository and downloads, preserving provenance and QA. Compiled dam research references remain unverified.
9. No implied site coordinates: pictogram placement uses display-space displacement from an LGA representative anchor.
10. Source-only resources outside mapped catchments stay in the review queue.

## Acceptance and checks
- Exact canonicalization: both 'Barite' and 'Baryte' display as Barite in the map/list, retaining distinct supporting evidence records.
- An selected resource theme changes actual map markers, not just panel text.
- Barite has one icon per reported LGA rather than duplicative icons for alternate spellings.
- No specific-resource dropdown, no full-width top icon legend, one visible Layers control.
- Only Overview and Resources appear in selected-catchment panel; States/LGAs expandable within Overview.
- Major crops/minerals/hazards and unverified dam references use SVG-style icon silhouettes rather than type abbreviation disks.
- No external CDN, font, or intellectual property dependency. The pictograms are authored in site/resource-icons.js.
- Keep the original map, 20 catchments, FAO modeled rivers, all published source data, and zero confirmed physical dams intact.
- Full source/privacy and desktop/tablet/mobile browser regression passes before production merge; verify GitHub Pages deployment.

## Follow-up outside S22
Community-scale sites, independent dam verification, source record geocoding and exact locations remain distinct, evidence-driven stages.
