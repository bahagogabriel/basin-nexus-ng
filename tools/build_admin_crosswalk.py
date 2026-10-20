#!/usr/bin/env python3
"""Basin Nexus NG -- reproduce catchment -> State/LGA spatial crosswalk.

No administrative result is manufactured without ADM1 & ADM2 boundary files.
The optional downloader reads geoBoundaries gbOpen 2022 Nigeria (GRID3-derived,
CC BY 4.0). The joins remain PROVISIONAL pending agency boundary QA.

Commands:
  python build_admin_crosswalk.py --self-test
  python build_admin_crosswalk.py --catchments SCMP_20_Catchments_Validated.gpkg --out crosswalk
  python build_admin_crosswalk.py --catchments SCMP_20_Catchments_Validated.gpkg --adm1 NGA_ADM1.geojson --adm2 NGA_ADM2.geojson --out crosswalk

Requires geopandas>=1.0, shapely>=2.0, pyproj, and requests (for downloading only).
"""
import argparse, json, csv, hashlib
from pathlib import Path
import geopandas as gpd
from shapely.geometry import Polygon
from shapely.validation import make_valid

API='https://www.geoboundaries.org/api/current/gbOpen/NGA/{level}/'
CRS='EPSG:6933'
NAME_FIELDS=('shapeName','admin1Name','admin2Name','name','NAME','NAME_1','NAME_2','ADM1_EN','ADM2_EN')

def field(g,opts):
 for candidate in opts:
  if candidate in g.columns: return candidate
 raise ValueError('No administrative name field in '+','.join(g.columns))

def clean_admin(raw,level):
 if raw.crs is None: raise ValueError(f'{level} has no CRS')
 n=field(raw,NAME_FIELDS)
 a=raw.loc[raw.geometry.notna()].copy().reset_index(drop=True)
 a['geometry']=a.geometry.map(make_valid)
 a=a.loc[a.geom_type.isin(['Polygon','MultiPolygon'])].copy().reset_index(drop=True)
 a['admin_name']=a[n].astype(str).str.strip()
 a=a.loc[a['admin_name'].ne('')].copy().reset_index(drop=True)
 a['uid']=[f'{level}-'+(str(val) if 'shapeID' in a.columns and str(val).strip() not in ('','nan','None') else f'{i+1:04d}') for i,val in enumerate(a['shapeID'] if 'shapeID' in a.columns else ['']*len(a))]
 if a['uid'].duplicated().any():raise ValueError(f'{level} has duplicate admin identifiers; verify file')
 a=a[['uid','admin_name','geometry']].to_crs(CRS)
 assert all(a.is_valid)
 return a

def compute(rawcatch,rawst,rawlg,min_intersection_km2=.01):
 if rawcatch.crs is None or not {'CatchID','Name'}.issubset(rawcatch.columns):raise ValueError('Catchment data require CRS, CatchID, Name')
 c=rawcatch[['CatchID','Name','geometry']].copy().to_crs(CRS)
 c['geometry']=c.geometry.map(make_valid)
 if c['CatchID'].duplicated().any() or len(c)!=20 and len(c)!=2:raise ValueError('Unexpected catchment count or duplicate IDs')
 st=clean_admin(rawst,'ADM1');lg=clean_admin(rawlg,'ADM2')
 areas={v:float(g.area/1e6) for v,g in zip(c['CatchID'],c.geometry)}
 a=gpd.overlay(c,st,how='intersection',keep_geom_type=True,make_valid=True)
 a['intersect_km2']=a.geometry.area/1e6
 a=a.loc[a.intersect_km2>=min_intersection_km2].copy()
 a['Pct_of_catchment']=[round(100*row.intersect_km2/areas[row.CatchID],6) for row in a.itertuples()]
 st_result=a[['CatchID','Name','uid','admin_name','intersect_km2','Pct_of_catchment']].rename(columns={'Name':'Catchment','uid':'StateUID','admin_name':'State','intersect_km2':'Intersection_km2'})

 # Assign each specific LGA polygon to the state with the largest geometric overlap.
 # Name-only joins are incorrect for LGAs that share names or contain spelling variants.
 pp=gpd.overlay(lg,st,how='intersection',keep_geom_type=True,make_valid=True)
 pp['match_area']=pp.geometry.area
 pp=pp.sort_values('match_area',ascending=False).drop_duplicates('uid_1')
 parent={r.uid_1:(r.uid_2,r.admin_name_2) for r in pp.itertuples()}
 lga_hits=gpd.overlay(c,lg,how='intersection',keep_geom_type=True,make_valid=True)
 lga_hits['intersect_km2']=lga_hits.geometry.area/1e6
 lga_hits=lga_hits.loc[lga_hits.intersect_km2>=min_intersection_km2].copy()
 lga_hits['state_uid']=[parent.get(uid,('',''))[0] for uid in lga_hits.uid]
 lga_hits['state_name']=[parent.get(uid,('',''))[1] for uid in lga_hits.uid]
 lga_hits['Pct_of_catchment']=[round(100*row.intersect_km2/areas[row.CatchID],6) for row in lga_hits.itertuples()]
 lg_result=lga_hits[['CatchID','Name','state_uid','state_name','uid','admin_name','intersect_km2','Pct_of_catchment']].rename(columns={'Name':'Catchment','state_uid':'StateUID','state_name':'State','uid':'LGA_UID','admin_name':'LGA','intersect_km2':'Intersection_km2'})

 # Union rather than sum protects the coverage metric from duplicate admin polygons.
 national_union=st.geometry.union_all()
 coverage=[]
 for r in c.itertuples():
  ci=r.geometry.intersection(national_union).area/1e6
  ca=areas[r.CatchID]
  coverage.append({'CatchID':r.CatchID,'Catchment':r.Name,'Area_km2':round(ca,3),'Covered_by_admin1_km2':round(ci,3),'Not_covered_km2':round(max(0,ca-ci),3),'Covered_pct':round(100*ci/ca,4),'QA':'PROVISIONAL_NOT_APPROVED'})
 return st_result.sort_values(['CatchID','State']).reset_index(drop=True),lg_result.sort_values(['CatchID','State','LGA']).reset_index(drop=True),coverage

def fetch(level,out):
 import requests
 r=requests.get(API.format(level=level),timeout=45);r.raise_for_status();m=r.json()
 if m.get('boundaryISO')!='NGA' or m.get('boundaryType')!=level:raise ValueError('Unexpected upstream administrative dataset')
 if 'Creative Commons Attribution 4.0' not in m.get('boundaryLicense',''):raise ValueError('Unexpected data license; review before use')
 p=out/f'geoBoundaries_NGA_{level}.geojson'
 if not p.exists():
  r=requests.get(m['simplifiedGeometryGeoJSON'],timeout=120);r.raise_for_status()
  b=r.content
  if not b.lstrip().startswith(b'{') or b'FeatureCollection' not in b[:1000]:raise RuntimeError('Download returned invalid JSON or Git LFS pointer')
  p.write_bytes(b)
 m['local_sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
 return p,m

def self_test():
 crs='EPSG:4326'
 c=gpd.GeoDataFrame({'CatchID':['X1','X2'],'Name':['WestCatch','EastCatch']},geometry=[Polygon([(0,0),(2,0),(2,2),(0,2)]),Polygon([(2,0),(3,0),(3,2),(2,2)])],crs=crs)
 states=gpd.GeoDataFrame({'shapeName':['Alpha','Beta'],'shapeID':['S1','S2']},geometry=[Polygon([(0,0),(1.5,0),(1.5,3),(0,3)]),Polygon([(1.5,0),(3,0),(3,3),(1.5,3)])],crs=crs)
 # Two distinct LGAs deliberately have identical names: avoid name-collapsing.
 lgas=gpd.GeoDataFrame({'shapeName':['Central','Central','South'],'shapeID':['L1','L2','L3']},geometry=[Polygon([(0,0),(1.5,0),(1.5,3),(0,3)]),Polygon([(1.5,0),(2.5,0),(2.5,3),(1.5,3)]),Polygon([(2.5,0),(3,0),(3,3),(2.5,3)])],crs=crs)
 st,lg,audit=compute(c,states,lgas)
 assert len(st)==3,(len(st),st)
 assert len(lg)==4,(len(lg),lg)
 assert lg[lg.LGA=='Central'].LGA_UID.nunique()==2
 assert lg[lg.LGA_UID=='ADM2-L2'].State.unique().tolist()==['Beta']
 assert abs(audit[0]['Covered_pct']-100)<.001 and abs(audit[1]['Covered_pct']-100)<.001
 assert sum(st[st.CatchID=='X1']['Pct_of_catchment'])-100<.01
 print('PASS: CRS transform; area intersections; shared-name LGAs remain unique; state parent attribution; coverage union.')

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--self-test',action='store_true');p.add_argument('--catchments');p.add_argument('--adm1');p.add_argument('--adm2');p.add_argument('--out',default='BasinNexusNG_Admin_Crosswalk')
 args=p.parse_args()
 if args.self_test:self_test();raise SystemExit(0)
 if not args.catchments:p.error('Provide --catchments or --self-test')
 d=Path(args.out);d.mkdir(parents=True,exist_ok=True)
 m={}
 if args.adm1 or args.adm2:
  if not args.adm1 or not args.adm2:p.error('Provide both --adm1 and --adm2')
  p1,p2=Path(args.adm1),Path(args.adm2)
 else:p1,m['ADM1']=fetch('ADM1',d);p2,m['ADM2']=fetch('ADM2',d)
 st,lg,audit=compute(gpd.read_file(args.catchments),gpd.read_file(p1),gpd.read_file(p2))
 st.to_csv(d/'BasinNexusNG_Catchment_State_Crosswalk_PROVISIONAL.csv',index=False)
 lg.to_csv(d/'BasinNexusNG_Catchment_LGA_Crosswalk_PROVISIONAL.csv',index=False)
 with (d/'BasinNexusNG_Administrative_Coverage_QA.csv').open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=audit[0].keys());w.writeheader();w.writerows(audit)
 (d/'Boundary_Source_Metadata.json').write_text(json.dumps(m,indent=2))
 print(f'PROVISIONAL: {len(st)} state intersections, {len(lg)} LGA intersections written. Review for spatial and administrative validity before publication.')
