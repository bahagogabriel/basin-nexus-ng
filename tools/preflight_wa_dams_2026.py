#!/usr/bin/env python3
"""Preflight external 2026 West Africa dam CSV without releasing records/coordinates.

Kouassi et al. (2026), bonndata CC BY 4.0, doi:10.60507/FK2/YLDK1Y.
Download must match the publisher's MD5 before reading rows. Artifacts contain
aggregate-only source quality findings; never stakeholder records or field-derived
locations. No download is required for the synthetic CI unit tests.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import io
import json
import re
import sys
import time
import urllib.error
import urllib.request
from collections import Counter
from pathlib import Path

SOURCE_DOI="10.60507/FK2/YLDK1Y"
CSV_DOI="10.60507/FK2/YLDK1Y/WKZDRQ"
EXPECTED_CSV_MD5="046b106da1e3a57ec2f1c461fe411b26"
EXPECTED_ROWS=1429
URL=("https://bonndata.uni-bonn.de/api/access/datafile/:persistentId/"
     "?persistentId=doi%3A10.60507%2FFK2%2FYLDK1Y%2FWKZDRQ")
MAX_BYTES=3_000_000
CANON_COUNTRY={"Country","COUNTRY","country","Country_Name","country_name",
               "CountryName","COUNTRY_NAME","Country_1"}
NIGERIA={"nigeria","nga","ng"}

def fetch_pinned(url=URL):
    """Retrieve one published datafile, fail rather than silently switching origin."""
    if url!=URL:
        raise ValueError("Only the registered, pinned Dataverse file is permitted")
    last=None
    for attempt in range(3):
        try:
            request=urllib.request.Request(url,headers={"User-Agent":"BasinNexusSourceQA/1.0"})
            with urllib.request.urlopen(request,timeout=35) as stream:
                data=stream.read(MAX_BYTES+1)
            if len(data)>MAX_BYTES or len(data)<300:
                raise ValueError("Unexpected source file size")
            return data
        except (urllib.error.URLError,TimeoutError,OSError) as exc:
            last=exc
            if attempt<2:time.sleep(2*(attempt+1))
    raise RuntimeError("Pinned remote file unavailable; no candidate data accepted") from last

def preflight(data, expected_md5=EXPECTED_CSV_MD5, expected_count=EXPECTED_ROWS):
    """Return *only aggregate* QA; no record values or coordinates."""
    if not isinstance(data,bytes) or len(data)>MAX_BYTES:
        raise ValueError("Invalid file input")
    md5=hashlib.md5(data).hexdigest()
    if md5.lower()!=expected_md5.lower():
        raise ValueError("Source checksum differs from publisher's official MD5")
    try:
        text=data.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValueError("CSV encoding unexpected; manual review required") from exc
    rows=list(csv.DictReader(io.StringIO(text,newline="")))
    if not rows:
        raise ValueError("Empty CSV")
    columns=list(rows[0])
    if len(columns)!=len(set(columns)) or len(columns)<5:
        raise ValueError("Duplicate or unexpected number of CSV columns")
    if any(not isinstance(k,str) or not k.strip() or len(k)>120 for k in columns):
        raise ValueError("Malformed CSV headers")
    if len(rows)!=expected_count:
        raise ValueError("Unexpected source record count; review version before any ingest")
    if any(any(k not in columns for k in r) or None in r for r in rows):
        raise ValueError("Malformed ragged source row")
    if len(rows)>10000:raise ValueError("Source row limit exceeded")
    source_country=[k for k in columns if k in CANON_COUNTRY]
    if len(source_country)>1:
        raise ValueError("Ambiguous country fields; do not infer geography")
    country_field=source_country[0] if source_country else None
    values=Counter()
    nigeria=0
    if country_field:
        for row in rows:
            val=str(row.get(country_field) or "").strip()
            values[val if val else "MISSING"]+=1
            if val.lower() in NIGERIA:nigeria+=1
    return {
        "status":"CHECKSUM_VERIFIED_COUNTRY_REVIEW_REQUIRED"
                 if not country_field else "CHECKSUM_VERIFIED_COUNTRY_FIELD_DETECTED",
        "dataset_doi":SOURCE_DOI,
        "source_file_doi":CSV_DOI,
        "license":"CC BY 4.0",
        "publisher_md5":expected_md5,
        "computed_md5":md5,
        "source_records":len(rows),
        "column_names":columns,
        "country_field":country_field,
        "country_values_distinct":len(values) if country_field else None,
        "nigeria_source_country_rows":nigeria if country_field else None,
        "country_label_validation_required":True,
        "coordinate_reference_and_point_accuracy_review_required":True,
        "catchment_overlay_performed":False,
        "individual_source_records_released":0,
        "exact_positions_released":0,
        "stakeholder_crossmatches_performed":False,
        "publication_decision":"HOLD_FOR_GEOGRAPHIC_AND_SOURCE_QA",
        "limitations":"Publisher checksum and raw country label only. Does not verify dam identity, coordinate accuracy, source independence, operating status or Nigerian catchment overlap."
    }

def main():
    parser=argparse.ArgumentParser()
    mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--fetch",action="store_true",help="Fetch registered Dataverse datafile")
    mode.add_argument("--source-csv",type=Path,help="Previously downloaded unmodified source CSV")
    parser.add_argument("--report",type=Path,required=True)
    args=parser.parse_args()
    data=fetch_pinned() if args.fetch else args.source_csv.read_bytes()
    result=preflight(data)
    # Reports contain only aggregate QA; do not include the source CSV in artifacts.
    if args.report.exists():raise SystemExit("Review report already exists; refusing overwrite")
    args.report.parent.mkdir(parents=True,exist_ok=True)
    with args.report.open("x",encoding="utf-8") as handle:
        json.dump(result,handle,indent=2,ensure_ascii=False)
        handle.write("\n")
    print("WEST AFRICA DAMS SOURCE PREFLIGHT:",result["status"],
          "rows",result["source_records"],"country_column",result["country_field"],
          "Nigerian_country_rows",result["nigeria_source_country_rows"],
          "PUBLIC_RECORDS",result["individual_source_records_released"])

if __name__=="__main__":
    main()
