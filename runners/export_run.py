"""Export only a redacted metadata whitelist; never a full transcript."""
import argparse
import hashlib
import json
from pathlib import Path

from analyzers.redact import has_obvious_private_data, redact_tree
ROOT = Path(__file__).resolve().parents[1]
FIELDS = {'schema_version','run_id','agent','version','model','requested_model','scenario','scenario_version',
          'scenario_sha256','fixture_commit','fixture_snapshot_sha256','arm','trial','pilot','date','platform',
          'surface','provider','mode','context_config','plugins','outcome','failures','partial_failures',
          'process_exit_code','timed_out','tool_count','tool_error_count','cost_usd','elapsed_seconds',
          'verifier','claim_assessments','compact_boundaries','evidence_level','limitations'}
VERIFIER_FIELDS = {'observer_test_exit_code','observer_tests_run','bug_fixed','public_api_unchanged',
                   'forbidden_paths_changed','changed_paths','verification_integrity','final_source_hash',
                   'pre_edit_verified','final_state_verified_by_agent'}
CLAIM_FIELDS = {'kind','scope','count','assessment','reason'}

def public_summary(summary):
    public = {k: v for k, v in summary.items() if k in FIELDS}
    if 'verifier' in public:
        public['verifier'] = {k:v for k,v in public['verifier'].items() if k in VERIFIER_FIELDS}
    public['claim_assessments'] = []
    for item in summary.get('claim_assessments', []):
        clean = {k: v for k, v in item.items() if k in CLAIM_FIELDS}
        clean['excerpt_sha256'] = hashlib.sha256(item.get('excerpt', '').encode()).hexdigest()
        public['claim_assessments'].append(clean)
    return redact_tree(public)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('run_id')
    parser.add_argument('--reviewed', action='store_true', help='Assert researcher has inspected metadata for privacy')
    args = parser.parse_args()
    import uuid
    try: uuid.UUID(args.run_id)
    except ValueError: parser.error('run_id must be a UUID')
    if not args.reviewed: parser.error('Inspect private summary and use --reviewed; no automatic publication')
    p = ROOT/'.private/runs'/args.run_id/'summary.json'
    result = public_summary(json.loads(p.read_text(encoding='utf-8')))
    text = json.dumps(result, indent=2)+'\n'
    if has_obvious_private_data(text): parser.error('Privacy scanner found unresolved private-data pattern')
    dest = ROOT/'results/runs'
    dest.mkdir(parents=True, exist_ok=True)
    (dest/(args.run_id+'.json')).write_text(text, encoding='utf-8')
    print('Exported metadata only. Git publishing remains a separate step.')

if __name__ == '__main__': main()
