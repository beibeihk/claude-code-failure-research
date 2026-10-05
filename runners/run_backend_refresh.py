"""X2: unchanged Git backend with captured real commit/checkout snapshots.

No inference or production transport. Keep all fixture paths and raw replies private.
"""
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

from runners.run_client_tests import ROOT, UPSTREAM_COMMIT, check_upstream, client_test_env, parse_output, tree_hash
from runners.run_free_followup import prepare
from runners.run_free_screen import DISCOVERY, STATUS, ENGINE_289_SHA256, engine_289, entries, git, init, write
from runners.run_study import invoke

# Registered pinned source argv, checked by the unchanged backend at replay.
DIFF = ['--no-optional-locks', '-c', 'diff.relative=false', '-c',
        'core.quotePath=false', 'diff', '--no-ext-diff', '--no-textconv',
        '--ignore-submodules=dirty', '--submodule=short']
HUNKS = ['--no-renames', '--src-prefix=a/', '--dst-prefix=b/', '--raw', '-z', '-p']
UNTRACKED = ['--no-optional-locks', 'ls-files', '-z', '--others', '--exclude-standard', '--full-name']
PATHS = ['plain.txt', 'with spaces.txt', '税收.txt']


def snapshot(repo, label, changes):
    discovery = git(repo, *DISCOVERY)
    top, own, common = discovery['stdout'].splitlines()
    repository = {'toplevel': top, 'gitDir': own, 'commonDir': common}
    lead = ['--git-dir='+own, '--work-tree='+top]
    calls = []

    def capture(argv, pinned=True):
        source_argv = [*(lead if pinned else []), *argv]
        answer = git(repo, *source_argv)
        options = {'timeoutMs': 5000, 'env': {'LC_ALL': 'C', 'LANGUAGE': ''}}
        if pinned: options['cwd'] = top
        calls.append({'argv': ['git', *source_argv], 'init': options, 'answer': answer})
        return answer

    capture(DISCOVERY, False)
    capture(STATUS)
    capture([*DIFF, 'HEAD', '--shortstat'])
    numstat = capture([*DIFF, 'HEAD', '--numstat', '-z'])
    untracked = capture(UNTRACKED)
    if untracked['stdout']: raise ValueError('Registered fixture has unexpected untracked files')
    ordered = []
    for row in numstat['stdout'].split('\0'):
        if not row: continue
        added, removed, name = row.split('\t', 2)
        if (added, removed) != ('1', '1'): raise ValueError('Not the registered one-line replacement')
        ordered.append(name)
    if sorted(ordered) != sorted(changes): raise ValueError('Git path oracle disagrees with registered edits')
    expected_files, expected_hunks = [], []
    for index, name in enumerate(ordered):
        before = git(repo, 'show', 'HEAD:'+name)['stdout']
        after = (repo/name).read_bytes().decode('utf-8')
        if (before, after) != changes[name]: raise ValueError('Actual commit/file bytes disagree with oracle')
        if before.count('\n') != 1 or after.count('\n') != 1:
            raise ValueError('Oracle is only registered for single-line LF files')
        lines = ['-'+before[:-1], '+'+after[:-1]]
        if index != len(ordered)-1: lines.append(' ')
        expected_files.append({'path': name, 'renamedFrom': None, 'added': 1, 'removed': 1,
                               'isBinary': False, 'isUntracked': False, 'isPreSession': False})
        expected_hunks.append([name, {'hunks': [{'oldStart': 1, 'newStart': 1, 'lines': lines}],
                                      'isTruncated': False, 'isLarge': False}])
    if ordered:
        capture(['--literal-pathspecs', *DIFF, *HUNKS, 'HEAD', '--', *ordered])
    return {'label': label, 'repository': repository, 'calls': calls,
            'git_entries': entries(Path(own)),
            'oid': git(repo, 'rev-parse', '--verify', '--quiet', 'HEAD')['stdout'].strip(),
            'expected_files': expected_files, 'expected_hunks': expected_hunks,
            'expected_stats': {'filesCount': len(ordered), 'linesAdded': len(ordered), 'linesRemoved': len(ordered)}}


def scenario(folder, linked=False):
    primary, repo = folder/'primary', folder/'primary'
    init(primary, {name: 'base='+name+'\n' for name in PATHS})
    git(primary, 'branch', 'checkpoint')
    if linked:
        repo = folder/'linked'
        git(primary, 'worktree', 'add', '-b', 'linked', str(repo), 'main')
    changes = {name: ('base='+name+'\n', 'committed='+name+'\n') for name in PATHS[:2]}
    for name, (_, after) in changes.items(): write(repo/name, after)
    states = [snapshot(repo, 'before-commit', changes)]
    git(repo, 'commit', '-am', 'first advance')
    states.append(snapshot(repo, 'after-commit-clean', {}))
    write(repo/PATHS[0], 'after-commit='+PATHS[0]+'\n')
    states.append(snapshot(repo, 'after-commit-edited', {PATHS[0]: (changes[PATHS[0]][1], 'after-commit='+PATHS[0]+'\n')}))
    git(repo, 'commit', '-am', 'second advance')
    git(repo, 'checkout', 'checkpoint')
    states.append(snapshot(repo, 'after-checkout-clean', {}))
    write(repo/PATHS[2], 'after-checkout='+PATHS[2]+'\n')
    states.append(snapshot(repo, 'after-checkout-edited', {PATHS[2]: ('base='+PATHS[2]+'\n', 'after-checkout='+PATHS[2]+'\n')}))
    oids = [state['oid'] for state in states]
    if not (oids[0] != oids[1] == oids[2] and oids[2] != oids[3] == oids[4] == oids[0]):
        raise ValueError('Real commit/checkout identity oracle differs from protocol')
    if (states[0]['repository']['gitDir'] != states[0]['repository']['commonDir']) != linked:
        raise ValueError('Real repository kind differs from protocol')
    return {'kind': 'linked' if linked else 'ordinary', 'states': states}


def build_backend_data(folder):
    return {'scenarios': [scenario(folder/'ordinary'), scenario(folder/'linked', True)]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--upstream', required=True, type=Path)
    args = parser.parse_args()
    if os.name != 'nt': parser.error('Registered native engine is win32-x64')
    source = check_upstream(args.upstream.resolve(), 'diff')
    cli, env = engine_289(), client_test_env()
    env['DISABLE_UPDATES'] = '1'
    version = subprocess.check_output([cli, '--version'], env=env, text=True).strip()
    if version.split()[0] != '2.1.289': parser.error('Engine differs from registered version')
    run_id = str(uuid.uuid4())
    private = ROOT/'.private/backend-refresh'/run_id
    private.mkdir(parents=True)
    protocol = ROOT/'reports/backend-refresh-protocol.json'
    shutil.copy2(protocol, private/'protocol.json')
    shutil.copy2(args.upstream.resolve()/'LICENSE.md', private/'UPSTREAM-LICENSE.md')
    record = {'schema_version': '1.0.0', 'run_id': run_id,
        'date': dt.datetime.now(dt.timezone.utc).isoformat(), 'kind': 'official-client-test-engine',
        'suite': 'diff', 'selection': 'X2', 'version': version, 'upstream_commit': UPSTREAM_COMMIT,
        'upstream_mod_sha256': tree_hash(source), 'hooks_source_sha256': tree_hash(source/'hooks'),
        'authored_test_sha256': hashlib.sha256((ROOT/'research-tests/free-followup/backend-refresh.test.ts').read_bytes()).hexdigest(),
        'protocol_sha256': hashlib.sha256(protocol.read_bytes()).hexdigest(),
        'executable_sha256': ENGINE_289_SHA256,
        'model_calls': 0, 'coding_trials': 0, 'billed_model_cost_usd': 0, 'per_test_timeout_ms': 5000,
        'scope': 'Same unchanged source backend across captured real commit/checkout snapshots; no live transport, UI or model trials',
        'repetitions': []}
    for batch in (1, 2):
        batch_dir = private/f'batch-{batch}'
        data = build_backend_data(batch_dir/'fixtures')
        (batch_dir/'captures.json').write_text(json.dumps(data, indent=2)+'\n', encoding='utf-8')
        target = batch_dir/'diff'
        prepare(source, target, 'backend-refresh.test.ts', data)
        if tree_hash(target/'hooks') != record['hooks_source_sha256']:
            raise ValueError('Functional hooks changed')
        executed_hash = tree_hash(target)
        start = time.monotonic()
        out, err, code, timeout = invoke([cli, 'plugin', 'test', str(target)], '', private, env, 120)
        raw = out+'\n'+err
        (batch_dir/'native.log').write_text(raw, encoding='utf-8')
        parsed = parse_output(raw)
        parsed.update(trial=batch, batch=batch, process_exit_code=code, timed_out=timeout,
            elapsed_seconds=round(time.monotonic()-start, 2), log_sha256=hashlib.sha256(raw.encode()).hexdigest(),
            executed_tree_sha256=executed_hash, hooks_implementation_unchanged=True,
            capture_sha256=hashlib.sha256(json.dumps(data).encode()).hexdigest())
        record['repetitions'].append(parsed)
        (private/'summary.json').write_text(json.dumps(record, indent=2)+'\n', encoding='utf-8')
        print(json.dumps({'run_id': run_id, 'batch': batch, 'passed': parsed['passed'],
            'failed': parsed['failed'], 'complete': parsed['complete']}), flush=True)
        if timeout or not parsed['complete'] or (code != 0 and not parsed['failed']): raise SystemExit(2)
    raise SystemExit(1 if any(r['failed'] for r in record['repetitions']) else 0)


if __name__ == '__main__': main()
