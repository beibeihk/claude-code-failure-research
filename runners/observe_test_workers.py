"""Separate Windows-only worker-observation arm; never capture command lines."""
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
import uuid

from runners.run_client_tests import ROOT, CLI_VERSION, UPSTREAM_COMMIT, check_upstream, client_test_env, parse_output, prepare_portable_control, tree_hash


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--upstream', required=True, type=Path)
    args = parser.parse_args()
    if os.name != 'nt': parser.error('Worker observer is registered for native Windows only.')
    source = check_upstream(args.upstream.resolve(), 'diff')
    env = client_test_env()
    version = subprocess.check_output(['claude', '--version'], env=env, text=True).strip()
    if version.split()[0] != CLI_VERSION: parser.error('Unregistered client version.')
    run_id = str(uuid.uuid4())
    private = ROOT/'.private/client-tests'/run_id
    private.mkdir(parents=True)
    target = prepare_portable_control(source, 'diff', private/'plugin')
    (private/'UPSTREAM-LICENSE.md').write_bytes((args.upstream.resolve()/'LICENSE.md').read_bytes())
    start = time.monotonic()
    process = subprocess.Popen(['claude', 'plugin', 'test', str(target)], cwd=private, env=env,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8',
                               creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
    observer_source = (ROOT/'runners/sample_test_workers.ps1').read_text(encoding='utf-8')
    observer_command = '& {\n'+observer_source+'\n} -CliRootPid '+str(process.pid)
    observer = subprocess.Popen(['powershell', '-NoProfile', '-Command', observer_command], env=env,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')
    timed_out = False
    try:
        stdout, stderr = process.communicate(timeout=150)
    except subprocess.TimeoutExpired:
        timed_out = True
        subprocess.run(['taskkill', '/PID', str(process.pid), '/T', '/F'], capture_output=True)
        stdout, stderr = process.communicate(timeout=10)
    observed, observer_errors = observer.communicate(timeout=30)
    raw = stdout+'\n'+stderr
    (private/'trial-1.log').write_text(raw, encoding='utf-8')
    (private/'worker-samples.jsonl').write_text(observed, encoding='utf-8')
    (private/'observer.stderr.txt').write_text(observer_errors, encoding='utf-8')
    samples = [json.loads(line) for line in observed.splitlines() if line.strip()]
    counts = parse_output(raw)
    counts.update({'trial':1, 'process_exit_code':process.returncode, 'timed_out':timed_out,
                   'elapsed_seconds':round(time.monotonic()-start,2),
                   'log_sha256':hashlib.sha256(raw.encode()).hexdigest()})
    record = {'schema_version':'1.0.0', 'run_id':run_id, 'date':dt.datetime.now(dt.timezone.utc).isoformat(),
              'kind':'official-client-test-engine', 'suite':'diff', 'selection':'upstream-worker-observation',
              'version':version, 'platform':'win32', 'upstream_commit':UPSTREAM_COMMIT,
              'upstream_mod_sha256':tree_hash(source), 'executed_tree_sha256':tree_hash(target),
              'hooks_implementation_unchanged':tree_hash(source/'hooks')==tree_hash(target/'hooks'),
              'model_calls':0, 'coding_trials':0, 'billed_model_cost_usd':0, 'per_test_timeout_ms':5000,
              'instrumented':True, 'worker_observation':{'observer_exit_code':observer.returncode,
                 'peak_descendant_count':max((s['descendant_count'] for s in samples),default=None),
                 'samples':samples, 'command_lines_captured':False,
                 'limitation':'Process counts are sampled for this CLI process tree only; observer load may affect elapsed time.'},
              'repetitions':[counts]}
    (private/'summary.json').write_text(json.dumps(record,indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'run_id':run_id,'passed':counts['passed'],'failed':counts['failed'],
                      'peak_descendants':record['worker_observation']['peak_descendant_count']}))
    if observer.returncode or timed_out or not counts['complete']: raise SystemExit(2)
    if counts['failed']: raise SystemExit(1)


if __name__ == '__main__': main()
