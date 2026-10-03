"""Descriptive rates and Wilson intervals; blocked runs never enter denominators."""
import argparse
import json
import math
from pathlib import Path

def wilson(k, n, z=1.96):
    if not n: return None
    d = 1+z*z/n
    center = (k/n+z*z/(2*n))/d
    margin = z*math.sqrt((k/n)*(1-k/n)/n+z*z/(4*n*n))/d
    return [max(0, center-margin), min(1, center+margin)]

def summarize(runs):
    groups = {}
    for r in runs:
        if r.get('pilot'): continue
        key = r['arm']
        group = groups.setdefault(key, {'attempted': 0, 'valid': 0, 'blocked': 0, 'failures': 0, 'task_failures': 0})
        group['attempted'] += 1
        if r['outcome'] == 'blocked': group['blocked'] += 1
        else:
            group['valid'] += 1
            group['failures'] += bool(r['failures'])
            group['task_failures'] += r['outcome']=='task_failed'
    for g in groups.values():
        g['failure_rate'] = g['failures']/g['valid'] if g['valid'] else None
        g['task_failure_rate'] = g['task_failures']/g['valid'] if g['valid'] else None
        g['wilson_95'] = wilson(g['failures'], g['valid'])
    return groups

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('files', nargs='+')
    args = parser.parse_args()
    print(json.dumps(summarize([json.loads(Path(p).read_text()) for p in args.files]), indent=2))

if __name__ == '__main__': main()
