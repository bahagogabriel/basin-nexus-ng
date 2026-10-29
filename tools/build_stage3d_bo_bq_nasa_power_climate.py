#!/usr/bin/env python3
"""NASA POWER 2005–2025 monthly point climate: 20 SCMP map-label locations.

Fetch (once) with bounded parallelism; preserve exact NASA replies in research/.
Rebuild 20 public climatology/annual series and compact integrated register from
the pinned replies with NO remote service required at Pages deploy time.

NASA POWER POWER monthly precipitation PRECTOTCORR is the modeled mean
DAILY rate in mm/day. Monthly accumulated estimate = rate * calendar days.
T2M is a modeled 2-meter daily average temperature in Celsius. Weighted
annual means and 21-year climatologies below are point samples, NOT catchment
area-weighted values or station observations.
"""
from __future__ import annotations
import argparse,calendar,csv,hashlib,io,json,math,time
from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request,urlopen

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"site/data"
SNAP=ROOT/"research/nasa_power_monthly_2005_2025"
API="https://power.larc.nasa.gov/api/temporal/monthly/point"
START,END=2005,2025
VARS=("PRECTOTCORR","T2M")
SCHEMA="BN_STAGE3D_BO_POWER_LABEL_POINT_CLIMATE_2005_2025_V1"
REGISTER_SCHEMA="BN_STAGE3D_BQ_UNIFIED_CATCHMENT_REGISTER_2005_2025_V1"
FIELDS=("catchment_id","catchment_name","area_km2","label_lon","label_lat",
        "provisional_state_intersections","provisional_lga_intersections",
        "fao_2026_clipped_reaches","nasa_power_mean_annual_precip_mm_2005_2025",
        "nasa_power_precip_mm_2025","nasa_power_mean_temp_c_2005_2025",
        "nasa_power_mean_temp_c_2025","nasa_power_wettest_month_number",
        "nasa_power_driest_month_number","climate_spatial_basis")
MISSING=-900.0

def registry():
    rows=json.loads((DATA/"registry.json").read_text("utf-8"))
    if len(rows)!=20 or set(x["id"] for x in rows)!={f"SCMP-C{i:02d}" for i in range(1,21)}:
        raise ValueError("Original 20 catchment register identity changed")
    return rows

def api_url(r):
    return API+"?"+urlencode({"parameters":",".join(VARS),"community":"AG",
       "latitude":str(r["label_lat"]),"longitude":str(r["label_lon"]),
       "start":START,"end":END,"format":"JSON"})

def get_live(row, max_attempts=3):
    url=api_url(row)
    for n in range(max_attempts):
        try:
            req=Request(url,headers={"User-Agent":"BasinNexusNG-NASA-POWER-climate/1.0",
                                     "Accept":"application/json"})
            with urlopen(req,timeout=100) as res:
                blob=res.read(1_000_000+1)
            if len(blob)>1_000_000:raise ValueError("NASA response exceeds permitted source bytes")
            data=json.loads(blob)
            validate_reply(data,row)
            return row["id"],json.dumps(data,ensure_ascii=True,sort_keys=True,separators=(",",":")).encode("utf-8")
        except (OSError,ValueError) as e:
            if n==max_attempts-1:raise RuntimeError(f"NASA POWER source unavailable for {row['id']}: {e}")
            time.sleep(1.5*(n+1))
    raise AssertionError("unreachable")

def _params(data):
    if data.get("type")=="Feature" and isinstance(data.get("properties"),dict):
        return data["properties"].get("parameter")
    return data.get("properties",{}).get("parameter")

def validate_reply(data,row):
    if not isinstance(data,dict) or data.get("type")!="Feature":
        raise ValueError("Unexpected NASA POWER response type")
    geometry=data.get("geometry") or {}
    pt=geometry.get("coordinates")
    if (geometry.get("type")!="Point" or not isinstance(pt,list)
        or len(pt)<2 or any(type(v) not in (float,int) or not math.isfinite(v) for v in pt[:2])
        or abs(pt[0]-row["label_lon"])>1.5 or abs(pt[1]-row["label_lat"])>1.5):
        raise ValueError("NASA POWER point location is not the requested catchment representative location")
    props=_params(data)
    if not isinstance(props,dict) or not all(isinstance(props.get(v),dict) for v in VARS):
        raise ValueError("NASA POWER monthly climate variables unavailable")
    info=data.get("parameters") or {}
    if info:
        unit_r=str((info.get("PRECTOTCORR") or {}).get("units","")).replace(" ","").lower()
        unit_t=str((info.get("T2M") or {}).get("units","")).replace(" ","").lower()
        if unit_r not in ("mm/day","mm/d","mm/day-1","mmday-1") or unit_t not in ("c","°c","degc"):
            raise ValueError("NASA POWER monthly variable units changed: "+str((unit_r,unit_t)))
    for y in range(START,END+1):
        for m in range(1,13):
            key=f"{y}{m:02d}"
            for parameter in VARS:
                val=props[parameter].get(key)
                if type(val) not in (int,float) or not math.isfinite(val) or val<=MISSING:
                    raise ValueError(f"NASA POWER missing/invalid complete monthly source value {row['id']} {parameter} {key}: {val}")
                if parameter=="PRECTOTCORR" and not 0<=val<200:
                    raise ValueError("Unreasonable daily modeled rain rate at point")
                if parameter=="T2M" and not -40<val<60:
                    raise ValueError("Unreasonable modeled monthly temperature")
    return True

def make_climate(rows,snapshot_dir):
    by=[]
    for row in rows:
        path=snapshot_dir/(row["id"]+".json")
        raw=path.read_bytes()
        if len(raw)>1_000_000:raise ValueError("Source snapshot exceeds bounded size")
        data=json.loads(raw)
        validate_reply(data,row)
        values=_params(data)
        annual=[];monthly_tot=[0.0]*12;monthly_temp=[0.0]*12
        for year in range(START,END+1):
            rains=[];temps=[];days=[]
            for month in range(1,13):
                key=f"{year}{month:02d}"
                n=calendar.monthrange(year,month)[1]
                rain=float(values["PRECTOTCORR"][key])*n
                temp=float(values["T2M"][key])
                rains.append(rain);temps.append(temp);days.append(n)
                monthly_tot[month-1]+=rain
                monthly_temp[month-1]+=temp
            annual.append({"year":year,"precip_mm":round(sum(rains),1),
                           "mean_t2m_c":round(sum(t*d for t,d in zip(temps,days))/sum(days),2)})
        climate_monthly=[{"month":m,"mean_monthly_precip_mm":round(monthly_tot[m-1]/(END-START+1),1),
                          "mean_t2m_c":round(monthly_temp[m-1]/(END-START+1),2)}
                         for m in range(1,13)]
        avg_rain=round(sum(z["precip_mm"] for z in annual)/len(annual),1)
        avg_temp=round(sum(z["mean_t2m_c"] for z in annual)/len(annual),2)
        wet=max(climate_monthly,key=lambda z:z["mean_monthly_precip_mm"])["month"]
        dry=min(climate_monthly,key=lambda z:z["mean_monthly_precip_mm"])["month"]
        by.append({"catchment_id":row["id"],"catchment_name":row["name"],
                   "sample_lon":row["label_lon"],"sample_lat":row["label_lat"],
                   "nasa_power_snapshot_sha256":hashlib.sha256(raw).hexdigest(),
                   "source_api_url":api_url(row),
                   "mean_annual_precip_mm_2005_2025":avg_rain,
                   "mean_t2m_c_2005_2025":avg_temp,
                   "recent_2025":annual[-1],"wettest_mean_precip_month":wet,
                   "driest_mean_precip_month":dry,
                   "monthly_climatology":climate_monthly,"annual":annual})
    result={"schema_version":SCHEMA,
       "data_status":"NASA_POWER_MODELED_POINT_SAMPLE_NOT_CATCHMENT_MEAN",
       "dataset":"NASA POWER monthly/annual point API, Agroclimatology community",
       "source":"https://power.larc.nasa.gov/docs/services/api/temporal/monthly/",
       "precipitation_variable":"PRECTOTCORR",
       "precipitation_method":"Monthly NASA POWER modeled daily precipitation rate (mm/day) multiplied by calendar days and summed for year; not catchment zonal precipitation",
       "temperature_variable":"T2M",
       "temperature_method":"Day-count weighted mean of NASA POWER monthly modeled two-meter air temperatures, degrees Celsius",
       "sample_basis":"Existing SCMP catchment registry map-label longitude/latitude; sample grid values are NOT catchment-averaged raster statistics",
       "period_start":START,"period_end":END,
       "catchment_point_count":20,"records":by,
       "source_limits":[
          "Point climate samples at SCMP map-label locations are not spatially representative averages of whole watersheds, particularly for large and transboundary catchments.",
          "NASA POWER uses modeled/reanalysis meteorological grids and must not be described as measured gauge rainfall or a station temperature observation.",
          "Monthly precipitation source units are a daily mean rate; multiplying by calendar days creates an approximate annual mm total at the selected point.",
          "Climate values must not be used to estimate river discharge, flood risk, dam safety or irrigation demand without independent, scale-appropriate analysis.",
          "Original NASA responses for 20 source points are preserved under research/nasa_power_monthly_2005_2025 and source hashes are in each record."
        ]}
    return result

def integrated(climate, rows):
    meta=json.loads((DATA/"detailed_river_manifest.json").read_text("utf-8"))
    admin=json.loads((DATA/"admin_crosswalk_provisional.json").read_text("utf-8"))
    by={r["catchment_id"]:r for r in climate["records"]}
    result=[]
    for row in rows:
        cid=row["id"];c=by[cid]
        result.append({
          "catchment_id":cid,"catchment_name":row["name"],"area_km2":row["area_km2"],
          "label_lon":row["label_lon"],"label_lat":row["label_lat"],
          "provisional_state_intersections":len(admin["byCatchment"][cid]["states"]),
          "provisional_lga_intersections":len(admin["byCatchment"][cid]["lgas"]),
          "fao_2026_clipped_reaches":meta["files"][cid]["count"],
          "nasa_power_mean_annual_precip_mm_2005_2025":c["mean_annual_precip_mm_2005_2025"],
          "nasa_power_precip_mm_2025":c["recent_2025"]["precip_mm"],
          "nasa_power_mean_temp_c_2005_2025":c["mean_t2m_c_2005_2025"],
          "nasa_power_mean_temp_c_2025":c["recent_2025"]["mean_t2m_c"],
          "nasa_power_wettest_month_number":c["wettest_mean_precip_month"],
          "nasa_power_driest_month_number":c["driest_mean_precip_month"],
          "climate_spatial_basis":"NASA_POWER_MAP_LABEL_POINT_NOT_CATCHMENT_MEAN"
        })
    summary={"schema_version":REGISTER_SCHEMA,
      "status":"MULTI_SOURCE_EXPLORATORY_POINT_CLIMATE_AND_MODELLED_RIVERS",
      "source_climate_sha256":hashlib.sha256(json.dumps(climate,sort_keys=True,separators=(",",":")).encode()).hexdigest(),
      "catchment_count":20,
      "caveats":"Study polygon area and administrative polygon intersections are provisional; FAO river reaches are clipped modeled records, and NASA climate is a point sample (NOT catchment average).",
      "rows":result}
    return summary

def csv_text(register):
    o=io.StringIO(newline="")
    writer=csv.DictWriter(o,fieldnames=FIELDS,lineterminator="\n")
    writer.writeheader()
    for r in register["rows"]:writer.writerow(r)
    return o.getvalue()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--fetch",action="store_true")
    ap.add_argument("--snapshots",type=Path,default=SNAP)
    ap.add_argument("--output",type=Path,default=DATA)
    ap.add_argument("--check",action="store_true")
    args=ap.parse_args()
    rows=registry()
    if args.fetch:
        if args.snapshots.exists():raise SystemExit("Refusing to overwrite existing NASA POWER source snapshots")
        args.snapshots.mkdir(parents=True)
        with ThreadPoolExecutor(max_workers=3) as pool:
            tasks={pool.submit(get_live,row):row["id"] for row in rows}
            for f in as_completed(tasks):
                cid,blob=f.result()
                (args.snapshots/(cid+".json")).write_bytes(blob)
                print("NASA POWER original 2005-2025",cid,"bytes",len(blob),flush=True)
        if len(list(args.snapshots.glob("SCMP-C*.json")))!=20:
            raise ValueError("NASA POWER 20 source observations incomplete")
    climate=make_climate(rows,args.snapshots)
    reg=integrated(climate,rows)
    outcl=args.output/"nasa_power_20_catchment_point_climate_2005_2025.json"
    outreg=args.output/"integrated_catchment_indicator_register.json"
    outcsv=args.output/"integrated_catchment_indicator_register.csv"
    if args.check:
        if (json.loads(outcl.read_text("utf-8"))!=climate
          or json.loads(outreg.read_text("utf-8"))!=reg
          or outcsv.read_text("utf-8")!=csv_text(reg)):
            raise ValueError("Published NASA model climate or integrated catchment register drift")
    else:
        args.output.mkdir(parents=True,exist_ok=True)
        outcl.write_text(json.dumps(climate,indent=2,ensure_ascii=False)+"\n","utf-8")
        outreg.write_text(json.dumps(reg,indent=2,ensure_ascii=False)+"\n","utf-8")
        outcsv.write_text(csv_text(reg),"utf-8")
    print("NASA POWER modeled POINT climate 20 catchments, 2005-2025 inclusive; 20-year+ annual series; original observations retained. Register",len(reg["rows"]))
if __name__=="__main__":main()
