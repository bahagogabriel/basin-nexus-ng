#!/usr/bin/env python3
"""Stage 3D-T: review-only triage of the pinned, public-source dam references.

Input MUST be the existing candidate-builder artifact, never stakeholder data.
Output is a review-only record queue, not a validated dam inventory. This code
never identifies a real-world facility, consolidates records or approves release.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
import unicodedata
from pyproj import Geod

PUBLISHER_CSV_MD5 = "046b106da1e3a57ec2f1c461fe411b26"
PUBLISHER_ZIP_MD5 = "a87f9b4ef2e96625b737ffac8595c138"
PUBLIC_PREVIEW_SHA256 = "2dc9c81925ea2ed6b2cb82f13410868a96ccc93d1897f3eda6040e924c9dd82a"
WITHHELD = {"Souapiti", "Mambilla", "Kafin Zaki"}
REQUIRED_PROPERTIES = {"reference_id", "catchment_id", "published_name", "name_status",
                       "record_kind", "independent_existence_verified", "position_verified",
                       "facility_operational_status", "source_lineage", "source_doi", "source_license"}
GEOD = Geod(ellps="WGS84")


def normalize_name(name):
    if name is None:
        return None
    s = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode().lower()
    return " ".join(re.findall(r"[a-z0-9]+", s)) or None


def triage(data, *, strict=True):
    meta = data.get("metadata")
    if data.get("type") != "FeatureCollection" or not isinstance(meta, dict):
        raise ValueError("Require source-only FeatureCollection")
    if (meta.get("schema_version") != "BN_COMPILED_DAM_REFERENCE_PREVIEW_V1"
        or meta.get("publication_decision") != "REVIEW_CANDIDATES_ONLY"
        or meta.get("verified_facility_count") != 0
        or meta.get("source_doi") != "10.60507/FK2/YLDK1Y"
        or meta.get("source_license") != "CC BY 4.0"
        or meta.get("source_crs_epsg") != 4326
        or meta.get("source_csv_md5") != PUBLISHER_CSV_MD5
        or meta.get("source_shapefile_md5") != PUBLISHER_ZIP_MD5):
        raise ValueError("Source lineage, coordinate system or zero-confirmed gate changed")
    features = data.get("features")
    if not isinstance(features, list):
        raise ValueError("Missing source features")
    entries, seen = [], set()
    for feature in features:
        p = feature.get("properties", {})
        geo = feature.get("geometry", {})
        if set(p) != REQUIRED_PROPERTIES or feature.get("type") != "Feature":
            raise ValueError("Unexpected candidate fields: refuse private or unreviewed columns")
        ref = p["reference_id"]
        if (not isinstance(ref, str) or not re.fullmatch(r"WA26-\d{3}", ref)
            or ref != feature.get("id") or ref in seen):
            raise ValueError("Duplicate or invalid source-only reference ID")
        seen.add(ref)
        coord = geo.get("coordinates")
        if geo.get("type") != "Point" or not isinstance(coord, list) or len(coord) != 2:
            raise ValueError("Expected WGS84 source point")
        lon, lat = coord
        if (type(lon) not in (int, float) or type(lat) not in (int, float)
            or not (2 <= lon <= 16 and 4 <= lat <= 15)):
            raise ValueError("Position outside source QA bounds")
        if not re.fullmatch(r"SCMP-C(0[1-9]|1[0-9]|20)", str(p["catchment_id"])):
            raise ValueError("Invalid catchment assignment")
        name = p["published_name"]
        if name is not None and (not isinstance(name, str) or not 2 <= len(name) <= 96):
            raise ValueError("Bad published source name")
        if ((name is None) != (p["name_status"] == "unknown_in_source")):
            raise ValueError("Published-name and unknown-source flags disagree")
        if (p["name_status"] not in ("named_in_source", "unknown_in_source")
            or p["record_kind"] != "compiled_research_reference"
            or p["independent_existence_verified"] is not False
            or p["position_verified"] is not False
            or p["facility_operational_status"] != "unknown"
            or p["source_doi"] != meta["source_doi"]
            or p["source_license"] != meta["source_license"]
            or p["source_lineage"] != "Kouassi et al. 2026 compiled dataset"):
            raise ValueError("A candidate has changed its unverified-source contract")
        entries.append({"reference_id": ref, "catchment_id": p["catchment_id"],
                        "source_name": name, "coordinates": coord})
    if len({tuple(e["coordinates"]) for e in entries}) != len(entries):
        raise ValueError("Repeated source coordinates require separate examination")
    if strict:
        if (len(entries) != 189 or sum(e["source_name"] is not None for e in entries) != 71
            or sum(e["source_name"] is None for e in entries) != 118
            or meta.get("source_rows_intersecting_catchments") != 189
            or meta.get("named_source_rows_intersecting_catchments") != 71):
            raise ValueError("Original 189/71/118 publisher-candidate baseline drift")
        withholding = [e for e in entries if e["source_name"] in WITHHELD]
        if len(withholding) != 3 or {e["source_name"] for e in withholding} != WITHHELD:
            raise ValueError("Three identity disputes must remain held out")
        rows = [[*e["coordinates"], int(e["catchment_id"][-2:]), e["source_name"]]
                for e in entries if e["source_name"] not in WITHHELD]
        digest = hashlib.sha256(json.dumps(rows, ensure_ascii=False,
                          separators=(",", ":")).encode("utf-8")).hexdigest()
        if digest != PUBLIC_PREVIEW_SHA256:
            raise ValueError("Public 186-record research preview no longer source-identical")
    names = Counter(normalize_name(e["source_name"]) for e in entries
                    if normalize_name(e["source_name"]))
    distances = [float("inf")] * len(entries)
    neighbors = [None] * len(entries)
    nearby_250, nearby_1000, same_name_5km = set(), set(), set()
    for i, a in enumerate(entries):
        for j in range(i+1, len(entries)):
            b = entries[j]
            _, _, d = GEOD.inv(*a["coordinates"], *b["coordinates"])
            if d < distances[i]:
                distances[i], neighbors[i] = d, b["reference_id"]
            if d < distances[j]:
                distances[j], neighbors[j] = d, a["reference_id"]
            if d <= 250:
                nearby_250.update((i, j))
            if d <= 1000:
                nearby_1000.update((i, j))
            if d <= 5000 and a["source_name"] and b["source_name"] and normalize_name(a["source_name"]) == normalize_name(b["source_name"]):
                same_name_5km.update((i, j))
    priority_order = {"P0_WITHHELD_IDENTITY": 0, "P1_NEARBY_OR_REPEATED_NAME": 1,
                      "P2_UNNAMED_SOURCE": 2, "P3_NAMED_SOURCE": 3}
    queue = []
    for i, e in enumerate(entries):
        name = e["source_name"]
        flags = []
        if name in WITHHELD:
            flags.append("WITHHELD_DISPUTED_IDENTITY")
        if i in nearby_250:
            flags.append("ANOTHER_COMPILED_POINT_WITHIN_250M")
        elif i in nearby_1000:
            flags.append("ANOTHER_COMPILED_POINT_WITHIN_1KM")
        if name and names[normalize_name(name)] > 1:
            flags.append("REPEATED_SOURCE_NAME_COUNTRY_SUBSET")
        if i in same_name_5km:
            flags.append("SAME_NORMALIZED_NAME_WITHIN_5KM")
        if name is None:
            flags.append("SOURCE_NAME_MISSING")
        priority = ("P0_WITHHELD_IDENTITY" if name in WITHHELD else
                    "P1_NEARBY_OR_REPEATED_NAME" if i in nearby_1000 or (name and names[normalize_name(name)] > 1) else
                    "P2_UNNAMED_SOURCE" if name is None else "P3_NAMED_SOURCE")
        queue.append({**e, "priority": priority, "flags": flags,
                      "nearest_compiled_reference": neighbors[i],
                      "nearest_reference_distance_m_rounded": (round(distances[i]/10)*10 if neighbors[i] else None),
                      "display_eligibility": ("WITHHELD" if name in WITHHELD else "EXISTING_OPT_IN_UNVERIFIED_REFERENCE"),
                      "independent_existence_verified": False,
                      "position_verified": False,
                      "facility_status": "not_assessed",
                      "review_outcome": "REQUIRES_INDEPENDENT_EVIDENCE"})
    queue.sort(key=lambda e: (priority_order[e["priority"]], e["reference_id"]))
    groups = Counter(q["priority"] for q in queue)
    per_catchment = defaultdict(Counter)
    for q in queue:
        per_catchment[q["catchment_id"]][q["priority"]] += 1
    return {"schema_version": "BN_WA_DAM_REFERENCE_TRIAGE_V1",
            "status": "REVIEW_ONLY_COMPILED_SOURCES_NO_CONFIRMED_DAMS",
            "source_dataset_doi": meta["source_doi"],
            "source_csv_md5": meta["source_csv_md5"],
            "source_shapefile_md5": meta["source_shapefile_md5"],
            "candidate_count": len(entries),
            "source_named_count": sum(e["source_name"] is not None for e in entries),
            "source_unnamed_count": sum(e["source_name"] is None for e in entries),
            "withheld_identity_count": sum(q["priority"] == "P0_WITHHELD_IDENTITY" for q in queue),
            "confirmed_facility_count": 0,
            "independent_site_validation_performed": False,
            "automatic_deduplication_performed": False,
            "nearest_distance_not_position_uncertainty": True,
            "public_source_preview_sha256": PUBLIC_PREVIEW_SHA256,
            "priority_counts": {p: groups[p] for p in priority_order},
            "catchment_priority_counts": {f"SCMP-C{i:02d}": dict(per_catchment[f"SCMP-C{i:02d}"])
                                           for i in range(1,21)},
            "review_queue": queue}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-artifact", type=Path, required=True)
    parser.add_argument("--review-output", type=Path, required=True)
    args = parser.parse_args()
    if args.review_output.exists():
        raise SystemExit("Refusing to overwrite an existing research review queue")
    output = triage(json.loads(args.candidate_artifact.read_text(encoding="utf-8")))
    args.review_output.parent.mkdir(parents=True, exist_ok=True)
    with args.review_output.open("x", encoding="utf-8") as fh:
        json.dump(output, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print("STAGE3D-T RESEARCH-ONLY TRIAGE:", output["priority_counts"],
          "confirmed_dams=0; individual reviews not performed")


if __name__ == "__main__":
    main()
