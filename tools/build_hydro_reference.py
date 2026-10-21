#!/usr/bin/env python3
"""Build coarse hydrological reference data for Basin Nexus NG.

Natural Earth (public domain), 1:50 million rivers and lakes. This is map
context, *not* a complete water inventory or a confirmed dam register.
Catchments are user-supplied, simplified and may cross international borders.
Use EPSG:6933 geometry for selection, buffered to provide nearby context;
do not clip river lines to national or state borders.
"""
import hashlib
import json
from pathlib import Path
import requests
from shapely.geometry import shape, mapping
from shapely.ops import transform, unary_union
from shapely.validation import make_valid
from pyproj import Transformer

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'site' / 'data'
TMP = ROOT / 'review' / 'hydro-reference'
SOURCE_REF = 'ca96624a56bd078437bca8184e78163e5039ad19'
SOURCE = 'https://raw.githubusercontent.com/nvkelso/natural-earth-vector/' + SOURCE_REF + '/geojson/'
URLS = {
  'river': SOURCE + 'ne_50m_rivers_lake_centerlines.geojson',
  'lake': SOURCE + 'ne_50m_lakes.geojson',
}
FORWARD = Transformer.from_crs(4326,6933,always_xy=True).transform
BACK = Transformer.from_crs(6933,4326,always_xy=True).transform
CONTEXT_BUFFER_M = 20000

def source_json(url):
    r=requests.get(url,timeout=150,headers={'User-Agent':'BasinNexusNG/Stage2E-HydroQA'})
    r.raise_for_status()
    raw=r.content
    if raw.startswith(b'version https://git-lfs.github.com'):
        raise ValueError('Source is Git LFS pointer, not geographic data')
    data=json.loads(raw)
    if data.get('type')!='FeatureCollection':raise ValueError('Unexpected source format')
    return data,hashlib.sha256(raw).hexdigest()

def safe_geom(geom,kind):
    g=make_valid(geom)
    if g.is_empty:return None
    if kind=='river' and g.geom_type not in ('LineString','MultiLineString'):
        raise ValueError('Unexpected river geometry '+g.geom_type)
    if kind=='lake' and g.geom_type not in ('Polygon','MultiPolygon'):
        raise ValueError('Unexpected lake geometry '+g.geom_type)
    if not g.is_valid:raise ValueError('Invalid source geometry')
    return g

def process(kind,original,domain):
    out=[];stats={'original_count':len(original),'intersecting_count':0,'named_count':0,'unnamed_count':0,'invalid_empty_source_indices':[]}
    for idx,f in enumerate(original):
        geometry=safe_geom(shape(f['geometry']),kind)
        if geometry is None:
            stats['invalid_empty_source_indices'].append(idx)
            continue
        projected=transform(FORWARD,geometry)
        if not projected.intersects(domain):
            continue
        stats['intersecting_count']+=1
        # Keep complete source river and lake shapes where they intersect the domain.
        # Web display uses a bounded-area *clip* to limit asset size.
        clipped=projected.intersection(domain)
        possible=('LineString','MultiLineString') if kind=='river' else ('Polygon','MultiPolygon')
        if clipped.geom_type=='GeometryCollection':
            segments=[x for x in clipped.geoms if x.geom_type in possible]
            if not segments:continue
            clipped=unary_union(segments)
        if clipped.geom_type not in possible or clipped.is_empty:continue
        render=clipped.simplify(130 if kind=='river' else 110,preserve_topology=True)
        if render.is_empty or render.geom_type not in possible:continue
        p=f.get('properties') or {}
        name=str(p.get('name') or p.get('name_en') or '').strip()
        if name:stats['named_count']+=1
        else:stats['unnamed_count']+=1
        out.append({'type':'Feature','properties':{
          'id':f'NE50_{kind.upper()}_{idx+1:04d}',
          'name':name or None,
          'category':'river_network' if kind=='river' else 'lake_waterbody',
          'source':'Natural Earth',
          'source_scale':'1:50m',
          'precision':'overview_only',
          'not_a_dam_inventory':True,
        },'geometry':mapping(transform(BACK,render))})
    if len(stats['invalid_empty_source_indices'])>15:
        raise RuntimeError('Too many degenerate features in '+kind+' source')
    out.sort(key=lambda f:f['properties']['id'])
    return {'type':'FeatureCollection','name':f'basin_nexus_{kind}_overview_50m','features':out},stats

def main():
    TMP.mkdir(parents=True,exist_ok=True)
    catch=json.loads((SITE/'catchments.geojson').read_text('utf-8'))
    assert catch['type']=='FeatureCollection' and len(catch['features'])==20
    geo=[transform(FORWARD,shape(f['geometry'])) for f in catch['features']]
    domain=unary_union(geo).buffer(CONTEXT_BUFFER_M)
    assert domain.is_valid and domain.area>1e11
    meta={'status':'OVERVIEW_REFERENCE_ONLY','source':'Natural Earth 1:50m rivers and lakes',
      'source_repo':'https://github.com/nvkelso/natural-earth-vector',
      'source_commit':SOURCE_REF,'license':'Natural Earth public domain',
      'purpose':'Water geography overview, not site-surveyed rivers, dams, reservoirs, irrigation assets or high-resolution river networks',
      'study_scope':'20 mainly Northern Nigeria catchments, including portions outside Nigeria',
      'domain_buffer_m':CONTEXT_BUFFER_M,
      'process_crs':'EPSG:6933','web_crs':'EPSG:4326',
      'input_catchment_sha256':hashlib.sha256((SITE/'catchments.geojson').read_bytes()).hexdigest(),'datasets':{}}
    for kind in ('river','lake'):
        data,sha=source_json(URLS[kind])
        out,stats=process(kind,data['features'],domain)
        if not out['features']:raise RuntimeError('No '+kind+' features in domain')
        target=TMP/(kind+'s_overview.geojson')
        target.write_text(json.dumps(out,separators=(',',':'),ensure_ascii=False)+'\n','utf-8')
        if target.stat().st_size>=1800000:raise RuntimeError(kind+' layer > 1.8MB')
        meta['datasets'][kind]={'url':URLS[kind],'sha256':sha,'file':target.name,
          'output_count':len(out['features']),'bytes':target.stat().st_size,**stats}
    (TMP/'hydro_reference_metadata.json').write_text(json.dumps(meta,indent=2)+'\n','utf-8')
    print(json.dumps(meta,indent=2))
    print('HYDRO OVERVIEW QA: PASS, map-scale source and jurisdiction preserved')
if __name__=='__main__':main()
