#!/usr/bin/env python3
"""All names, coordinates and IDs below are fictional testing fixtures."""
import csv,hashlib,io,json,tempfile,unittest
from pathlib import Path
from pyproj import CRS
from zipfile import ZipFile
from review_wa_dam_identity_2026 import inspect,norm,to_year

COLS=["Country","ID","Dam_Name","Main_Sourc","Long_X","Lat_Y","Dam_Year"]
def make(rows):
    out=io.StringIO()
    w=csv.DictWriter(out,fieldnames=COLS)
    w.writeheader()
    w.writerows(rows)
    raw=out.getvalue().encode("utf-8")
    return raw,hashlib.md5(raw).hexdigest()
def zip_source():
    stream=io.BytesIO()
    with ZipFile(stream,"w") as z:
        z.writestr("dams/WA_Dams.shp",b"synthetic placeholder")
        z.writestr("dams/WA_Dams.prj",CRS.from_epsg(4326).to_wkt())
    raw=stream.getvalue()
    return raw,hashlib.md5(raw).hexdigest()
def dam(id,name,x,y,source="Invented research",country="Nigeria",year="2018"):
    return dict(Country=country,ID=id,Dam_Name=name,Main_Sourc=source,
                Long_X=str(x),Lat_Y=str(y),Dam_Year=year)

class IdentityQATests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.path=Path(self.tmp.name)/"catchments.geojson"
        f=[]
        for i in range(1,21):
            x=0 if i==1 else i*10
            ring=[[x,0],[x+2,0],[x+2,2],[x,2],[x,0]]
            f.append(dict(type="Feature",properties={"id":f"SCMP-C{i:02d}"},
                          geometry={"type":"Polygon","coordinates":[ring]}))
        self.path.write_text(json.dumps({"type":"FeatureCollection","features":f}))
        self.zip,self.zip_md5=zip_source()
    def tearDown(self):self.tmp.cleanup()
    def run_audit(self,rows):
        raw,hash=make(rows)
        return inspect(raw,self.zip,self.path,len(rows),
                       sum(x["Country"]=="Nigeria" for x in rows),hash,self.zip_md5)
    def test_source_identity_and_provenance(self):
        out=self.run_audit([dam("A","Fiction Alpha",1,1),dam("B","Fiction Beta",1.5,1.5,"")])
        self.assertEqual(out["source_rows_with_a_dam_name"],2)
        self.assertEqual(out["source_rows_without_source_label"],1)
        self.assertEqual(out["by_catchment"]["SCMP-C01"]["source_positions"],2)
        self.assertEqual(out["by_catchment"]["SCMP-C01"]["rows_with_source_label"],1)
        self.assertEqual(out["independently_verified_facilities"],0)
        self.assertEqual(out["individual_dam_points_published"],0)
    def test_pair_below_250m_is_not_deduplicated(self):
        out=self.run_audit([dam("A","Fiction Alpha",1,1),dam("B","Fiction Beta",1.001,1)])
        self.assertEqual(out["distinct_source_point_pairs_within_250m"],1)
        self.assertEqual(out["same_normalized_name_pairs_within_1km"],0)
        self.assertEqual(out["by_catchment"]["SCMP-C01"]["source_positions"],2)
    def test_same_name_nearby_not_called_one_dam(self):
        out=self.run_audit([dam("A","Fiction Epsilon",1,1),dam("B","Fiction Épsilon",1.002,1)])
        self.assertEqual(out["same_normalized_name_pairs_within_1km"],1)
        self.assertEqual(out["repeated_normalized_name_groups_countrywide"],1)
        self.assertEqual(out["nigeria_source_rows"],2)
    def test_same_name_far_apart_is_not_duplicate_entity_claim(self):
        out=self.run_audit([dam("A","Fiction Alpha",1,1),dam("B","Fiction Alpha",21,1)])
        self.assertEqual(out["repeated_normalized_name_groups_countrywide"],1)
        self.assertEqual(out["same_normalized_name_pairs_within_5km"],0)
    def test_unknown_names_and_year_handled(self):
        out=self.run_audit([dam("A","Unknown",1,1,year=""),
                            dam("B","Fiction Alpha",1.5,1.5,year="not a year")])
        self.assertEqual(out["source_rows_with_missing_name"],1)
        self.assertEqual(out["rows_with_missing_dam_year"],1)
        self.assertEqual(out["rows_with_unparseable_dam_year"],1)
    def test_no_non_nigeria_source_count(self):
        out=self.run_audit([dam("A","Fiction Alpha",1,1,country="Benin"),
                            dam("B","Fiction Beta",1.5,1.5)])
        self.assertEqual(out["nigeria_source_rows"],1)
        self.assertEqual(out["within_20_catchments_source_rows"],1)
    def test_invalid_source_md5_rejected(self):
        raw,_=make([dam("A","Fiction",1,1)])
        with self.assertRaises(ValueError):
            inspect(raw,self.zip,self.path,1,1,"f"*32,self.zip_md5)
    def test_invalid_zip_md5_rejected(self):
        raw,h=make([dam("A","Fiction",1,1)])
        with self.assertRaises(ValueError):
            inspect(raw,self.zip,self.path,1,1,h,"f"*32)
    def test_empty_name_normalisation(self):
        self.assertFalse(norm("N/A") in ("unused",))
        self.assertEqual(norm(" Éléphant-Dam "), "elephant dam")
        self.assertEqual(to_year("2020"),2020)
        self.assertIsNone(to_year("2030"))
    def test_no_individual_names_or_positions_in_report(self):
        out=self.run_audit([dam("TEST-PRIVATE-STRING","Fiction-Example-Claim",1.11111,1.00001)])
        result=json.dumps(out)
        self.assertNotIn("Fiction-Example-Claim",result)
        self.assertNotIn("TEST-PRIVATE-STRING",result)
        self.assertNotIn("1.11111",result)
        self.assertNotIn("coordinates",result)
    def test_invalid_position_rejected(self):
        with self.assertRaises(ValueError):
            self.run_audit([dam("A","Fiction",190,2)])
    def test_missing_source_column_rejected(self):
        raw,h=make([dam("A","Fiction",1,1)])
        raw=raw.replace(b"Main_Sourc",b"Other_Src_")
        with self.assertRaises(ValueError):
            inspect(raw,self.zip,self.path,1,1,hashlib.md5(raw).hexdigest(),self.zip_md5)

if __name__=="__main__":unittest.main()
