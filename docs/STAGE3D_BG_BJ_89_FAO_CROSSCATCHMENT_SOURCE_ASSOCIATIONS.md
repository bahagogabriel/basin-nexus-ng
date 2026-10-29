# Basin Nexus NG — Stages 3D-BG–BJ: 89 cross-catchment source-reach geometry audit

**29 October 2026.** Combined source-count reconciliation, catchment overlap screening, public transparent research exploration, and independent browser/release QA. Extends the verified Stage 3D-BC–BF source original-versus-clipped model resolution.

## Scope and original source

- 20 original SCMP catchments; 52,012 clipped FAO AQUASTAT 2026 river features from 51,906 unique publisher modeled `HYRIV_ID` values. Original publisher `NEXT_DOWN` source IDs, no inferred stream names or revised geometry.
- The source SHA-256-backed `fao_downstream_index.json` yields **89 source-reach clips** where `NEXT_DOWN` exists elsewhere among the 20 catchment indices but not in the originating catchment index.
- These 89 origination records contribute **92 destination study-area memberships**, because **three records** have modeled NEXT_DOWN targets that occur in two other catchment clips. This is an association count, not 92 independently confirmed interbasin flows.
- The 92 directed destination memberships aggregate to **33 original modeled source catchment-pair categories**.
- The geographically *simplified study polygons* are **overlapping for 91 of those 92 memberships** and **touch/intersect with no positive-area overlap for one**. **None** is between study polygons classed as spatially separate. This overlap finding is a critical reason **not** to interpret 33 pairs as 33 upstream-to-downstream watershed transfers.

## Compatible stages

**BG — Publisher-source graph integrity.** Regenerate `fao_downstream_summary.json` and `fao_downstream_index.json`, enforce 20 catchment identity masks, required 89 source-clip links and 33 source pair types. Treat an original reach appearing in two or more clips as the **same publisher `HYRIV_ID`**, not two named rivers.

**BH — Catchment polygon and clipped model reach screening.** With Shapely 2.1.2 and only the original SHA-256-pinned 20 catchment and 20 river files, compare all 89 originating clipped lines to the target reach fragments in *each* destination study catchment. Classify whether catchment polygons overlap, touch/intersect, or are separate, and measure the *nearest available clipped line-to-line separation* in lon/lat plane with a spherical approximation. This is a **screening statistic** and cannot independently establish a physical confluence, a geodesically optimal route, travel time or transfer direction.

**BI — New searchable Data explorer.** The public atlas Data page provides all 89 source-association records in a searchable review table with catchment filter, source-ID search, closest clipped modeled gap bands and map drill-down. Show destination multiplicity and disclose overlap caveats. Distribute a source-only 89-record CSV and JSON; source model provenance remains FAO AQUASTAT 2026 CC BY 4.0, HydroRIVERS-derived.

**BJ — Source and browser release QA.** Unit tests check synthetic polygon intersection, clipped line separation, all 89 exact source IDs, 92 target memberships, per-catchment counts, 33 directed pair totals, and explicit non-hydraulic interpretation. Independent Chromium tests check 89 rows, filters, map drill-down, no misleading transfer claims and rejection of intentionally corrupt source data. The strict public Pages allowlist contains **only** the two newly approved public-derived CSV and JSON files, with a deterministic regeneration test that recomputes and matches both before deploying.

## Why source-reach directions do not equal whole-catchment directions

These are purpose-specific *study areas*, not necessarily a set of disjoint, properly nested hydrologic basin outlets. A source reach may belong to multiple clipped study areas and the source's `NEXT_DOWN` label only points to another modeled reach, possibly also inside overlapping polygons. Neither the 89 clip associations nor the 33 pair categories can define unambiguous catchment-outlet directions without independent outlet and nonoverlap/partition validation. Reciprocal catchment pair associations can occur without any impossible river flow.

The earlier three large >500m *clipped endpoint discrepancies* were independently reconciled to coincident **original FAO modeled endpoints** (0m) in Stage BC–BF; this is unrelated to independent hydraulic field confirmation for all 89 modeled source associations. The new nearest-line gap measurements must not be called survey positional errors or channel discontinuities.

## Protected release baseline

- All 20 published original SCMP catchment polygon files and FAO 52,012 display river features remain unchanged.
- Original 189 published compilation research dam intersections, 186 opt-in unverified research map markers and 3 disputed identities withheld unchanged. **Zero independent physical dam confirmations**.
- **Zero** individually approved public stakeholder evidence records.
- No private restricted SCMP files in model-source audit, no application approval mechanisms altered, and no new invented model drainage class or source river name.
- FAO modeled public river dataset: https://data.fao.org/catalog/dataset/e22667af-3977-4e9f-b58b-67fb91b0fa87 (**CC BY 4.0**).

## Next investigation checkpoint

The 89-source universe has now been quantified without uncontrolled publisher WFS calls. Genuine hydrologic direction analysis should first establish valid nonoverlapping catchment areas and original outlet/control point definitions and confirm whether reciprocal `NEXT_DOWN` study-pair associations are solely due to overlapping clip boundaries. Until then, use the 89-row source reviewer rather than publishing a directed water-transfer or catchment flow map. Field/engineering dam confirmation is a separate frozen evidence gate.
