"""Current-version qualification of existing test timeouts and upstream fixture paths."""
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import time
import uuid

from runners.run_client_tests import (ROOT, UPSTREAM_COMMIT, check_upstream,
    client_test_env, parse_output, prepare_portable_control, run_serial_files, tree_hash)
from runners.run_free_screen import engine_289, ENGINE_289_SHA256
from runners.run_study import invoke

ARMS = [('unmodified-full', 1), ('portable-full', 2), ('portable-serial', 1),
        ('unmodified-register', 3), ('portable-register', 3)]
FOLLOWUP_ARMS = [('unmodified-register', 3), ('portable-register', 3), ('portable-serial', 1)]


def prepare(source, target, arm):
    if arm.startswith('portable'):
        prepare_portable_control(source, 'diff', target)
    else:
        shutil.copytree(source, target)
    if arm.endswith('register'):
        for path in target.rglob('*'):
            if path.name.endswith(('.test.ts', '.test.tsx')) and path != target/'tests/register.test.ts':
                path.unlink()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--upstream', required=True, type=Path)
    parser.add_argument('--continue-after-incomplete', action='store_true',
        help='Protocol 1.0.1 fixed continuation: registration file controls then serial suite; no full-dispatch retry')
    args = parser.parse_args()
    if os.name != 'nt': parser.error('This protocol is registered for Windows')
    source = check_upstream(args.upstream.resolve(), 'diff')
    cli, env = engine_289(), client_test_env()
    env['DISABLE_UPDATES'] = '1'
    version = subprocess.check_output([cli, '--version'], env=env, text=True).strip()
    if version.split()[0] != '2.1.289': parser.error('Engine differs from protocol')
    cycle = ROOT/'.private/issue-qualification'/str(uuid.uuid4())
    cycle.mkdir(parents=True)
    protocol = ROOT/'reports/issue-qualification-protocol.json'
    shutil.copy2(protocol, cycle/'protocol.json')
    shutil.copy2(args.upstream.resolve()/'LICENSE.md', cycle/'UPSTREAM-LICENSE.md')
    for arm, repetitions in FOLLOWUP_ARMS if args.continue_after_incomplete else ARMS:
        run_id = str(uuid.uuid4())
        private = cycle/arm
        target = private/'plugin'
        prepare(source, target, arm)
        if tree_hash(source/'hooks') != tree_hash(target/'hooks'):
            raise ValueError('Production hooks changed')
        record = {'schema_version': '1.0.0', 'run_id': run_id,
            'date': dt.datetime.now(dt.timezone.utc).isoformat(), 'kind': 'official-client-test-engine',
            'suite': 'diff', 'selection': arm, 'version': version, 'platform': 'win32',
            'upstream_commit': UPSTREAM_COMMIT, 'upstream_mod_sha256': tree_hash(source),
            'executed_tree_sha256': tree_hash(target), 'hooks_implementation_unchanged': True,
            'original_register_test_sha256': hashlib.sha256((source/'tests/register.test.ts').read_bytes()).hexdigest(),
            'executed_register_test_sha256': hashlib.sha256((target/'tests/register.test.ts').read_bytes()).hexdigest(),
            'protocol_sha256': hashlib.sha256(protocol.read_bytes()).hexdigest(),
            'executable_sha256': ENGINE_289_SHA256, 'per_test_timeout_ms': 5000, 'instrumented': False,
            'dispatch': 'sequential-test-files' if arm.endswith('serial') else 'engine-default',
            'model_calls': 0, 'coding_trials': 0, 'billed_model_cost_usd': 0,
            'scope': 'Official native test runner and original upstream test fixture; no production merge defect inferred',
            'repetitions': []}
        for trial in range(1, repetitions+1):
            start = time.monotonic()
            if arm.endswith('serial'):
                raw, parsed, code, timeout = run_serial_files(target, private, env, 120, trial, cli=cli)
            else:
                out, err, code, timeout = invoke([cli, 'plugin', 'test', str(target)], '', private, env, 120)
                raw, parsed = out+'\n'+err, parse_output(out+'\n'+err)
            (private/f'trial-{trial}.log').write_text(raw, encoding='utf-8')
            parsed.update(trial=trial, process_exit_code=code, timed_out=timeout,
                elapsed_seconds=round(time.monotonic()-start, 2), log_sha256=hashlib.sha256(raw.encode()).hexdigest())
            record['repetitions'].append(parsed)
            (private/'summary.json').write_text(json.dumps(record, indent=2)+'\n', encoding='utf-8')
            print(json.dumps({'cycle': cycle.name, 'arm': arm, 'trial': trial,
                'passed': parsed['passed'], 'failed': parsed['failed'], 'complete': parsed['complete']}), flush=True)
            if timeout or not parsed['complete'] or (code != 0 and not parsed['failed']): raise SystemExit(2)
        # Complete functional/timeout failures are retained while registered controls continue.
    print(json.dumps({'cycle': cycle.name, 'status': 'all-registered-arms-completed'}), flush=True)


if __name__ == '__main__': main()
