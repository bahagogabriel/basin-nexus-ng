#!/usr/bin/env python3
"""Create public visualisation-only geometry from owner-supplied reviewed catchments.
No stakeholder evidence is exported. Source GPKG remains untouched.
"""
from pathlib import Path
import json, csv, hashlib, argparse
import geopandas as gpd
from shapely.validation import explain_validity

HERE=Path(__file__).resolve().parent.parent
DEFAULT=Path('/mnt/data/SCMP_20_Catchments_Validated.gpkg')

def build(source:Path, out:Path, tolerance_m=300):
    g=gpd.read_file(source)
    assert len(g)==20 and g['CatchID'].nunique()==20
    g=g.to_crs('EPSG:6933')
    original={i:float(x.area) for i,x in zip(g.CatchID,g.geometry)}
    # topology-preserving, display-only simplification in metric projection
    g['geometry']=g.geometry.simplify(tolerance_m,preserve_topology=True)
    area_delta={str(i):abs((x.area/original[i])-1)*100 for i,x in zip(g.CatchID,g.geometry)}
    assert max(area_delta.values()) < 1.5, max(area_delta.values())
    assert all(x.is_valid and not x.is_empty for x in g.geometry), [explain_validity(x) for x in g.geometry if not x.is_valid]
    g=g.to_crs('EPSG:4326')
    features=[]
    records=[]
    for r in g.itertuples():
        props={'id':r.CatchID,'name':r.Name,'slug':r.Slug,'historical_alias':r.Alias or '',
               'area_km2':round(float(r.Area_km2),1),'label_lon':round(float(r.LabelLon),6),
               'label_lat':round(float(r.LabelLat),6)}
        features.append({'type':'Feature','properties':props,'geometry':r.geometry.__geo_interface__})
        records.append(props)
    obj={'type':'FeatureCollection','features':features}
    out.mkdir(parents=True, exist_ok=True)
    (out/'catchments.geojson').write_text(json.dumps(obj,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    (out/'registry.json').write_text(json.dumps(records,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    with (out/'catchments.csv').open('w',newline='',encoding='utf-8') as fh:
        writer=csv.DictWriter(fh,fieldnames=records[0].keys());writer.writeheader();writer.writerows(records)
    report={'count':len(records),'source':'Owner-supplied 20 catchment polygons (repaired working copy)',
            'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
            'display_geometry_tolerance_m':tolerance_m,'max_simplification_area_delta_pct':round(max(area_delta.values()),6),
            'aggregate_simplification_area_delta_pct':round(abs(sum(x.area for x in g.to_crs('EPSG:6933').geometry)/sum(original.values())-1)*100,5),
            'public_data_scope':'only boundary names, geometry, ids, calculated areas and old alias; no stakeholder text or source Drive URLs',
            'area_method':'EPSG:6933 equal-area calculation stored in original registry (km2)',
            'caution':'Not an independent approval of boundary accuracy; validation and licensing review pending'}
    (out/'build_report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2));return report

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,default=DEFAULT);p.add_argument('--output',type=Path,default=HERE/'site'/'data');p.add_argument('--tolerance-m',type=float,default=300)
    a=p.parse_args();build(a.source,a.output,a.tolerance_m)
