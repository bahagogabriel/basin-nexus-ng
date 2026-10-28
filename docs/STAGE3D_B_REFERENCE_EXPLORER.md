# Basin Nexus NG — Stage 3D-B public geographic and water-reference explorer

Date: 28 October 2026
Release designation: v1.10 (requires passing pre-merge and main-branch GitHub Pages CI).

## Scope delivered

The metadata-only Knowledge index, previously searchable by SCMP engagement year, host city, source section theme and state overlap, now includes an LGA selector derived entirely from the accepted public administrative crosswalk. It offers 495 distinct provisional LGA geometries across 20 catchments; intersecting areas occur in 754 catchment–LGA pairings. Selecting a state constrains the LGA menu. Changing state resets an incompatible LGA. Reset restores name sorting and clears every filter.

Cards show existing catchment polygon area, the number of catchment-clipped reaches from the public FAO AQUASTAT (2026) modeled river reference manifest, and the number of 2022 GRID3/geoBoundaries LGA polygon intersections. A disclosure shows data limitations, cross-border caution and unpublished stakeholder evidence status. Sort by name, mapped area or count of FAO modelled river reaches. Download a CSV of the **currently filtered** public geographic/meeting-metadata summary.

## Interpretive boundaries

- **Catchment area:** user-provided project polygons, approximate, not statutory boundaries.
- **State/LGA intersections:** 2022 GRID3/geoBoundaries geographic overlaps only. An LGA may intersect more than one catchment; these overlaps do **not** establish formal catchment jurisdiction, state participation in a workshop or locations of individual source claims.
- **Water:** FAO AQUASTAT 2026 modelled reaches, counted after catchment clipping. Counts are not a count of independently surveyed rivers and do **not** estimate discharge, accessibility, water quality, flood occurrence, river length or hydraulic capacity.
- **Engagement source:** only the original institutionally sourced workshop host city, date range and the four section heading labels. No signed documents, private material, stakeholder claim text, verified facilities or unpublished assets are transferred or exposed.

The downloaded CSV has a fixed public allowlist: catchment identifier, name, area, modeled reach count, approximate state/LGA intersection counts, indicative outside-Nigeria fraction, source-event host city/date, and explicit metadata-only/provisional statuses. No user-entered query or privately sourced input is exported. CSV values are quoted and leading spreadsheet formula characters are escaped.

## Validation

`tools/test_knowledge_reference_explorer.py` confirms 20 IDs across the approved public registry/crosswalk/FAO manifest/source index, 102 provisional state intersections, 754 LGA associations involving 495 distinct IDs, and 52,012 catchment-clipped modeled reaches; it enforces zero source content or private identifiers in the public UI and the static metadata-only export routine.

The Playwright desktop and tablet suite checks LGA cascading filters (including Jos South intersecting four catchments), geographic caveats, no-results disablement, CSV export row count and absence of private column names, and ordered results for area and modeled river reaches. Existing map interactions, touch/gesture stability and release gates remain mandatory.

## Still not released

Individual SCMP stakeholder claims, inferred exact facility points, photos or institutionally controlled extracts remain HOLD pending source-rights, privacy, original-context review and separate spatial validation. Stage 3D-B is **not** completion of a full verified thematic stakeholder catalogue.
