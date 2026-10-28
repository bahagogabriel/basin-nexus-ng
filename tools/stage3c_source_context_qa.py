#!/usr/bin/env python3
"""Private source-context verification. This tool cannot authorize any public evidence."""
import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from stage3c_private_editorial_qa import parse_pilot

def parse_register(text):
    """Read private Stage 3B line-register JSONL while ignoring non-record headings."""
    records = []
    for line in text.lstrip('\ufeff').splitlines():
        item = line.strip()
        if not item.startswith('{"internal_claim_id"'):
            continue
        record = json.loads(item)
        if not isinstance(record, dict) or not isinstance(record.get('internal_claim_id'), str):
            raise ValueError('Invalid private source-line record')
        records.append(record)
    if not records:
        raise ValueError('No source lines found; expected Stage 3B JSONL records')
    return records

def is_fragment(value):
    if not isinstance(value, str):
        return True
    value = value.strip()
    return (len(value) < 35 or value.endswith((':', ';')) or
            bool(re.search(r'\b(include|includes|including|as follows|listed below|the following)\s*:?$', value, re.I)))

def verify(pilot, source_lines):
    if not isinstance(pilot, list) or not isinstance(source_lines, list):
        raise ValueError('Expected two private record lists')
    grouped = defaultdict(list)
    source_ids = set()
    duplicates = 0
    for line in source_lines:
        if not isinstance(line, dict):
            raise ValueError('Malformed source line')
        key = (line.get('source_id'), line.get('internal_claim_id'))
        if key in source_ids:
            duplicates += 1
        source_ids.add(key)
        grouped[line.get('source_id')].append(line)
    flags = Counter()
    if duplicates:
        flags['duplicate_source_line_keys'] = duplicates
    matched = 0
    for candidate in pilot:
        if not isinstance(candidate, dict):
            raise ValueError('Malformed editorial candidate')
        sequence = grouped.get(candidate.get('source_internal_id'), [])
        indices = [i for i,row in enumerate(sequence)
                   if row.get('internal_claim_id') == candidate.get('principal_candidate_id')]
        if len(indices) != 1:
            flags['unresolved_or_duplicate_source_candidate'] += 1
            continue
        index = indices[0]
        original = sequence[index]
        if original.get('raw_statement_internal', '').strip() != str(candidate.get('raw_statement_internal', '')).strip():
            flags['source_wording_mismatch'] += 1
            continue
        matched += 1
        if original.get('source_section') != candidate.get('source_section'):
            flags['source_section_mismatch'] += 1
        if original.get('source_locator') != candidate.get('source_locator'):
            flags['source_locator_mismatch'] += 1
        if candidate.get('catchment_id') not in (original.get('catchment_ids') or []):
            flags['catchment_link_mismatch'] += 1
        if is_fragment(candidate.get('raw_statement_internal')):
            flags['possible_fragment_or_list_heading'] += 1
            next_lines = sequence[index+1:index+3]
            next_in_section = [r for r in next_lines if r.get('source_section') == original.get('source_section')]
            if len(next_in_section) < 2:
                flags['fragment_insufficient_adjacent_context'] += 1
        if candidate.get('publication_decision') != 'HOLD' or candidate.get('release_authorization'):
            flags['release_state_needs_manual_review'] += 1
    return {
        'kind':'PRIVATE_SOURCE_CONTEXT_INTEGRITY_SCREEN_NOT_PUBLICATION_APPROVAL',
        'publication_status':'HOLD',
        'pilot_records':len(pilot),
        'source_line_records':len(source_lines),
        'exact_source_text_matches':matched,
        'source_register_collections':len(grouped),
        'counts_by_review_flag':dict(sorted(flags.items())),
        'public_records_authorized_by_this_tool':0
    }

def main():
    p = argparse.ArgumentParser()
    p.add_argument('private_pilot')
    p.add_argument('--source-register', action='append', required=True,
                   help='Repeat for each restricted Stage 3B source-extraction text')
    p.add_argument('--out', required=True)
    args = p.parse_args()
    root = Path(__file__).resolve().parents[1]
    srcs = [Path(args.private_pilot).resolve()] + [Path(x).resolve() for x in args.source_register]
    target = Path(args.out).resolve()
    if any(x.is_relative_to(root) for x in srcs+[target]):
        raise SystemExit('Private source/register/report must remain outside public repository')
    if target in srcs or target.exists() or not target.parent.is_dir() or any(not s.is_file() for s in srcs):
        raise SystemExit('Private sources must exist; output must be new and cannot overwrite an input')
    pilot = parse_pilot(srcs[0].read_text(encoding='utf-8'))
    source_lines = []
    for source in srcs[1:]:
        source_lines.extend(parse_register(source.read_text(encoding='utf-8')))
    report = verify(pilot, source_lines)
    with target.open('x', encoding='utf-8') as f:
        json.dump(report,f,sort_keys=True,indent=2)
        f.write('\n')
    print('Private source-integrity screening complete. Aggregate report only; public approvals: 0.')

if __name__ == '__main__':
    main()
