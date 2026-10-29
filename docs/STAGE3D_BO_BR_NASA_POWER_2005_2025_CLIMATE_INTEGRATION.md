# Basin Nexus NG — Stages 3D-BO–BR: substantial climate data integration

**29 October 2026.** This leap favors genuine public data integration and accessible profiles over additional catchment topology screening.

## Added source datasets and scale

NASA POWER Prediction Of Worldwide Energy Resources **monthly/annual point API**, Agroclimatology community (AG), years **2005–2025 inclusive**. Complete modeled climate data are loaded from **20 original NASA POWER JSON responses**, one at each catchment's registered display-label coordinate. The NASA-source JSONs are preserved in `research/nasa_power_monthly_2005_2025/SCMP-C01.json` through `SCMP-C20.json` with each SHA-256 in the public climate records.

- **420 catchment-point annual records**: 21 annual estimates × 20 points.
- **5,040 catchment-point original monthly pairs of climate variables**: 21 years × 12 months × 20 points, for both precipitation and temperature. Data remains in original NASA source files; don't imply 5,040 independent weather stations.
- **240 averaged monthly seasonality rows** (12 × 20 catchments).
- **20 source-attributed unified catchment indicator rows**, combining existing SCMP registered areas/map-label points, provisional 2022 GRID3 state and LGA polygon intersection counts, unchanged FAO AQUASTAT 2026 modeled clipped reach counts, and new NASA modeled climate metrics.

NASA POWER model source uses `PRECTOTCORR` **mm/day** and `T2M` **°C**. Each monthly precipitation amount is estimated as that month's daily mean modeled rate multiplied by its actual calendar day count. Annual precipitation is the sum of its 12 monthly approximations. Annual temperature is the calendar-day-weighted mean of the 12 monthly modeled temperatures. Historical precipitation and temperature means are arithmetic means of the 21 annual summaries. Wettest/driest historical month uses the 21-year climatology of estimated monthly precipitation.

NASA POWER metadata identifies MERRA-2 meteorology for the retained API replies, not original rain gauges. Do not call the estimates CHIRPS or high-resolution catchment rainfall, and do not interpret the 2025 model output alone as observed drought or flood conditions.

## Compatible stages

**BO — Original NASA point source integration**: automate 20 bounded monthly NASA POWER API queries (max three concurrent), validating exact dates, point location, variable names and native units, and preserve original responses and hashes. New data is sourced from NASA, not from model guesses.

**BP — Historical point climate profiles**: annual 2005–2025 modeled precipitation/temperature in a point-by-point 20-catchment comparison, 12-month rainfall seasonality, historical averages, 2025 source summary. The new **Climate** profile shortcut presents historical context and opens detailed records.

**BQ — Unified catchment indicator register**: one downloadable 20-row CSV and JSON with stable SCMP catchment IDs, original area and map-label position, provisional GRID3 administrative overlap counts, FAO 2026 clipped modeled reach count, and point climate. Unified values retain their source-specific precision and interpretation rather than being blended into a single unvalidated impact index.

**BR — Minimal source reproducibility and release**: a single Python source validator and existing browser smoke tests check the 20 point series/21 years/12 monthly climatology, source schema, search, and corrupted unified register rejection. The existing Pages publication gate recomputes all three public files from the **retained NASA original responses**, without downloading from NASA during deployments. Existing dam/privacy and river-source safeguards remain unchanged.

## New public files

`site/data/nasa_power_20_catchment_point_climate_2005_2025.json` — full 20 × 21 annual and 20 × 12 monthly climatology records, original request URLs and source SHA-256.

`site/data/integrated_catchment_indicator_register.json` — source-typed 20-catchment metadata and indicators.

`site/data/integrated_catchment_indicator_register.csv` — clean, ArcGIS/QGIS/Excel-friendly 20-row indicators, one row per SCMP catchment.

`site/climate.js` — standalone browser climate table, seasonal display, row search and profile-card adapter.

## Non-negotiable limits

**Climate is sampled at map-label coordinates, not the area-mean of the catchment**. It is a model-based gridded point estimate rather than a gauged station measurement. For hydrological rainfall gradients and RUSLE/scenario evaluation, a separate approved CHIRPS, IMERG or similar raster-based **spatial zonal analysis** will be required. No unsanctioned inferred drought impacts, flow rates, water balance or field-verified wetland/dam findings.

The 20 original catchments and 52,012 clipped FAO 2026 river records were not changed. The research dam inventory remains 189 publisher-compiled intersections, 186 optional **unverified** map references, three held disputed labels, zero independently confirmed physical facilities and zero released private stakeholder evidence records.

## Source links

- NASA POWER Monthly and Annual API: https://power.larc.nasa.gov/docs/services/api/temporal/monthly/
- NASA POWER meteorology origins and latency: https://power.larc.nasa.gov/docs/methodology/data/sources/
- FAO AQUASTAT 2026 modeled river network: https://data.fao.org/catalog/dataset/e22667af-3977-4e9f-b58b-67fb91b0fa87 (CC BY 4.0)

## Next project-completion focus

Use the integrated modelled source point-climate and existing mapped river/admin coverage to build more usable catchment profiles and source-attributed downloadable planning indicators. For rigorous whole-catchment rainfall mapping, next add **real raster-derived zonal precipitation** and then LULC/erosion if sourced and reproducible. Avoid repeating the completed source topology and model endpoint investigations or manufacturing unapproved infrastructure records.
