"""Existing N1 option contrasts and N3 real HEAD/ref refresh-probe oracles.

Public source helpers and native hooks consume private captured responses;
no model inference, production transport or live UI polling is tested.
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

from runners.run_client_tests import ROOT, CLI_VERSION, UPSTREAM_COMMIT, check_upstream, client_test_env, parse_output, tree_hash
from runners.run_free_screen import build_instruction_case, entries, git, init, write, DISCOVERY, engine_289, ENGINE_289_SHA256
from runners.run_study import invoke

MODES = ('claude-md', 'claude-md-and-agents-md', 'managed-only')
VERIFY_HEAD = ['--no-optional-locks', 'rev-parse', '--verify', '--quiet', 'HEAD']


def build_option_data(folder):
    fixture = build_instruction_case(folder, True)
    root = Path(fixture['root'])
    write(root/'CLAUDE.md', 'Project CLAUDE policy.\n')
    handed = []
    for kind, relative, content in (
        ('managed', 'organization/CLAUDE.md', 'Managed policy.\n'),
        ('user', 'person/CLAUDE.md', 'User policy.\n'),
        ('project', 'claimed/CLAUDE.md', 'Project CLAUDE policy.\n'),
        ('local', 'claimed/CLAUDE.local.md', 'Local policy.\n'),
        ('memory', 'memory/MEMORY.md', 'Remember fixture details.\n')):
        path = folder/relative
        write(path, content)
        handed.append({'path': str(path), 'kind': kind, 'content': path.read_text(encoding='utf-8')})
    fixture['handed'] = handed
    fixture['all_nested_frames'] = ['Contents of '+f['parts'][0]['path']+':\n\n'+f['content'] for f in fixture['nested']]
    return fixture


def capture_head(repo, label):
    top, own, common = git(repo, *DISCOVERY)['stdout'].splitlines()
    normalize = lambda p: str(p).replace('\\', '/')
    roots = {Path(own), Path(common)}
    listings, texts, stamps, nanoseconds = {}, {}, {}, {}
    for base in roots:
        for directory in [base, *(p for p in base.rglob('*') if p.is_dir() and not p.is_symlink())]:
            listings[normalize(directory)] = entries(directory)
        # Only the head key's possible files; no need to read repository objects.
        names = ['HEAD', 'packed-refs', 'logs/HEAD']
        head = (Path(own)/'HEAD').read_text(encoding='utf-8')
        if head.startswith('ref: '): names.append(head[5:].strip())
        for name in names:
            path = base/name
            if path.is_file() and not path.is_symlink():
                key = normalize(path)
                texts[key] = path.read_text(encoding='utf-8')
                nanoseconds[key] = path.stat().st_mtime_ns
                stamps[key] = nanoseconds[key]/1_000_000
    answer = git(repo, *VERIFY_HEAD)
    return {'label': label, 'repository': {'toplevel': top, 'gitDir': own, 'commonDir': common},
            'listings': listings, 'texts': texts, 'stamps_ms': stamps, 'stamps_ns': nanoseconds,
            'head_answer': answer, 'oid': answer['stdout'].strip(),
            'own_head_text': texts[normalize(Path(own)/'HEAD')]}


def build_head_data(folder):
    repo, linked = folder/'ordinary', folder/'linked'
    init(repo, {'file.txt': 'base\n'})
    git(repo, 'branch', 'topic')
    states = [capture_head(repo, 'ordinary-initial'), capture_head(repo, 'ordinary-noop')]
    write(repo/'file.txt', 'main edit\n')
    git(repo, 'commit', '-am', 'main advance')
    states.append(capture_head(repo, 'ordinary-committed'))
    git(repo, 'checkout', 'topic')
    states.append(capture_head(repo, 'ordinary-branch-switched'))
    git(repo, 'checkout', '--detach', 'HEAD')
    states.append(capture_head(repo, 'ordinary-detached'))
    git(repo, 'pack-refs', '--all', '--prune')
    states.append(capture_head(repo, 'ordinary-packed'))
    git(repo, 'worktree', 'add', '-b', 'linked', str(linked), 'main')
    states.append(capture_head(linked, 'linked-initial'))
    write(linked/'file.txt', 'linked edit\n')
    git(linked, 'commit', '-am', 'linked advance')
    states.append(capture_head(linked, 'linked-committed'))
    git(linked, 'checkout', '-b', 'feature/税收')
    states.append(capture_head(linked, 'unicode-initial'))
    write(linked/'file.txt', 'unicode edit\n')
    git(linked, 'commit', '-am', 'unicode advance')
    states.append(capture_head(linked, 'unicode-committed'))
    pairs = [('ordinary-initial', 'ordinary-noop', False, False),
             ('ordinary-noop', 'ordinary-committed', True, True),
             ('ordinary-committed', 'ordinary-branch-switched', True, True),
             ('ordinary-branch-switched', 'ordinary-detached', True, False),
             ('ordinary-detached', 'ordinary-packed', True, False),
             ('linked-initial', 'linked-committed', True, True),
             ('unicode-initial', 'unicode-committed', True, True)]
    by_label = {s['label']: s for s in states}
    comparisons = []
    for before, after, key_changes, oid_changes in pairs:
        a, b = by_label[before], by_label[after]
        if (a['oid'] != b['oid']) != oid_changes: raise ValueError('Git identity oracle differs from registered operations')
        comparisons.append({'before': before, 'after': after, 'key_changes': key_changes,
                            'oid_changes': oid_changes,
                            'own_head_text_changed': a['own_head_text'] != b['own_head_text']})
    return {'states': states, 'comparisons': comparisons, 'verify_head_argv': VERIFY_HEAD}


def prepare(source, target, test_name, data, mode=None):
    shutil.copytree(source, target)
    for path in target.rglob('*'):
        if path.name.endswith(('.test.ts', '.test.tsx')): path.unlink()
    shutil.copy2(ROOT/'research-tests/free-followup'/test_name, target/'tests/free-followup.test.ts')
    (target/'tests/followup-data.ts').write_text('export default '+json.dumps(data, ensure_ascii=True)+'\n', encoding='utf-8')
    if mode is not None:
        manifest_path = target/'.claude-plugin/plugin.json'
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        manifest['userConfig']['instructionFiles']['default'] = mode
        manifest_path.write_text(json.dumps(manifest, indent=2)+'\n', encoding='utf-8')
        original = json.loads((source/'.claude-plugin/plugin.json').read_text(encoding='utf-8'))
        restored = json.loads(manifest_path.read_text(encoding='utf-8'))
        restored['userConfig']['instructionFiles']['default'] = original['userConfig']['instructionFiles']['default']
        if restored != original: raise ValueError('Option injection changed another manifest field')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--upstream', required=True, type=Path)
    parser.add_argument('--item', required=True, choices=('N1', 'N3'))
    parser.add_argument('--engine-289', action='store_true', help='Optional later extension: same registered cases on the private checksum-pinned engine')
    args = parser.parse_args()
    if os.name != 'nt': parser.error('Native screen is registered for Windows only')
    suite = 'agents-md' if args.item == 'N1' else 'diff'
    source = check_upstream(args.upstream.resolve(), suite)
    env = client_test_env()
    env['DISABLE_UPDATES'] = '1'
    cli = engine_289() if args.engine_289 else 'claude'
    expected_version = '2.1.289' if args.engine_289 else CLI_VERSION
    version = subprocess.check_output([cli, '--version'], env=env, text=True).strip()
    if version.split()[0] != expected_version: parser.error('CLI differs from registered version')
    run_id = str(uuid.uuid4())
    private = ROOT/'.private/free-followup'/run_id
    private.mkdir(parents=True)
    shutil.copy2(args.upstream.resolve()/'LICENSE.md', private/'UPSTREAM-LICENSE.md')
    test_name = 'options.test.ts' if args.item == 'N1' else 'head-key.test.ts'
    record = {'schema_version': '1.0.0', 'run_id': run_id,
        'date': dt.datetime.now(dt.timezone.utc).isoformat(), 'kind': 'official-client-test-engine',
        'suite': suite, 'selection': args.item, 'version': version, 'upstream_commit': UPSTREAM_COMMIT,
        'upstream_mod_sha256': tree_hash(source), 'hooks_source_sha256': tree_hash(source/'hooks'),
        'authored_test_sha256': hashlib.sha256((ROOT/'research-tests/free-followup'/test_name).read_bytes()).hexdigest(),
        'executable_sha256': ENGINE_289_SHA256 if args.engine_289 else None,
        'model_calls': 0, 'coding_trials': 0, 'billed_model_cost_usd': 0, 'per_test_timeout_ms': 5000,
        'scope': 'Native option hooks or unchanged source head-key helper with captured real fixture replies; no production transport/model trials',
        'repetitions': []}
    trial = 0
    for batch in (1, 2):
        batch_dir = private/f'batch-{batch}'
        data = build_option_data(batch_dir/'fixtures') if args.item == 'N1' else build_head_data(batch_dir/'fixtures')
        (batch_dir/'captures.json').write_text(json.dumps(data, indent=2)+'\n', encoding='utf-8')
        for mode in MODES if args.item == 'N1' else (None,):
            trial += 1
            injected = {**data, 'mode': mode} if mode is not None else data
            target = batch_dir/(mode or 'head-key')
            prepare(source, target, test_name, injected, mode)
            if tree_hash(target/'hooks') != record['hooks_source_sha256']:
                raise ValueError('Functional hooks changed')
            executed_hash = tree_hash(target)
            start = time.monotonic()
            out, err, code, timeout = invoke([cli, 'plugin', 'test', str(target)], '', private, env, 120)
            raw = out+'\n'+err
            (batch_dir/f'{mode or "head-key"}.log').write_text(raw, encoding='utf-8')
            parsed = parse_output(raw)
            parsed.update(trial=trial, batch=batch, option_mode=mode, process_exit_code=code,
                timed_out=timeout, elapsed_seconds=round(time.monotonic()-start, 2),
                log_sha256=hashlib.sha256(raw.encode()).hexdigest(), executed_tree_sha256=executed_hash,
                hooks_implementation_unchanged=True,
                capture_sha256=hashlib.sha256(json.dumps(data).encode()).hexdigest())
            record['repetitions'].append(parsed)
            (private/'summary.json').write_text(json.dumps(record, indent=2)+'\n', encoding='utf-8')
            print(json.dumps({'run_id': run_id, 'item': args.item, 'batch': batch, 'mode': mode,
                'passed': parsed['passed'], 'failed': parsed['failed'], 'complete': parsed['complete']}), flush=True)
            if timeout or not parsed['complete'] or (code != 0 and not parsed['failed']): raise SystemExit(2)
    raise SystemExit(1 if any(r['failed'] for r in record['repetitions']) else 0)


if __name__ == '__main__': main()
