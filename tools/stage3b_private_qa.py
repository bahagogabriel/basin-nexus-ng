#!/usr/bin/env python3
"""Stage 3B private review QA. Input and output MUST remain outside public repository."""
import argparse
import json
import math
from pathlib import Path
from collections import Counter

TOPICS={'water_infrastructure','natural_resources','ecosystems','threats_challenges','socioeconomics','policies','interventions'}
STATUSES={'unknown','requested','planned','designed','contract_awarded','under_construction','completed','abandoned','stakeholder_reported'}
EVIDENCE={'stakeholder_reported','cross_checked','independently_verified'}

def audit(rows):
    if not isinstance(rows,list): raise ValueError('Expected private claims array')
    ids=set(); flags=Counter(); themes=Counter(); catchments=Counter(); readiness=Counter(); groups={}
    for row in rows:
        if not isinstance(row,dict): raise ValueError('Expected claim object')
        issues=set(); cid=row.get('internal_claim_id')
        if not isinstance(cid,str) or not cid or cid in ids: issues.add('MISSING_OR_DUPLICATE_INTERNAL_ID')
        else: ids.add(cid)
        if not row.get('source_id') or not row.get('source_locator'): issues.add('PROVENANCE_INCOMPLETE')
        if not isinstance(row.get('raw_statement_internal'),str) or not row['raw_statement_internal'].strip(): issues.add('ORIGINAL_WORDING_MISSING')
        links=row.get('catchment_ids')
        if not isinstance(links,list) or not links or any(not isinstance(c,str) or len(c)!=8 or not c.startswith('SCMP-C') or not c[-2:].isdigit() or not 1<=int(c[-2:])<=20 for c in links): issues.add('CATCHMENT_LINK_UNRESOLVED')
        else: catchments.update(links)
        theme=row.get('theme'); themes[theme if theme in TOPICS else 'unclassified']+=1
        if theme not in TOPICS: issues.add('INVALID_THEME')
        if row.get('reported_status','unknown') not in STATUSES: issues.add('STATUS_REVIEW')
        if row.get('evidence_status') not in EVIDENCE: issues.add('EVIDENCE_STATE_INVALID')
        if row.get('redistribution_rights')!='CLEARED': issues.add('RIGHTS_NOT_CLEARED')
        if row.get('release_decision')=='APPROVED' and not row.get('release_authorization'): issues.add('MISSING_RELEASE_AUTHORIZATION')
        if row.get('release_authorization') and row.get('release_decision')!='APPROVED': issues.add('RELEASE_STATE_MISMATCH')
        if row.get('privacy_flag') not in ('NONE','REVIEW','RESTRICTED'): issues.add('PRIVACY_REVIEW_REQUIRED')
        position=row.get('coordinates')
        if position is None: readiness['no_verified_point']+=1
        elif not isinstance(position,dict) or position.get('verification')!='independently_validated' or any(isinstance(position.get(k),bool) or not isinstance(position.get(k),(int,float)) or not math.isfinite(position[k]) for k in ('latitude','longitude','uncertainty_m')) or not (-90<=position['latitude']<=90 and -180<=position['longitude']<=180 and 0<=position['uncertainty_m']<=1e7):
            issues.add('COORDINATE_NOT_VERIFIED'); readiness['unvalidated_point_rejected']+=1
        else: readiness['validated_point_candidate']+=1
        group=row.get('reconciliation_group')
        if group and group!='PENDING': groups.setdefault(group,[]).append((row.get('quantity'),row.get('unit'),row.get('reported_status')))
        flags.update(issues)
    conflicts=sum(len({str(value) for value in values})>1 for values in groups.values() if len(values)>1)
    return {'publication_status':'PRIVATE_INTERNAL_QA_ONLY','total_records':len(rows),'unique_internal_ids':len(ids),'theme_counts':dict(sorted(themes.items())),'catchment_record_links':dict(sorted(catchments.items())),'readiness_counts':dict(sorted(readiness.items())),'flag_counts':dict(sorted(flags.items())),'reconciliation_groups':len(groups),'groups_requiring_conflict_review':conflicts,'approved_for_publication':0}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('private_claims')
    parser.add_argument('--out',required=True)
    args=parser.parse_args()
    source=Path(args.private_claims).resolve(); dest=Path(args.out).resolve()
    repository=Path(__file__).resolve().parents[1]
    if source==dest or source.is_relative_to(repository) or dest.is_relative_to(repository): raise SystemExit('Private files must remain outside the public repository')
    if not dest.parent.is_dir() or dest.exists(): raise SystemExit('Destination must be an existing private directory and a new file')
    report=audit(json.loads(source.read_text(encoding='utf-8')))
    dest.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print('Private QA complete:', report['total_records'], 'records. No private content printed.')

if __name__=='__main__': main()
