#!/usr/bin/env python3
"""Synthetic only: WGS84 physical-source preflight and provisional catchment overlay."""
import csv,hashlib,io,json,tempfile,unittest,zipfile
from pathlib import Path
from pyproj import CRS
from review_wa_dam_catchments_2026 import inspect,ensure_wgs84_zip

HEAD=["Country","Long_X","Lat_Y","ID","Dam_Name","Cap"]
def records(rows):
    text=io.StringIO()
    writer=csv.DictWriter(text,fieldnames=HEAD)
    writer.writeheader()
    writer.writerows(rows)
    data=text.getvalue().encode("utf-8")
    return data,hashlib.md5(data).hexdigest()
def zipped(epsg=4326):
    out=io.BytesIO()
    with zipfile.ZipFile(out,"w") as z:
        z.writestr("dam/WA_Dams.shp",b"placeholder synthetic geometry")
        z.writestr("dam/WA_Dams.prj",CRS.from_epsg(epsg).to_wkt())
    data=out.getvalue()
    return data,hashlib.md5(data).hexdigest()

class SpatialAuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.geopath=Path(self.tmp.name)/"test.geojson"
        features=[]
        for i in range(1,21):
            if i==1:ring=[[0,0],[2,0],[2,2],[0,2],[0,0]]
            elif i==2:ring=[[1,1],[3,1],[3,3],[1,3],[1,1]]
            else:
                x=i*10
                ring=[[x,0],[x+2,0],[x+2,2],[x,2],[x,0]]
            features.append({"type":"Feature","properties":{"id":f"SCMP-C{i:02d}"},
                             "geometry":{"type":"Polygon","coordinates":[ring]}})
        self.geopath.write_text(json.dumps({"type":"FeatureCollection","features":features}))
        self.zip,self.md5_zip=zipped()
    def tearDown(self):self.tmp.cleanup()
    def audit(self,rows):
        payload,md5=records(rows)
        return inspect(payload,self.zip,self.geopath,expected_count=len(rows),
                       expected_nigeria=sum(r["Country"].lower()=="nigeria" for r in rows),
                       csv_md5=md5,zip_md5=self.md5_zip)
    def test_overlap_not_duplicate_unique_count(self):
        rows=[dict(Country="Nigeria",Long_X="1.5",Lat_Y="1.5",ID="1",Dam_Name="Fiction 1",Cap="2"),
              dict(Country="Nigeria",Long_X="5",Lat_Y="5",ID="2",Dam_Name="Fiction 2",Cap="4")]
        out=self.audit(rows)
        self.assertEqual(out["source_country_nigeria_rows"],2)
        self.assertEqual(out["nigeria_source_rows_intersecting_any_study_catchment"],1)
        self.assertEqual(out["source_rows_intersecting_multiple_study_catchments"],1)
        self.assertEqual(out["intersections_not_unique_dams"],2)
        self.assertEqual(out["overlap_counts_by_catchment"],{"SCMP-C01":1,"SCMP-C02":1})
        self.assertEqual(out["individual_coordinates_published"],0)
    def test_border_included_but_not_field_verified(self):
        out=self.audit([dict(Country="Nigeria",Long_X="0",Lat_Y="1",ID="4",Dam_Name="Fiction",Cap="0")])
        self.assertEqual(out["nigeria_source_rows_intersecting_any_study_catchment"],1)
        self.assertGreaterEqual(out["boundary_intersection_candidate_count"],1)
    def test_missing_location_is_not_geo_discovery(self):
        out=self.audit([dict(Country="Nigeria",Long_X="",Lat_Y="",ID="4",Dam_Name="Fiction",Cap="0")])
        self.assertEqual(out["nigeria_rows_without_numeric_location"],1)
        self.assertEqual(out["nigeria_source_rows_intersecting_any_study_catchment"],0)
    def test_repeated_source_id_and_coordinate_are_not_deduplicated_silently(self):
        rows=[dict(Country="Nigeria",Long_X="1",Lat_Y="1",ID="9",Dam_Name="Fiction",Cap="0"),
              dict(Country="Nigeria",Long_X="1",Lat_Y="1",ID="9",Dam_Name="Fiction",Cap="0")]
        out=self.audit(rows)
        self.assertEqual(out["nigeria_repeated_source_ids"],1)
        self.assertEqual(out["nigeria_repeated_coordinate_pairs"],1)
    def test_non_nigeria_not_counted_in_catchment(self):
        out=self.audit([dict(Country="Ghana",Long_X="1.5",Lat_Y="1.5",ID="1",Dam_Name="Fiction",Cap="0")])
        self.assertEqual(out["nigeria_source_rows_intersecting_any_study_catchment"],0)
    def test_unpinned_shapefile_fails(self):
        with self.assertRaises(ValueError):ensure_wgs84_zip(self.zip,"f"*32)
    def test_projected_meter_coordinates_are_rejected(self):
        data,md5=zipped(3857)
        with self.assertRaises(ValueError):ensure_wgs84_zip(data,md5)
    def test_missing_prj_fails(self):
        mem=io.BytesIO()
        with zipfile.ZipFile(mem,"w") as z:z.writestr("WA_Dams.shp",b"test")
        data=mem.getvalue()
        with self.assertRaises(ValueError):ensure_wgs84_zip(data,hashlib.md5(data).hexdigest())
    def test_coordinate_outside_earth_is_flagged(self):
        out=self.audit([dict(Country="Nigeria",Long_X="181",Lat_Y="1",ID="1",Dam_Name="Fiction",Cap="0")])
        self.assertEqual(out["nigeria_rows_with_invalid_numeric_location"],1)

if __name__=="__main__":unittest.main()
