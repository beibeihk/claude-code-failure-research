"""Invocation diagnostics; correlation with the CLI tool stream remains necessary."""
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path

def analyze(records):
    counts = Counter(r['event'] for r in records)
    groups = defaultdict(list)
    for record in records:
        if record.get('tool_use_hash'):
            groups[(record.get('session_hash'),record['tool_use_hash'])].append(record)
    duplicates, order = [], []
    for key, group in groups.items():
        repeated = Counter((r['event'], r.get('registration')) for r in group)
        duplicates += [{'tool_use_hash': key[1], 'event': event, 'count': count}
                       for (event, _), count in repeated.items() if count > 1]
        pre = [r['monotonic_ns'] for r in group if r['event']=='PreToolUse']
        post = [r['monotonic_ns'] for r in group if r['event'] in ('PostToolUse','PostToolUseFailure')]
        if pre and post and min(post) < min(pre): order.append(key[1])
    return {'counts': dict(counts), 'potential_duplicate_deliveries': duplicates,
            'potential_order_mismatches': order,
            'finding': 'diagnostics only; establish registrations and stream correlation before classification'}

def main():
    p=argparse.ArgumentParser(); p.add_argument('ledger_folder'); args=p.parse_args()
    print(json.dumps(analyze([json.loads(f.read_text()) for f in Path(args.ledger_folder).glob('*.json')]),indent=2))

if __name__=='__main__': main()
