#!/usr/bin/env python3
"""Synthetic-only regression for 2026 West Africa dams intake: no real points."""
import csv,hashlib,io,unittest
from preflight_wa_dams_2026 import preflight,fetch_pinned

COLS=["Country","DamName","Lat","Lon","Capacity_MCM","Year"]
def payload(country=("Nigeria","Ghana"),cols=COLS):
    out=io.StringIO()
    writer=csv.DictWriter(out,fieldnames=cols)
    writer.writeheader()
    for i,val in enumerate(country):
        writer.writerow({key:("Fictional dam" if key=="DamName" else val if key=="Country" else "0") for key in cols})
    result=out.getvalue().encode("utf-8")
    return result,hashlib.md5(result).hexdigest()

class PinnedDamPreflightTests(unittest.TestCase):
    def test_good_source_countries_not_site_points(self):
        data,md5=payload()
        v=preflight(data,expected_md5=md5,expected_count=2)
        self.assertEqual(v["nigeria_source_country_rows"],1)
        self.assertEqual(v["exact_positions_released"],0)
        self.assertFalse(v["catchment_overlay_performed"])
    def test_nga_iso_label(self):
        data,md5=payload(("NGA","NG","nigeria"))
        self.assertEqual(preflight(data,md5,3)["nigeria_source_country_rows"],3)
    def test_unknown_label_not_inferred(self):
        data,md5=payload(("Niger","Nigerian territory"))
        self.assertEqual(preflight(data,md5,2)["nigeria_source_country_rows"],0)
    def test_unknown_country_schema_is_review_state(self):
        cols=["Nation","DamName","Lat","Lon","Cap","Year"]
        data,md5=payload(cols=cols)
        v=preflight(data,md5,2)
        self.assertIsNone(v["nigeria_source_country_rows"])
        self.assertEqual(v["status"],"CHECKSUM_VERIFIED_COUNTRY_REVIEW_REQUIRED")
    def test_wrong_checksum_rejected(self):
        data,_=payload()
        with self.assertRaises(ValueError):preflight(data,"f"*32,2)
    def test_wrong_expected_count_rejected(self):
        data,md5=payload()
        with self.assertRaises(ValueError):preflight(data,md5,1429)
    def test_legacy_publisher_encoding_with_valid_checksum(self):
        raw="Country,DamName,Lat,Lon,Capacity_MCM,Year\nNigeria,Fictional reservoir name,0,0,2,2025\n".replace("reservoir", "réservoir").encode("cp1252")
        v=preflight(raw,hashlib.md5(raw).hexdigest(),1)
        self.assertEqual(v["source_character_encoding"],"cp1252")
        self.assertEqual(v["nigeria_source_country_rows"],1)
    def test_invalid_encoding_rejected(self):
        raw=b'\xff'*512
        with self.assertRaises(ValueError):preflight(raw,hashlib.md5(raw).hexdigest(),2)
    def test_ambiguous_country_fields_rejected(self):
        cols=["Country","COUNTRY","DamName","Lat","Lon","Cap"]
        data,md5=payload(cols=cols)
        with self.assertRaises(ValueError):preflight(data,md5,2)
    def test_duplicate_raw_csv_headers_are_rejected(self):
        raw=b"Country,Country,DamName,Lat,Lon,Cap\nNigeria,Nigeria,Example,0,0,2\n"
        with self.assertRaises(ValueError):
            preflight(raw,hashlib.md5(raw).hexdigest(),1)
    def test_invalid_url_fails_closed(self):
        with self.assertRaises(ValueError):fetch_pinned("https://example.com/unsafe")
    def test_no_source_values_returned(self):
        data,md5=payload(("Nigeria","Benin"))
        v=preflight(data,md5,2)
        self.assertNotIn("Fictional dam",str(v))
        self.assertNotIn("Benin",str(v))
        self.assertNotIn("latitudes",str(v))
    def test_missing_countries_not_nigeria(self):
        data,md5=payload(("",))
        self.assertEqual(preflight(data,md5,1)["nigeria_source_country_rows"],0)

if __name__=="__main__":unittest.main()
