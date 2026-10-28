# Stage 3D-C — thematic evidence explorer (v1.11)

Date: 28 October 2026. Public release is conditional on a fully green main-branch GitHub Pages workflow.

## User experience

The Knowledge page retains its established catchment name/alias, source heading, meeting-year/host-city, provisional state/FCT, provisional LGA and sortable catchment filters. Four accessible **thematic lenses** now reveal distinct public evidence over the *currently filtered catchment set*. The new cross-border filter uses the previously published percentage outside Nigeria, interpreted using a stated >0.5% threshold.

1. **Modeled water network:** class counts for FAO AQUASTAT (2026) catchment-clipped reaches, grouped by the source hierarchy proxy of upstream drainage area: under 100 km²; 100 km² to below 1,000 km²; and 1,000 km² or greater. Selection totals and per-catchment class breakdowns come from the existing public `detailed_river_manifest.json` only. The 20-catchment reference totals are 33,169, 11,433 and 7,410, summing to 52,012 geometries. These class intervals do **not** represent river width, discharge, confirmed perennial water, river order or navigability. Where clipped reaches overlap in different catchments, overall display totals are not necessarily unique physical rivers.
2. **Geographic footprint:** already public mapped catchment areas, approximate 2022 GRID3/geoBoundaries state/FCT polygon intersections and indicative cross-border extent. The selected geographic footprints may overlap; summed area is not an official Nigerian basin or national land area. Nine of the 20 catchments have more than 0.5% area beyond the Nigeria administrative overlay, but geographic uncertainty remains.
3. **Institutional engagement:** published meeting event/year metadata and the existing four communiqué section headings. The indicated meeting host city does not locate facilities, communities, resource observations or source claims. Source presence is not endorsement by all participants or proof of each statement.
4. **Infrastructure and interventions:** an explicit, safe release-readiness state. It shows **zero currently authorized individual infrastructure records and zero validated facility points published from stakeholder sources**. This is emphatically **not** a finding that no physical assets or interventions exist.

All four lenses rely on the existing public data and share the same filtering, selection and map navigation. Switching lenses does not alter the underlying data source, modify geometry, reveal private source statements or trigger new hidden network requests.

## CSV and safety

The existing filtered public CSV now includes the three upstream-drainage class counts, maintaining source statuses and data caveats. The export continues to use only the existing catchment registry, approved administrative overlap and FAO manifest, and publicly indexed workshop event metadata. No private stakeholder claims, inventory names, exact asset coordinates, restricted links, reviewer IDs, source quotations, signed material or confidential data are included.

## Automated acceptance

`tools/test_thematic_lenses.py` validates the complete 20-catchment class counts, total 52,012, nine cross-border catchments, source metadata gating and absence of private field names in public HTML. Browser QA verifies dynamic thematic lens behavior, model count presentation, filter-dependent export, deliberate zero-record asset notice and reset behavior across desktop/tablet. Existing map, gesture, keyboard and public-release CI remain mandatory.

## Next stage boundary

A genuine searchable catalogue of individual water infrastructure, mineral, natural-resource, environmental challenge and intervention claims requires records with source context, faithful summaries, item-specific rights/privacy review, confirmed attribution, and any needed independent geospatial checks. All currently unapproved records remain HOLD.
