#!/usr/bin/env python3
"""HydroRIVERS v1 Africa: review-only density and topology preflight.

Official source: HydroSHEDS HydroRIVERS_v10_af_shp.zip (~108 MB).
CAUTION: The HydroSHEDS v1 license restricts independent redistribution.
This script NEVER writes or commits source river geometry. It reports only
aggregate per-catchment reach counts and source-field quality indicators.
Publishing derived geometries requires a distinct license decision and QA.
"""
from collections import Counter,defaultdict
from datetime import datetime,timezone
from pathlib import Path
import hashlib
import json
import shutil
import tempfile
import zipfile
import requests
import pyogrio
from shapely.geometry import shape
from shapely.strtree import STRtree

ROOT=Path(__file__).resolve().parents[1]
REPORT=ROOT/'review/hydrorivers-licensing-qa'
URL='https://data.hydrosheds.org/file/HydroRIVERS/HydroRIVERS_v10_af_shp.zip'
MAX_ARCHIVE_BYTES=225*1024*1024
MAX_UNCOMPRESSED_BYTES=1300*1024*1024

def download(target):
    sha=hashlib.sha256();size=0
    with requests.get(URL,stream=True,timeout=(30,220),headers={'User-Agent':'Basin-Nexus-NG/Stage2E-ReadOnly-Density-QA'}) as response:
        response.raise_for_status()
        with target.open('wb') as file:
            for chunk in response.iter_content(1024*1024):
                if not chunk:continue
                size+=len(chunk)
                if size>MAX_ARCHIVE_BYTES:raise ValueError('Unexpected large HydroRIVERS source')
                sha.update(chunk);file.write(chunk)
    if size<30*1024*1024:raise ValueError('Too-small HydroRIVERS source or incorrect response')
    return {'url':URL,'sha256':sha.hexdigest(),'compressed_bytes':size}
def unpack_safely(archive,out):
    with zipfile.ZipFile(archive) as z:
        members=z.infolist()
        if sum(m.file_size for m in members)>MAX_UNCOMPRESSED_BYTES:
            raise ValueError('Unexpectedly oversized extracted HydroRIVERS data')
        for m in members:
            p=Path(m.filename)
            if p.is_absolute() or '..' in p.parts:raise ValueError('Untrusted ZIP entry '+m.filename)
        z.extractall(out)
    shapefiles=list(out.rglob('*.shp'))
    if len(shapefiles)!=1:raise ValueError('Expected one HydroRIVERS Africa shapefile')
    return shapefiles[0]

def main():
    REPORT.mkdir(parents=True,exist_ok=True)
    atlas=json.loads((ROOT/'site/data/catchments.geojson').read_text('utf-8'))
    assert len(atlas['features'])==20
    ids=[f['properties']['id'] for f in atlas['features']]
    polys=[shape(f['geometry']) for f in atlas['features']]
    assert all(g.is_valid for g in polys)
    tree=STRtree(polys)
    left=min(x.bounds[0] for x in polys)-0.2
    bottom=min(x.bounds[1] for x in polys)-0.2
    right=max(x.bounds[2] for x in polys)+0.2
    top=max(x.bounds[3] for x in polys)+0.2
    with tempfile.TemporaryDirectory(prefix='bn-hydrorivers-') as tmp:
        tmp=Path(tmp);original=tmp/'hydrorivers_africa.zip'
        source=download(original)
        shp=unpack_safely(original,tmp/'extracted')
        info=pyogrio.read_info(str(shp))
        actual_crs=str(info['crs'])
        needed=[f for f in ('HYRIV_ID','NEXT_DOWN','ORD_FLOW','ORD_STRA','LENGTH_KM','UPLAND_SKM') if f in info['fields']]
        if 'HYRIV_ID' not in needed or 'ORD_FLOW' not in needed:
            raise ValueError('Expected HydroRIVERS key fields missing; publication on hold')
        frame=pyogrio.read_dataframe(str(shp),bbox=(left,bottom,right,top),columns=needed)
        if frame.crs is None:raise ValueError('Missing source CRS')
        if frame.crs.to_epsg()!=4326:frame=frame.to_crs('EPSG:4326')
        counts=Counter();orders=defaultdict(Counter);selectedIds=set();sourceIDs=set();empty=0
        for record in frame.itertuples(index=False):
            geom=record.geometry
            if geom is None or geom.is_empty:empty+=1;continue
            hyid=getattr(record,'HYRIV_ID')
            if hyid in sourceIDs:raise ValueError('Duplicate river reach identifier within spatial sample')
            sourceIDs.add(hyid)
            matches=tree.query(geom,predicate='intersects')
            if not len(matches):continue
            selectedIds.add(hyid)
            order=getattr(record,'ORD_FLOW',None)
            for j in matches:
                c=ids[int(j)];counts[c]+=1
                orders[c][str(int(order)) if order is not None else 'unknown']+=1
        metrics={'status':'REVIEW_ONLY_NO_GEOMETRY_PUBLICATION','publication_approved':False,
           'source':'HydroRIVERS v1.0 (Africa) / HydroSHEDS / WWF',
           'retrieved_utc':datetime.now(timezone.utc).isoformat(),
           'source_download':source,
           'license_warning':'HydroSHEDS v1 license contains redistribution conditions. Do not automatically publish original or clipped reach geometry.',
           'n_atlas_catchments':20,'source_crs':actual_crs,
           'bbox_wgs84':[round(v,5) for v in [left,bottom,right,top]],
           'bbox_candidate_reaches':len(frame),'invalid_or_empty_candidates':empty,
           'unique_reaches_intersecting_atlas':len(selectedIds),
           'catchments':[{'id':cid,'name':atlas['features'][idx]['properties']['name'],
             'reaches_intersecting':counts[cid],
             'ord_flow_counts':dict(sorted(orders[cid].items()))}
             for idx,cid in enumerate(ids)],
           'not_analysed':['river names, not systematically present in HydroRIVERS',
              'official jurisdictional waterbody designation',
              'channel alignment with user catchment GIS at full resolution',
              'full hydrologic connectivity QA and license compliance']}
        (REPORT/'density_and_license_hold.json').write_text(json.dumps(metrics,indent=2)+'\n','utf-8')
        assert len(metrics['catchments'])==20
        assert len(selectedIds)>100,'Dataset is too sparse or bbox query misinterpreted'
        print('HYDRORIVERS AFRICA PRE-FLIGHT — QA ONLY')
        print('Unique reaches touching study:',len(selectedIds))
        print('Atlas catchments with river reaches:',sum(v>0 for v in counts.values()),'/20')
        for c in metrics['catchments']:
            print(c['id'],c['name'],c['reaches_intersecting'])
        print('NO HYDRORIVERS LINE GEOMETRY OR LICENSED SOURCE IS OUTPUT')
if __name__=='__main__':main()
