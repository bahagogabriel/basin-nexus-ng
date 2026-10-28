#!/usr/bin/env python3
"""Offline, private review-receipt gate. Does not publish or create approvals."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from datetime import date
from pathlib import Path
from evidence_publication_gate import SCHEMA_VERSION, validate

def digest(record):
    # Fingerprint binds review to the exact public-facing JSON record.
    raw=json.dumps(record,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False)
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()

def promote(candidate, manifest, allowed_catchments):
    if not isinstance(candidate,dict) or candidate.get('type')!='PublicEvidenceCollection':
        raise ValueError('Candidate must be a complete public evidence collection')
    if manifest.get('type')!='EvidencePublicationReview' or manifest.get('review_version')!='1':
        raise ValueError('Review receipt must be an explicit EvidencePublicationReview v1')
    receipts=manifest.get('records')
    if not isinstance(receipts,list) or len(receipts)!=len(candidate.get('records',[])):
        raise ValueError('One completed receipt required per candidate')
    receipt_index={}
    for rec in receipts:
        if not isinstance(rec,dict) or set(rec)!={'record_id','record_sha256','source_rights',
                'privacy','editorial','reviewer','decision_date','release_authorization','spatial_review'}:
            raise ValueError('Review receipt must have exactly the approved fields')
        rid=rec['record_id']
        if rid in receipt_index or not isinstance(rid,str):
            raise ValueError('Duplicate or invalid review receipt ID')
        if (rec['source_rights']!='CLEARED' or rec['privacy']!='CLEARED' or
            rec['editorial']!='APPROVED' or not isinstance(rec['reviewer'],str) or
            len(rec['reviewer'].strip())<3):
            raise ValueError('Independent source-rights, privacy and named reviewer decisions missing')
        try:
            when=date.fromisoformat(rec['decision_date'])
        except (ValueError,TypeError):
            raise ValueError('Invalid review decision date') from None
        if when>date.today():
            raise ValueError('A publication review cannot be future-dated')
        if not isinstance(rec['record_sha256'],str) or not re.fullmatch(r'[a-f0-9]{64}',rec['record_sha256']):
            raise ValueError('Invalid record fingerprint')
        receipt_index[rid]=rec
    public_records=candidate['records']
    seen=set()
    for record in public_records:
        rid=record.get('record_id') if isinstance(record,dict) else None
        if rid in seen or rid not in receipt_index:
            raise ValueError('Missing or duplicate record-specific review decision')
        seen.add(rid)
        receipt=receipt_index[rid]
        if digest(record)!=receipt['record_sha256']:
            raise ValueError('Record changed after editorial review')
        if receipt['release_authorization']!=record.get('release_authorization'):
            raise ValueError('Review authorization mismatch')
        if receipt['spatial_review']!=('APPROVED' if record.get('location') else 'NOT_APPLICABLE'):
            raise ValueError('Independent mapped-location approval is missing or inconsistent')
    released={'type':'PublicEvidenceCollection','schema_version':SCHEMA_VERSION,
              'publication_status':'APPROVED_PUBLIC_ONLY','records':public_records}
    result=validate(released,allowed_catchments)
    return released,result

def main():
    parser=argparse.ArgumentParser(description='Private record-fingerprint review gate; does not deploy')
    parser.add_argument('candidate')
    parser.add_argument('--review-manifest',required=True)
    parser.add_argument('--out',required=True)
    args=parser.parse_args()
    root=Path(__file__).resolve().parents[1]
    paths=[Path(p).resolve() for p in (args.candidate,args.review_manifest,args.out)]
    if any(p.is_relative_to(root) for p in paths):
        raise SystemExit('Candidate, review receipt and output must stay outside public repository')
    if any(not p.is_file() for p in paths[:2]) or paths[2].exists() or not paths[2].parent.is_dir():
        raise SystemExit('Private inputs must exist; output must be new, never overwrite')
    candidate=json.loads(paths[0].read_text('utf-8'))
    review=json.loads(paths[1].read_text('utf-8'))
    ids=json.loads((root/'site/data/registry.json').read_text('utf-8'))
    collection,report=promote(candidate,review,{c['id'] for c in ids})
    with paths[2].open('x',encoding='utf-8') as handle:
        json.dump(collection,handle,ensure_ascii=False,allow_nan=False,indent=2)
        handle.write('\n')
    print(f"Private reviewed export created: {report['validated_public_records']} records, "
          f"{report['mapped_locations']} independently validated positions. "
          "This is NOT publication; independent approval authenticity and a reviewed PR are still required.")

if __name__=='__main__':
    main()
