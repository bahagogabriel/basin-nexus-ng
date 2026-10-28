#!/usr/bin/env python3
"""Synthetic-only Stage 3D-T fail-closed tests. Fictional source identifiers."""
import copy
import unittest
from triage_wa_dam_compiled_references import triage, PUBLISHER_CSV_MD5, PUBLISHER_ZIP_MD5


def fixture(name1="Synthetic Test North", name2=None, xy2=(7.0006, 10.0)):
    features = []
    for i, (name, xy) in enumerate([(name1, (7.0, 10.0)), (name2, xy2)], 1):
        rid = f"WA26-{i:03d}"
        features.append({"type": "Feature", "id": rid, "geometry": {"type": "Point", "coordinates": list(xy)},
                         "properties": {"reference_id": rid, "catchment_id": "SCMP-C01",
                                        "published_name": name,
                                        "name_status": "named_in_source" if name else "unknown_in_source",
                                        "record_kind": "compiled_research_reference",
                                        "independent_existence_verified": False, "position_verified": False,
                                        "facility_operational_status": "unknown",
                                        "source_lineage": "Kouassi et al. 2026 compiled dataset",
                                        "source_doi": "10.60507/FK2/YLDK1Y", "source_license": "CC BY 4.0"}})
    return {"type": "FeatureCollection", "metadata": {"schema_version": "BN_COMPILED_DAM_REFERENCE_PREVIEW_V1",
            "publication_decision": "REVIEW_CANDIDATES_ONLY", "verified_facility_count": 0,
            "source_doi": "10.60507/FK2/YLDK1Y", "source_license": "CC BY 4.0",
            "source_crs_epsg": 4326, "source_csv_md5": PUBLISHER_CSV_MD5,
            "source_shapefile_md5": PUBLISHER_ZIP_MD5}, "features": features}


class SourceTriageTests(unittest.TestCase):
    def test_nearby_does_not_promote_or_merge(self):
        data = triage(fixture(), strict=False)
        self.assertEqual(data["candidate_count"], 2)
        self.assertEqual(data["confirmed_facility_count"], 0)
        self.assertFalse(data["automatic_deduplication_performed"])
        self.assertEqual(data["priority_counts"]["P1_NEARBY_OR_REPEATED_NAME"], 2)
        self.assertTrue(all(q["independent_existence_verified"] is False for q in data["review_queue"]))
        self.assertTrue(all(q["position_verified"] is False for q in data["review_queue"]))
        self.assertEqual(data["source_unnamed_count"], 1)

    def test_same_name_far_apart_is_still_identity_review_not_duplicate(self):
        data = triage(fixture("Éxample", "Example", (9.5, 10.0)), strict=False)
        self.assertEqual(data["priority_counts"]["P1_NEARBY_OR_REPEATED_NAME"], 2)
        self.assertEqual(data["candidate_count"], 2)
        self.assertTrue(all("REPEATED_SOURCE_NAME_COUNTRY_SUBSET" in q["flags"] for q in data["review_queue"]))
        self.assertFalse(any("SAME_NORMALIZED_NAME_WITHIN_5KM" in q["flags"] for q in data["review_queue"]))

    def test_withheld_identity_always_first(self):
        data = triage(fixture("Mambilla", None), strict=False)
        self.assertEqual(data["review_queue"][0]["priority"], "P0_WITHHELD_IDENTITY")
        self.assertEqual(data["withheld_identity_count"], 1)

    def test_false_claims_rejected(self):
        x = fixture()
        for key, val in [("independent_existence_verified", True), ("position_verified", True),
                         ("facility_operational_status", "operational")]:
            bad = copy.deepcopy(x)
            bad["features"][0]["properties"][key] = val
            with self.subTest(key=key), self.assertRaises(ValueError): triage(bad, strict=False)

    def test_source_name_mismatch_and_unexpected_private_fields_rejected(self):
        x = fixture()
        x["features"][1]["properties"]["name_status"] = "named_in_source"
        with self.assertRaises(ValueError): triage(x, strict=False)
        x = fixture()
        x["features"][0]["properties"]["private_drive_id"] = "do_not_publish"
        with self.assertRaises(ValueError): triage(x, strict=False)

    def test_duplicate_and_bad_coordinates_rejected(self):
        x = fixture()
        x["features"][1]["geometry"]["coordinates"] = [7.0, 10.0]
        with self.assertRaises(ValueError): triage(x, strict=False)
        x = fixture()
        x["features"][0]["geometry"]["coordinates"] = [19.0, 10.0]
        with self.assertRaises(ValueError): triage(x, strict=False)

    def test_source_lineage_and_record_baseline_fail_closed(self):
        x = fixture()
        with self.assertRaises(ValueError): triage(x, strict=True)
        x["metadata"]["source_csv_md5"] = "0" * 32
        with self.assertRaises(ValueError): triage(x, strict=False)


if __name__ == "__main__":
    unittest.main()
