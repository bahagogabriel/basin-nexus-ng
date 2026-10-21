#!/usr/bin/env python3
"""Build per-catchment detailed rivers using FAO AQUASTAT Rivers (2026).

FAO metadata: CC BY 4.0 (2026-06-15), dataset ID e22667af-3977-4e9f-b58b-67fb91b0fa87.
Retrieval: GeoServer WFS aquamaps:river_network with a bounded geographic query
and stable, verified pagination. No naming or cartographic river class is invented.
Geometry clips to user-supplied catchments for display; cross-catchment topology
is retained by the original HYRIV_ID, NEXT_DOWN and MAIN_RIV fields.

Do not publish if coverage, paging, geometry, size, metadata or source QA fails.
"""
from pathlib import Path
from collections import Counter,defaultdict
import hashlib
import json
import math
import time
import requests
from shapely.geometry import shape, mapping, LineString, MultiLineString
from shapely.ops import unary_union
from shapely.strtree import STRtree

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'site/data'
OUT=ROOT/'review/fao-detailed-rivers'
STORE=OUT/'river_network'
BASE='https://data.apps.fao.org/map/gsrv/gsrv1/aquamaps/wfs'
SOURCE='https://data.fao.org/catalog/dataset/e22667af-3977-4e9f-b58b-67fb91b0fa87'
PAGE=1750
MIN_EXPECTED=10000
MAX_EXPECTED=250000
MAX_SINGLE_FILE_BYTES=9_000_000
TIMEOUT=(20,125)

def fetch(session,params):
    for attempt in range(4):
        try:
            r=session.get(BASE,params=params,timeout=TIMEOUT)
            if r.status_code in (429,502,503,504):
                time.sleep((attempt+1)*3)
                continue
            r.raise_for_status()
            if 'json' not in r.headers.get('content-type','').lower() and not r.text.lstrip().startswith('{'):
                raise ValueError('WFS returned non-JSON response: '+r.text[:300])
            d=r.json()
            if d.get('type')!='FeatureCollection':
                raise ValueError('WFS did not return GeoJSON FeatureCollection')
            return d
        except (requests.RequestException,ValueError):
            if attempt==3:raise
            time.sleep((attempt+1)*2)
    raise RuntimeError('Exceeded WFS retries')

def safe_line(g):
    if g.is_empty:return None
    if g.geom_type in ('LineString','MultiLineString'):
        return g if g.length>0 else None
    lines=[x for x in getattr(g,'geoms',[]) if x.geom_type in ('LineString','MultiLineString') and x.length>0]
    if not lines:return None
    united=unary_union(lines)
    return united if united.geom_type in ('LineString','MultiLineString') else None

def num(p,key,allow_none=True):
    n=p.get(key)
    if n in ('',None):return None if allow_none else 0
    v=float(n)
    if not math.isfinite(v):raise ValueError('Non-finite '+key)
    return v

def main():
    STORE.mkdir(parents=True,exist_ok=True)
    atlas=json.loads((DATA/'catchments.geojson').read_text('utf-8'))
    names={f['properties']['id']:f['properties']['name'] for f in atlas['features']}
    assert len(names)==20
    polys=[shape(f['geometry']) for f in atlas['features']]
    assert all(p.is_valid and not p.is_empty for p in polys)
    bbox=[min(g.bounds[0] for g in polys)-.15,min(g.bounds[1] for g in polys)-.15,
          max(g.bounds[2] for g in polys)+.15,max(g.bounds[3] for g in polys)+.15]
    ids=list(names)
    tree=STRtree(polys)
    if not 0<bbox[0]<bbox[2]<20 or not 0<bbox[1]<bbox[3]<20:
        raise ValueError('Unexpected geographic input extent')
    bbox_arg=','.join(str(round(x,6)) for x in bbox)+',EPSG:4326'
    prepared={cid:[] for cid in ids}
    count_by_class={cid:Counter() for cid in ids}
    obs=set();errors=[];matched=set();pages=0;total=None;seen=0
    session=requests.Session();session.headers.update({'User-Agent':'BasinNexusNG/FAO-AQUASTAT2026-CCBY4-AtlasQA/1.0'})
    while True:
        query={'service':'WFS','version':'1.1.0','request':'GetFeature','typeName':'aquamaps:river_network',
            'bbox':bbox_arg,'outputFormat':'application/json','srsName':'EPSG:4326',
            'sortBy':'hyriv_id','startIndex':seen,'maxFeatures':PAGE}
        response=fetch(session,query)
        features=response.get('features') or []
        n=int(response.get('totalFeatures') or response.get('numberMatched') or 0)
        if total is None:
            total=n
            assert MIN_EXPECTED<=total<=MAX_EXPECTED,('Unexpected WFS result size',total)
        elif n and total!=n:
            raise ValueError('FAO WFS totalFeatures changed while paginating')
        if not features:break
        if len(features)>PAGE:raise ValueError('Page exceeds requested limit')
        for f in features:
            p=f.get('properties') or {}
            fid=p.get('hyriv_id')
            if fid is None:raise ValueError('No source HYRIV_ID')
            fid=str(int(fid))
            if fid in obs:raise ValueError('Pagination reused HYRIV_ID '+fid)
            obs.add(fid)
            geometry=f.get('geometry')
            if geometry is None:errors.append(['missing geometry',fid]);continue
            g=safe_line(shape(geometry))
            if g is None:errors.append(['empty geometry',fid]);continue
            hits=tree.query(g,predicate='intersects')
            if not len(hits):continue
            matched.add(fid)
            for ix in hits:
                i=int(ix);cid=ids[i]
                intersected=safe_line(g.intersection(polys[i]))
                if intersected is None:continue
                order=num(p,'ord_flow')
                upland=num(p,'upland_skm')
                if upland is not None and upland<0:raise ValueError('Negative upstream area')
                props={'id':cid+'_'+fid,'hyriv_id':fid,
                    'next_down':str(int(p['next_down'])) if p.get('next_down') is not None else None,
                    'main_riv':str(int(p['main_riv'])) if p.get('main_riv') is not None else None,
                    'ord_flow':int(order) if order is not None else None,
                    'upland_skm':round(upland,3) if upland is not None else None,
                    'dis_av_cms':num(p,'dis_av_cms'),
                    'length_km_source':num(p,'length_km'),
                    'flow_regime_code':p.get('smooth_100') if p.get('smooth_100') in ('P','I') else None,
                    'name':None,'source':'FAO AQUASTAT 2026 river network',
                    'source_license':'CC BY 4.0','location_precision':'modeled_15_arcsec',
                    'is_clipped_to_catchment':True}
                cls=('large_upstream_1000plus' if upland is not None and upland>=1000 else
                     'medium_upstream_100plus' if upland is not None and upland>=100 else
                     'small_upstream_below100')
                props['upstream_class']=cls
                render=intersected.simplify(0.00012,preserve_topology=True)
                if render.is_empty or render.geom_type not in ('LineString','MultiLineString'):render=intersected
                prepared[cid].append({'type':'Feature','properties':props,'geometry':mapping(render)})
                count_by_class[cid][cls]+=1
        seen+=len(features);pages+=1
        print('WFS PAGE',pages,'fetched',seen,'of',total,flush=True)
        if len(features)<PAGE:break
        if seen>=total:break
        if pages>180:raise ValueError('Exceeded expected paging horizon')
        time.sleep(.08)
    if seen!=total:raise ValueError(f'Pagination completeness mismatch: fetched {seen}, expected {total}')
    if len(errors)>max(10,total*.002):raise ValueError('Too many invalid source geometries')
    if len(matched)<MIN_EXPECTED*.45:raise ValueError('Unexpectedly low river coverage after clip')
    if any(len(v)==0 for v in prepared.values()):raise ValueError('One or more catchments have zero river reaches in detailed source')
    manifest={'status':'PROVISIONAL_DETAILED_RIVER_NETWORK','license':'CC BY 4.0 (FAO AQUASTAT)',
        'source':SOURCE,'source_wfs':BASE,'layer':'aquamaps:river_network','version':'2026-06-15',
        'derived_from':'HydroRIVERS 15-arcsecond modeled network',
        'source_note':'Modelled river reaches; smaller streams may be missing. A reach generally qualifies at >=10 km2 drainage or >=0.1 m3/s average flow.',
        'catchment_source':'user supplied and verified 20 catchments, simplified for web',
        'source_catchment_sha256':hashlib.sha256((DATA/'catchments.geojson').read_bytes()).hexdigest(),
        'bbox_wgs84':bbox,'bbox_candidate_count':total,'page_size':PAGE,'pages':pages,
        'source_unique_ids':len(obs),'source_intersecting_unique_reaches':len(matched),
        'source_geometry_warnings':errors[:20],
        'display_units':'Individual clipped river reaches, not independently surveyed rivers',
        'hierarchy_method':'upstream drainage area: >=1000, >=100, <100 square kilometres',
        'topology_warning':'NEXT_DOWN and MAIN_RIV are original source IDs; clips and catchment boundaries can separate connected reaches.',
        'files':{},'total_display_reaches':0}
    for cid in ids:
        fc={'type':'FeatureCollection','name':'Basin_Nexus_detailed_rivers_'+cid,
            'properties':{'catchment_id':cid,'catchment':names[cid],'data_status':'provisional'},
            'features':prepared[cid]}
        file=STORE/(cid+'.geojson')
        raw=(json.dumps(fc,ensure_ascii=False,separators=(',',':'))+'\n').encode()
        if len(raw)>MAX_SINGLE_FILE_BYTES:raise ValueError(cid+' exceeds safe tablet payload size')
        file.write_bytes(raw)
        manifest['files'][cid]={'name':names[cid],'file':'river_network/'+cid+'.geojson',
            'count':len(prepared[cid]),'bytes':len(raw),
            'sha256':hashlib.sha256(raw).hexdigest(),'classes':dict(count_by_class[cid])}
        manifest['total_display_reaches']+=len(prepared[cid])
    (OUT/'detailed_river_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n','utf-8')
    print('FAO DETAIL QA PASS:',total,'WFS candidates;',len(matched),'source reaches intersect; 20 catchment files')
    for cid in ids:print(cid,names[cid],manifest['files'][cid]['count'],'reaches',manifest['files'][cid]['bytes'],'bytes')
    print('FAO CC BY 4.0, network modeled at 15arcsec; no source river names inferred')
if __name__=='__main__':main()
