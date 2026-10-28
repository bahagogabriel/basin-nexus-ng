#!/usr/bin/env python3
"""Synthetic dam source dataset: not actual dams."""
import csv,io,hashlib,json,tempfile,unittest
from pathlib import Path
from zipfile import ZipFile
from pyproj import CRS
from build_wa_2026_dam_candidate_review import build,clean_display_name

def fixtures():
  folder=tempfile.TemporaryDirectory()
  geopath=Path(folder.name)/"catch.geojson"
  geo={"type":"FeatureCollection","features":[]}
  for i in range(1,21):
    x=0 if i==1 else i*10
    geo["features"].append({"type":"Feature","properties":{"id":f"SCMP-C{i:02d}"},
      "geometry":{"type":"Polygon","coordinates":[[[x,0],[x+2,0],[x+2,2],[x,2],[x,0]]]}})
  geopath.write_text(json.dumps(geo))
  out=io.StringIO()
  writer=csv.DictWriter(out,fieldnames=["Country","ID","Long_X","Lat_Y","Dam_Name","Main_Sourc"])
  writer.writeheader()
  for i in range(231):
    iswithin=i<189
    writer.writerow({"Country":"Nigeria","ID":str(i+1),
                     "Long_X":.2+(i%100)*.013 if iswithin else 3.0,
                     "Lat_Y":.2+(i%100)*.013 if iswithin else 3.0,
                     "Dam_Name":("Fictional Training Dam "+str(i+1)) if i<71 else "",
                     "Main_Sourc":"Artificial testing only"})
  raw=out.getvalue().encode()
  z=io.BytesIO()
  with ZipFile(z,"w") as f:
    f.writestr("source/WA_Dams.shp",b"synthetic placeholder")
    f.writestr("source/WA_Dams.prj",CRS.from_epsg(4326).to_wkt())
  return folder,geopath,raw,hashlib.md5(raw).hexdigest(),z.getvalue(),hashlib.md5(z.getvalue()).hexdigest()

class CandidateTests(unittest.TestCase):
  def setUp(self):
    self.folder,self.geopath,self.csv,self.csv_md5,self.z,self.z_md5=fixtures()
  def tearDown(self):self.folder.cleanup()
  def make(self,**other):
    return build(self.csv,self.z,self.geopath,self.csv_md5,self.z_md5,
                 expected_regional=231,expected_nigeria=231,**other)
  def test_source_counts(self):
    c=self.make()
    self.assertEqual(len(c["features"]),189)
    self.assertEqual(sum(x["properties"]["published_name"] is not None for x in c["features"]),71)
    self.assertEqual(c["metadata"]["verified_facility_count"],0)
    self.assertEqual(c["metadata"]["publication_decision"],"REVIEW_CANDIDATES_ONLY")
  def test_missing_name_not_named_dam(self):
    c=self.make()
    f=c["features"][71]
    self.assertIsNone(f["properties"]["published_name"])
    self.assertEqual(f["properties"]["name_status"],"unknown_in_source")
    self.assertIs(f["properties"]["independent_existence_verified"],False)
  def test_no_invented_names(self):
    self.assertIsNone(clean_display_name(""))
    self.assertIsNone(clean_display_name("Unknown"))
    self.assertIsNone(clean_display_name("Dam"))
    self.assertIsNone(clean_display_name("<script>alert(1)</script>"))
  def test_no_raw_source_columns(self):
    for f in self.make()["features"]:
      self.assertNotIn("Main_Sourc",f["properties"])
      self.assertNotIn("Dam_Year",f["properties"])
      self.assertNotIn("Res_Vol",f["properties"])
  def test_no_unpinned_csv(self):
    with self.assertRaises(ValueError):build(self.csv,self.z,self.geopath,"f"*32,self.z_md5,231,231)
  def test_no_unpinned_shapefile(self):
    with self.assertRaises(ValueError):build(self.csv,self.z,self.geopath,self.csv_md5,"f"*32,231,231)
  def test_wrong_country_count(self):
    with self.assertRaises(ValueError):build(self.csv,self.z,self.geopath,self.csv_md5,self.z_md5,231,230)
  def test_source_id_required(self):
    rows=self.csv.replace(b"Nigeria,1,",b"Nigeria,,",1)
    with self.assertRaises(ValueError):
      build(rows,self.z,self.geopath,hashlib.md5(rows).hexdigest(),self.z_md5,231,231)
if __name__=="__main__":unittest.main()
