#!/usr/bin/env python3
"""Synthetic-only Stage 3D-W source and EO metadata tests. No HTTP on PR."""
import copy
import json
import unittest
from test_stage3d_v_osm_context_review import fixture as u_fixture
from build_stage3d_v_osm_context_review import compare as make_v
from build_stage3d_w_lineage_eo_discovery import (
    REFERENCES,EPOCHS,assemble,make_search,parse_osm_history,parse_stac,validate_inputs)

def cases():
    u=u_fixture()
    ids=["WA26-003","WA26-083","WA26-184","WA26-185","WA26-186"]
    for r,new in zip(u["records"][3:8],ids):
        r["source_reference_id"]=new
    osm=[]
    for ref,way in REFERENCES.items():
        row=next(r for r in u["records"] if r["source_reference_id"]==ref)
        lon,lat=row["compiled_reference_position_WGS84"]
        osm.append({"type":"way","id":int(way.split("/")[1]),
                    "center":{"lon":lon,"lat":lat},
                    "tags":{"waterway":"dam"}})
    v=make_v(u,{"type":"FeatureCollection","osm3s":{"timestamp_osm_base":"2026-10-29T04:55:17Z"},
                "elements":osm})
    return u,v

def fake_history(osm_id):
    id=osm_id.split("/")[1]
    return (f'<osm version="0.6"><way id="{id}" version="1" timestamp="2017-02-01T00:00:00Z">'
        '<tag k="waterway" v="dam"/></way>'
        f'<way id="{id}" version="2" timestamp="2024-02-01T00:00:00Z">'
        '<tag k="waterway" v="dam"/><tag k="source:geometry" v="imagery"/></way></osm>').encode()

def fake_stac(body):
    query=json.loads(body)
    start=query["datetime"][:4]
    items=[]
    for i,c in enumerate([48,10,4]):
        items.append({"type":"Feature","collection":"sentinel-2-c1-l2a","id":f"SCENE-{start}-{i}",
        "properties":{"datetime":f"{start}-08-01T10:00:00Z","eo:cloud_cover":c},
        "links":[{"rel":"self","href":f"https://earth-search.aws.element84.com/v1/collections/sentinel-2-c1-l2a/items/SCENE-{start}-{i}"}]})
    return json.dumps({"type":"FeatureCollection","features":items}).encode()

class StageWTests(unittest.TestCase):
    def test_research_only_5_cases_and_shortlisted_metadata(self):
        u,v=cases(); history_calls=[];stac_calls=[]
        def history(url,**kwargs):
            history_calls.append(url)
            return fake_history(url.split("/api/0.6/")[1].replace("/history",""))
        def catalog(url,body=None,**kwargs):
            stac_calls.append(json.loads(body));return fake_stac(body)
        out=assemble(u,v,fetch_history=history,fetch_scene=catalog)
        self.assertEqual(out["reviewed_site_count"],5)
        self.assertEqual(out["independently_confirmed_dams"],0)
        self.assertEqual(out["human_release_receipts_generated"],0)
        self.assertFalse(out["public_map_changes"])
        self.assertEqual(len(history_calls),5)
        self.assertEqual(len(stac_calls),10)
        self.assertEqual(set(z["source_reference_id"] for z in out["records"]),set(REFERENCES))
        for r in out["records"]:
            self.assertFalse(r["constructed_dam_independently_verified"])
            self.assertFalse(r["dam_wall_independently_located"])
            self.assertFalse(r["source_lineage_independent"])
            self.assertEqual(r["osm_lineage_context"]["history_status"],"AVAILABLE_TAG_HISTORY_ONLY")
            for epoch,obj in r["sentinel2_scene_metadata"].items():
                self.assertEqual(obj["catalog_state"],"SCENE_METADATA_FOUND")
                self.assertEqual([x["scene_cloud_pct"] for x in obj["shortlist"]],[4.0,10.0,48.0])
                self.assertTrue(all(x["scene_cloud_not_point_cloud"] for x in obj["shortlist"]))
                self.assertTrue(all(x["structure_visually_confirmed"] is False for x in obj["shortlist"]))
        self.assertTrue(all(r["osm_lineage_context"]["independent_lineage_verified"] is False for r in out["records"]))
    def test_unavailable_external_systems_not_absence(self):
        u,v=cases()
        def fail(*args,**kwargs):raise TimeoutError("synthetic outage")
        x=assemble(u,v,fetch_history=fail,fetch_scene=fail)
        self.assertTrue(all(r["osm_lineage_context"]["history_status"]=="LOOKUP_UNAVAILABLE_NOT_INDEPENDENT" for r in x["records"]))
        self.assertTrue(all(z["catalog_state"]=="CATALOG_UNAVAILABLE_NOT_NO_IMAGERY"
                       for r in x["records"] for z in r["sentinel2_scene_metadata"].values()))
        self.assertEqual(x["independently_confirmed_dams"],0)
    def test_history_source_tag_not_independence(self):
        h=b'<osm><way id="571289118" version="1" timestamp="2019-01-01T00:00:00Z"><tag k="source" v="Kouassi bonndata"/></way></osm>'
        x=parse_osm_history(h,"way/571289118")
        self.assertTrue(x["possible_compiled_dataset_source_tag"])
        self.assertFalse(x["independent_lineage_verified"])
        self.assertFalse(x["osm_editor_personal_data_exported"])
    def test_invalid_history_has_no_success(self):
        for raw in [b"<html></html>",b"<osm></osm>",
                    b'<osm><way id="99" version="1" timestamp="2021-01-01T00:00:00Z"/></osm>',
                    b'<osm><way id="571289118" version="1" timestamp="invalid"/></osm>']:
            with self.subTest(raw=raw),self.assertRaises(ValueError):parse_osm_history(raw,"way/571289118")
    def test_unverified_stage_v_or_stage_u_flags_are_protected(self):
        u,v=cases()
        for obj,key,value in [(u,"reviewed_and_confirmed",1),
                              (u,"source_pinned_public_preview_sha256","false"),
                              (v,"confirmed_facility_count",1),
                              (v,"public_map_updated",True)]:
            w=copy.deepcopy(u);z=copy.deepcopy(v)
            (w if obj is u else z)[key]=value
            with self.subTest(k=key),self.assertRaises(ValueError):validate_inputs(w,z)
        x=copy.deepcopy(v)
        for r in x["records"]:
            if r["reference_id"]=="WA26-185":
                r["osm_context_candidates"]=[]
        with self.assertRaises(ValueError):validate_inputs(u,x)
    def test_cloud_is_scene_level_and_out_of_window_rejected(self):
        f=json.loads(fake_stac(make_search([7,9],"historical_2019")))
        x=parse_stac(f,[7,9],EPOCHS["historical_2019"])
        self.assertEqual(x["eligible_item_count"],3)
        self.assertTrue(all(z["image_pixels_downloaded"] is False for z in x["shortlist"]))
        f["features"][0]["collection"]="other"
        with self.assertRaises(ValueError):parse_stac(f,[7,9],EPOCHS["historical_2019"])
        self.assertEqual(parse_stac({"type":"FeatureCollection","features":[]},[7,9],EPOCHS["historical_2019"])["catalog_state"],
                         "NO_USABLE_CATALOG_ITEMS_NOT_NO_IMAGERY")
    def test_point_stac_request_uses_bounded_epochs(self):
        for epoch in EPOCHS:
            data=json.loads(make_search([8.22,10.03],epoch))
            self.assertEqual(data["limit"],40)
            self.assertEqual(data["collections"],["sentinel-2-c1-l2a"])
            self.assertEqual(data["intersects"]["coordinates"],[8.22,10.03])
            self.assertEqual(data["datetime"],EPOCHS[epoch])
    def test_missing_osm_never_promotes(self):
        u,v=cases()
        v["osm_query_state"]="QUERY_UNAVAILABLE"
        v["osm_timestamp"]=None
        for r in v["records"]:
            r["osm_context_candidates"]=[]
            r["osm_candidate_count_in_radius"]=None
        out=assemble(u,v,fetch_history=lambda *a,**k:None,
                     fetch_scene=lambda *a,**k:fake_stac(k["body"]))
        self.assertTrue(all(r["osm_lineage_context"]["history_status"]=="UPSTREAM_CONTEXT_NOT_AVAILABLE" for r in out["records"]))
        self.assertFalse(any(r["constructed_dam_independently_verified"] for r in out["records"]))
    def test_bad_osm_id_is_rejected(self):
        with self.assertRaises(ValueError):parse_osm_history(b"<osm></osm>","way/invalid")
    def test_no_personal_author_in_report(self):
        source=b'<osm><way id="571289118" version="1" timestamp="2020-01-01T00:00:00Z" user="Test Person" uid="1234" changeset="2"><tag k="waterway" v="dam"/></way></osm>'
        obj=parse_osm_history(source,"way/571289118")
        self.assertNotIn("Test Person",json.dumps(obj))
        self.assertNotIn("uid",json.dumps(obj))
        self.assertFalse(obj["independent_lineage_verified"])

if __name__=="__main__":unittest.main()
