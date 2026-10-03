"""Offline schema, link, privacy, fixture and reporting-gate checks. No model calls."""
import json
from pathlib import Path
import re

from jsonschema import Draft202012Validator, FormatChecker
from analyzers.redact import has_obvious_private_data
ROOT=Path(__file__).resolve().parents[1]

def validate():
    schemas={p.stem.split('.')[0]: json.loads(p.read_text(encoding='utf-8')) for p in (ROOT/'schemas').glob('*.json')}
    for schema in schemas.values(): Draft202012Validator.check_schema(schema)
    checks=0
    for path in (ROOT/'scenarios').glob('*.json'):
        Draft202012Validator(schemas['scenario'],format_checker=FormatChecker()).validate(json.loads(path.read_text(encoding='utf-8'))); checks+=1
    for path in (ROOT/'results/runs').glob('*.json'):
        Draft202012Validator(schemas['run'],format_checker=FormatChecker()).validate(json.loads(path.read_text(encoding='utf-8'))); checks+=1
    for path in (ROOT/'docs/failures').glob('*.json'):
        Draft202012Validator(schemas['failure-card']).validate(json.loads(path.read_text(encoding='utf-8'))); checks+=1
    for folder in ('results','reports'):
        for path in (ROOT/folder).rglob('*.json'):
            text=path.read_text(encoding='utf-8')
            json.loads(text)
            if has_obvious_private_data(text): raise ValueError(f'Privacy pattern in {path.relative_to(ROOT)}')
    broken=[]
    for folder in (ROOT, ROOT/'docs', ROOT/'reports'):
        paths = folder.glob('*.md') if folder==ROOT else folder.rglob('*.md')
        for path in paths:
            for target in re.findall(r'(?<!!)\[[^\]]+\]\(([^)]+)\)',path.read_text(encoding='utf-8')):
                if '://' in target or target.startswith('#'): continue
                target=target.split('#')[0]
                if target and not (path.parent/target).exists(): broken.append(str(path.relative_to(ROOT))+': '+target)
    if broken: raise ValueError('Broken local links: '+', '.join(broken))
    gate=json.loads((ROOT/'reports/reporting-gate.json').read_text())
    if gate['new_issues_submitted']>gate['max_new_issues_this_cycle']: raise ValueError('Issue count exceeds gate')
    if gate['decision']=='submit' and not all(gate['checks'].values()): raise ValueError('Incomplete reporting gate')
    cards=json.loads((ROOT/'reports/candidate-screening.json').read_text())
    if cards['candidate_count']!=len(cards['candidates']) or cards['candidate_count']<20: raise ValueError('Candidate inventory mismatch')
    return {'schema_documents_validated':checks,'candidates_screened':cards['candidate_count'],
            'privacy_metadata_checks':'pass','local_links':'pass','reporting_decision':gate['decision']}

def main(): print(json.dumps(validate()))
if __name__=='__main__': main()
