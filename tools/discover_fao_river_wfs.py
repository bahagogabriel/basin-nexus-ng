#!/usr/bin/env python3
"""Discover whether FAO AQUASTAT Rivers 2026 (CC-BY 4.0) offers vector WFS.

Only reads public OGC service capabilities; never retrieves bulk source geometry.
A positive discovery is not yet approval for public per-catchment linework.
"""
from pathlib import Path
import json
from datetime import datetime,timezone
import requests
from lxml import etree

BASE='https://data.apps.fao.org/map/gsrv/gsrv1/aquamaps/'
OUT=Path(__file__).resolve().parents[1]/'review/fao-rivers-capabilities'
DATASET='https://data.fao.org/catalog/dataset/e22667af-3977-4e9f-b58b-67fb91b0fa87'
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    report={'status':'DISCOVERY_ONLY','source':DATASET,'license_as_listed':'CC BY 4.0',
            'checked_utc':datetime.now(timezone.utc).isoformat(),
            'request_limit':'Capabilities only, no full geometries',
            'services':[]}
    for endpoint in ('wfs','ows'):
        url=BASE+endpoint
        params={'service':'WFS','version':'1.1.0','request':'GetCapabilities'}
        item={'url':url,'parameters':params}
        try:
            r=requests.get(url,params=params,timeout=(15,60),headers={'User-Agent':'BasinNexusNG/HydroDataDiscovery'})
            item['http_code']=r.status_code
            item['response_bytes']=len(r.content)
            item['content_type']=r.headers.get('Content-Type','')
            if r.ok and len(r.content)<15_000_000:
                root=etree.fromstring(r.content)
                names=[e.text for e in root.xpath('//*[local-name()="FeatureType"]/*[local-name()="Name"]') if e.text]
                item['published_feature_types']=len(names)
                item['river_candidates']=[x for x in names if 'river' in x.lower() or 'hydro' in x.lower()][:50]
            else:
                item['message']='Service unavailable or capabilities response too large'
        except Exception as e:item['error']=str(e)[:250]
        report['services'].append(item)
        if item.get('river_candidates'):report['status']='POSSIBLE_RIVER_WFS_FOUND'
    (OUT/'fao_wfs_discovery.json').write_text(json.dumps(report,indent=2)+'\n','utf-8')
    print(json.dumps(report,indent=2))
    print('DISCOVERY ONLY — NO GEOGRAPHIC LINES ADDED TO PUBLIC ATLAS')
if __name__=='__main__':main()
