#!/usr/bin/env python3
"""PRIVATE Stage 3C-B pilot screening. No individual statement may be published by this tool."""
import argparse
import json
import re
from collections import Counter
from pathlib import Path

THEMES = frozenset({'natural_resources','threats_challenges','socioeconomics','policies','interventions'})
REQUIRED = ('internal_review_id','principal_candidate_id','catchment_id','theme','source_internal_id',
            'source_section','source_locator','raw_statement_internal','engagement_period','engagement_city')
EVENT_CITIES = frozenset({'Kano','Sokoto','Ilorin','Lokoja','Gombe'})

def parse_pilot(text):
    """Accept a JSON array or a private Google Doc text export containing one JSON object per line."""
    text = text.lstrip('\ufeff').strip()
    if text.startswith('['):
        data = json.loads(text)
        if not isinstance(data, list):
            raise ValueError('Expected JSON list')
        return data
    records = []
    for line in text.splitlines():
        candidate = line.strip()
        if not candidate.startswith('{'):
            continue
        value = json.loads(candidate)
        if not isinstance(value, dict) or 'internal_review_id' not in value:
            raise ValueError('Unexpected JSON object within private pilot')
        records.append(value)
    if not records:
        raise ValueError('No editorial records found in private pilot')
    return records

def audit(records):
    if not isinstance(records, list):
        raise ValueError('Expected list of editorial review records')
    ids, refs = set(), set()
    counts, themes, cities, catchments = Counter(), Counter(), Counter(), Counter()
    for row in records:
        if not isinstance(row, dict):
            raise ValueError('Expected editorial review object')
        counts['record_count'] += 1
        if any(not isinstance(row.get(k), str) or not row[k].strip() for k in REQUIRED):
            counts['missing_source_or_identity_anchor'] += 1
        identifier = row.get('internal_review_id')
        if not isinstance(identifier, str) or not re.fullmatch(r'BN-PILOT-\d{3,}', identifier) or identifier in ids:
            counts['invalid_or_duplicate_review_id'] += 1
        else:
            ids.add(identifier)
        candidate = row.get('principal_candidate_id')
        if not isinstance(candidate, str) or not candidate or candidate in refs:
            counts['duplicate_or_missing_source_candidate'] += 1
        else:
            refs.add(candidate)
        catchment = row.get('catchment_id')
        if not isinstance(catchment, str) or not re.fullmatch(r'SCMP-C(?:0[1-9]|1\d|20)', catchment):
            counts['invalid_catchment_id'] += 1
        else:
            catchments[catchment] += 1
        theme = row.get('theme')
        if theme not in THEMES:
            counts['unclassified_theme'] += 1
        else:
            themes[theme] += 1
        city = row.get('engagement_city')
        if city not in EVENT_CITIES:
            counts['unrecognized_engagement_city'] += 1
        else:
            cities[city] += 1
        statement = row.get('raw_statement_internal','')
        statement = statement if isinstance(statement, str) else ''
        if len(statement.strip()) < 35 or statement.rstrip().endswith((':',';')) or re.search(
            r'\b(include|includes|including|as follows|listed below|the following)\s*:?$',statement.strip(),re.I):
            counts['context_or_fragment_review'] += 1
        summary = row.get('editorial_summary_candidate')
        if not isinstance(summary, str) or not summary.strip():
            counts['paraphrase_required'] += 1
        if row.get('editorial_review') != 'APPROVED':
            counts['editorial_review_pending'] += 1
        if row.get('independent_verification') != 'PERFORMED':
            counts['independent_verification_not_performed'] += 1
        if row.get('source_rights') != 'CLEARED':
            counts['source_rights_pending'] += 1
        if row.get('privacy_status') != 'CLEARED':
            counts['privacy_review_pending'] += 1
        if row.get('location') is not None:
            counts['location_present_requires_independent_spatial_review'] += 1
        if row.get('publication_decision') != 'HOLD' or row.get('release_authorization'):
            counts['release_state_requires_manual_investigation'] += 1
    # Never copy identifiers, quotations, precise locations, private links or excerpts into QA output.
    return {
        'kind': 'PRIVATE_STAGE3C_EDITORIAL_SCREEN_NOT_APPROVAL',
        'publication_status': 'HOLD',
        'total_candidates': len(records),
        'catchments_represented': len(catchments),
        'counts_by_theme': dict(sorted(themes.items())),
        'counts_by_host_city': dict(sorted(cities.items())),
        'review_flags': dict(sorted(counts.items())),
        'public_records_authorized_by_this_tool': 0
    }

def main():
    ap = argparse.ArgumentParser(description='Private Stage 3C editorial QA; never grants release permission')
    ap.add_argument('private_input', help='Private JSON array or exported pilot text')
    ap.add_argument('--out', required=True, help='New private aggregate JSON report')
    args = ap.parse_args()
    repo = Path(__file__).resolve().parents[1]
    source, dest = Path(args.private_input).resolve(), Path(args.out).resolve()
    if source.is_relative_to(repo) or dest.is_relative_to(repo) or source == dest:
        raise SystemExit('Refusing private input/output inside public repository')
    if not source.is_file() or not dest.parent.is_dir() or dest.exists():
        raise SystemExit('Input file or output path invalid; never overwrite private reports')
    results = audit(parse_pilot(source.read_text(encoding='utf-8')))
    with dest.open('x', encoding='utf-8') as f:
        json.dump(results, f, indent=2, sort_keys=True)
        f.write('\n')
    print('Private editorial QA complete; aggregate-only report created. Public approvals: 0.')

if __name__ == '__main__':
    main()
