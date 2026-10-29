#!/usr/bin/env python3
"""Fast isolated QA for NASA POWER point climate, not basin-wide precipitation."""
import json,calendar,unittest
from build_stage3d_bo_bq_nasa_power_climate import registry,api_url,validate_reply,START,END,VARS,DATA,make_climate,integrated,csv_text,SNAP

class ClimateTests(unittest.TestCase):
 def example(self):
  loc=registry()[0]
  values={name:{} for name in VARS}
  for y in range(START,END+1):
   for m in range(1,13):
    values["PRECTOTCORR"][f"{y}{m:02d}"]=2.2
    values["T2M"][f"{y}{m:02d}"]=25.0
  return loc,{"type":"Feature","geometry":{"type":"Point","coordinates":[loc["label_lon"],loc["label_lat"]]},
    "properties":{"parameter":values},
    "parameters":{"PRECTOTCORR":{"units":"mm/day"},"T2M":{"units":"C"}}}
 def test_full_historical_point_schema_and_units(self):
  row,data=self.example()
  self.assertTrue(validate_reply(data,row))
  u=api_url(row)
  self.assertIn("temporal/monthly/point",u)
  self.assertIn("PRECTOTCORR",u)
  self.assertIn("T2M",u)
  self.assertIn("start=2005",u)
  self.assertIn("end=2025",u)
 def test_reject_wrong_units_missing_month_and_mislocated_point(self):
  row,data=self.example()
  data["parameters"]["PRECTOTCORR"]["units"]="mm"
  with self.assertRaises(ValueError):validate_reply(data,row)
  data["parameters"]["PRECTOTCORR"]["units"]="mm/day"
  del data["properties"]["parameter"]["T2M"]["200512"]
  with self.assertRaises(ValueError):validate_reply(data,row)
  data["properties"]["parameter"]["T2M"]["200512"]=25
  data["geometry"]["coordinates"][0]+=5
  with self.assertRaises(ValueError):validate_reply(data,row)
 def test_pinned_existing_source_coverage_when_available(self):
  if not SNAP.exists():return
  cl=make_climate(registry(),SNAP)
  reg=integrated(cl,registry())
  self.assertEqual(len(cl["records"]),20)
  self.assertEqual(len(reg["rows"]),20)
  self.assertEqual(len(cl["records"][0]["annual"]),21)
  self.assertEqual(len(cl["records"][0]["monthly_climatology"]),12)
  self.assertEqual(len(csv_text(reg).splitlines()),21)
  self.assertTrue(all(z["nasa_power_mean_annual_precip_mm_2005_2025"]>0 for z in reg["rows"]))
  self.assertTrue(all(z["climate_spatial_basis"]=="NASA_POWER_MAP_LABEL_POINT_NOT_CATCHMENT_MEAN" for z in reg["rows"]))
if __name__=="__main__":unittest.main()
