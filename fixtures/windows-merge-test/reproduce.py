"""Isolate the original upstream Windows merge-state tests without model calls.

Run from this research checkout; separately obtain the official source and binary.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import uuid

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from runners.run_client_tests import check_upstream, client_test_env, parse_output, tree_hash
from runners.run_free_screen import ENGINE_289_SHA256
from runners.qualify_issue import prepare
from runners.run_study import invoke


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--upstream', type=Path, required=True)
    parser.add_argument('--engine', type=Path, required=True)
    parser.add_argument('--mode', choices=('literal', 'portable'), required=True)
    args = parser.parse_args()
    if os.name != 'nt': parser.error('Registered case is native Windows only')
    source = check_upstream(args.upstream.resolve(), 'diff')
    cli = args.engine.resolve()
    if hashlib.sha256(cli.read_bytes()).hexdigest() != ENGINE_289_SHA256:
        parser.error('Requires checksum-pinned official win32-x64 2.1.289')
    env = client_test_env()
    env['DISABLE_UPDATES'] = '1'
    version = subprocess.check_output([str(cli), '--version'], env=env, text=True).strip()
    if version.split()[0] != '2.1.289': parser.error('Unexpected engine version')
    private = ROOT/'.private/win-merge'/str(uuid.uuid4())
    target = private/'p'
    prepare(source, target, 'unmodified-register' if args.mode == 'literal' else 'portable-register')
    shutil.copy2(args.upstream.resolve()/'LICENSE.md', private/'UPSTREAM-LICENSE.md')
    if tree_hash(source/'hooks') != tree_hash(target/'hooks'):
        raise ValueError('Production hooks differ')
    executed_hash = tree_hash(target)
    out, err, code, timeout = invoke([str(cli), 'plugin', 'test', str(target)], '', private, env, 120)
    raw = out+'\n'+err
    (private/'native.log').write_text(raw, encoding='utf-8')
    parsed = parse_output(raw)
    record = {'mode': args.mode, 'version': version, 'model_calls': 0,
              'executed_tree_sha256': executed_hash, 'process_exit_code': code,
              'timed_out': timeout, 'log_sha256': hashlib.sha256(raw.encode()).hexdigest(), **parsed}
    (private/'summary.json').write_text(json.dumps(record, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k: record[k] for k in ('mode', 'version', 'model_calls', 'passed', 'failed', 'complete', 'timed_out')}))
    raise SystemExit(2 if timeout or not parsed['complete'] else 1 if parsed['failed'] else 0)


if __name__ == '__main__': main()
