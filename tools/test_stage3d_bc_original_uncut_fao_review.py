#!/usr/bin/env python3
"""Synthetic-only tests of bounded FAO WFS response and uncut model comparison."""
import copy, io, json, math, unittest
from pathlib import Path
from build_stage3d_bc_original_uncut_fao_review import (
 EXPECTED,INPUTS,SCHEMA,haversine,lines,validate_feature,bounded_get,
 closest_endpoints,oriented_distance,source_reconciliation
)

def sample(id,next_down,coords):
    return {"type":"Feature","properties":{"hyriv_id":id,"next_down":next_down,
        "source":"synthetic"},"geometry":{"type":"LineString","coordinates":coords}}

def packet(f):
    return json.dumps({"type":"FeatureCollection","features":[f]}).encode()

def fake_opener(payloads):
    def fetch(request,timeout):
        from urllib.parse import parse_qs,urlparse
        fid=int(parse_qs(urlparse(request.full_url).query)["cql_filter"][0].split("=")[1])
        if fid not in payloads:raise ValueError("No source")
        return io.BytesIO(payloads[fid])
    return fetch

class UncutTests(unittest.TestCase):
 def test_exact_queue_scope(self):
  self.assertEqual(len(INPUTS),6)
  self.assertEqual(len(EXPECTED),3)
  self.assertEqual(set(INPUTS),{10505946,10506074,10566530,10567236,10568272,10568127})
 def test_synthetic_wfs_exact_single_response_and_id(self):
  p={10505946:packet(sample(10505946,10506074,[[6,10],[6.01,10.01]]))}
  r,raw,d=bounded_get(10505946,retries=1,opener=fake_opener(p))
  self.assertEqual(r["id"],10505946)
  self.assertEqual(r["next_down"],10506074)
  self.assertEqual(raw["type"],"Feature")
  self.assertEqual(len(d),64)
  with self.assertRaises(ValueError):bounded_get(1234567,retries=1,opener=fake_opener(p))
  with self.assertRaises(ValueError):bounded_get(10506074,retries=1,opener=fake_opener(p))
 def test_reject_changed_or_multiple_fao_sources(self):
  p={10505946:packet(sample(999,10506074,[[6,10],[6.01,10.01]]))}
  with self.assertRaises(ValueError):bounded_get(10505946,retries=1,opener=fake_opener(p))
  bad={"type":"FeatureCollection","features":[sample(10505946,10506074,[[6,10],[6.01,10.01]])]*2}
  p[10505946]=json.dumps(bad).encode()
  with self.assertRaises(ValueError):bounded_get(10505946,retries=1,opener=fake_opener(p))
 def test_full_source_min_endpoint_diagnostic(self):
  a=[[(6,10),(6.05,10)]]
  b=[[(6.05,10),(6.1,10)]]
  self.assertAlmostEqual(closest_endpoints(a,b)[0],0)
  self.assertAlmostEqual(oriented_distance(a,b),0)
  self.assertGreater(haversine((6,10),(6.05,10)),5000)
 def test_multi_segment_and_missing_geometry_refused(self):
  f=sample(10505946,10506074,[[6,10],[6.02,10.03]])
  f["geometry"]={"type":"MultiLineString","coordinates":[[[6,10],[6.02,10.03]],[[6.5,10.2],[6.6,10.3]]]}
  self.assertEqual(len(lines(f)),2)
  for wrong in [{"type":"Point","coordinates":[6,10]},
                 {"type":"LineString","coordinates":[[6,10]]},
                 {"type":"LineString","coordinates":[[float('nan'),10],[6,10]]}]:
   f["geometry"]=wrong
   with self.assertRaises(ValueError):lines(f)
 def test_reconcile_requires_original_next_down_exact(self):
  original={a:{"id":a,"next_down":b,"parts":[[(6,10),(6.01,10.01)]]} for a,b,_,_ in EXPECTED}
  original.update({b:{"id":b,"next_down":None,"parts":[[(6.01,10.01),(6.05,10.05)]]}
                   for a,b,_,_ in EXPECTED})
  source={"schema_version":"BN_STAGE3D_AU_FAO_TOPOLOGY_SUMMARY_V1",
    "source_manifest_sha256":"abc"}
  clipped={"schema_version":"BN_STAGE3D_AY_FAO_CLIPPED_ENDPOINT_GAP_QA_V1",
    "source_manifest_sha256":"abc","source_index_sha256":"def"}
  report=source_reconciliation(original,clipped,source)
  self.assertEqual(report["schema_version"],SCHEMA)
  self.assertEqual(report["targeted_original_reaches"],6)
  self.assertEqual(len(report["source_gap_pairs"]),3)
  self.assertFalse(any("verified" in row["interpretation"].lower()
                        and "not_verified" not in row["interpretation"].lower()
                        for row in report["source_gap_pairs"]))
  original[10505946]["next_down"]=12345
  with self.assertRaises(ValueError):source_reconciliation(original,clipped,source)
 def test_original_source_coordinates_never_survey_grade(self):
  f=sample(10505946,10506074,[[6,10],[6.2,10.2]])
  ok=validate_feature(f,10505946)
  self.assertEqual(ok["geometry_type"],"LineString")
  self.assertNotIn("surveyor",str(ok))
if __name__=="__main__":unittest.main()
