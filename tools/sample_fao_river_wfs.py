#!/usr/bin/env python3
"""Read-only FAO AQUASTAT WFS sample before full river-network ingestion."""
import json, requests
from pathlib import Path
root=Path(__file__).resolve().parents[1]
out=root/'review/fao-river-sample';out.mkdir(parents=True,exist_ok=True)
url='https://data.apps.fao.org/map/gsrv/gsrv1/aquamaps/wfs'
bbox='4,7,14,15,EPSG:4326'
report={'status':'SAMPLE_ONLY','service':url,'sample_bbox':bbox,'layers':[]}
for typename in ('aquamaps:river_network','aquamaps:rivers_africa_37333'):
 for version in ('1.0.0','1.1.0'):
  params={'service':'WFS','version':version,'request':'GetFeature','typeName':typename,'outputFormat':'application/json','srsName':'EPSG:4326','bbox':bbox,'maxFeatures':4}
  row={'layer':typename,'version':version}
  try:
   r=requests.get(url,params=params,timeout=(15,85),headers={'User-Agent':'BasinNexusNG/FAORiverSample'})
   row.update({'status_code':r.status_code,'bytes':len(r.content),'media':r.headers.get('content-type')})
   if r.ok and len(r.content)<3000000 and r.text.lstrip().startswith('{'):
    d=r.json()
    feats=d.get('features') or []
    row['result_type']=d.get('type');row['features_returned']=len(feats)
    row['total_info']={k:d.get(k) for k in ['totalFeatures','numberMatched','numberReturned'] if k in d}
    if feats:
      f=feats[0];row['first_geometry_type']=f.get('geometry',{}).get('type');row['first_geometry_coordinates_preview']=str(f.get('geometry',{}).get('coordinates'))[:160]
      row['property_names']=list(f.get('properties',{}));row['property_sample']={k:str(v)[:90] for k,v in f.get('properties',{}).items()}
   else:row['response_preview']=r.text[:300]
  except Exception as exc:row['error']=str(exc)[:220]
  report['layers'].append(row)
  print(json.dumps(row,ensure_ascii=False))
(out/'small_wfs_query.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
print('FAO RIVER WFS SAMPLE COMPLETE — no atlas geometry changed')
