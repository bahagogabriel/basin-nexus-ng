#!/usr/bin/env python3
"""Non-public preflight only: can 1:10m Natural Earth hydro improve the atlas?

Uses the existing validated selection pipeline to collect counts, candidate
river/lake names, output sizes, degenerate-source QA. Results remain under
review and cannot be auto-promoted to the public Pages site.
"""
from pathlib import Path
import json, hashlib
from shapely.geometry import shape
from shapely.ops import transform, unary_union
import build_hydro_reference as base

P=Path(__file__).resolve().parents[1]
OUT=P/'review'/'hydro10m-preflight'
REF=base.SOURCE_REF
ORIGIN=f'https://raw.githubusercontent.com/nvkelso/natural-earth-vector/{REF}/geojson/'
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    catch=json.loads((P/'site/data/catchments.geojson').read_text())
    area=unary_union([transform(base.FORWARD,shape(f['geometry'])) for f in catch['features']]).buffer(20000)
    meta={'publication':'HOLD_ONLY','scale':'1:10m','source':'Natural Earth (public domain)','source_commit':REF,
      'catchment_count':len(catch['features']),'note':'No public output; sourced world features may be incomplete and names are not infrastructure coordinates'}
    for kind in ('river','lake'):
        url=ORIGIN+('ne_10m_rivers_lake_centerlines.geojson' if kind=='river' else 'ne_10m_lakes.geojson')
        data,sha=base.source_json(url)
        fc,qa=base.process(kind,data['features'],area)
        names=sorted({f['properties']['name'] for f in fc['features'] if f['properties']['name']})
        # Explicitly *exclude* these QA-only geometries from the public site.
        result=OUT/f'{kind}s_candidate_NE10_review.geojson'
        result.write_text(json.dumps(fc,separators=(',',':'))+'\n')
        meta[kind]={'url':url,'hash':sha,'world_count':len(data['features']),
          'candidate_count':len(fc['features']),'bytes':result.stat().st_size,
          'named_count':len(names),'examples':names[:80],'source_geometry_qa':qa}
    (OUT/'preflight_summary.json').write_text(json.dumps(meta,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps(meta,indent=2,ensure_ascii=False))
    print('NE10 HYDRO DATA PREFLIGHT COMPLETE — NOT PUBLIC')
if __name__=='__main__':main()
