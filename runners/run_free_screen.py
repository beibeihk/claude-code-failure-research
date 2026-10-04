"""Three bounded, no-model component screens against captured real fixtures.

The native mod engine replays responses collected from actual local files/Git.
It does not exercise production filesystem/process transport or Claude models.
All fixtures, source overlays and raw outputs stay in .private until review.
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

from runners.run_client_tests import (ROOT, UPSTREAM_COMMIT, CLI_VERSION,
    check_upstream, client_test_env, parse_output, tree_hash)
from runners.run_study import invoke

DISCOVERY = ['--no-optional-locks', 'rev-parse', '--path-format=absolute',
             '--show-toplevel', '--git-dir', '--git-common-dir']
STATUS = ['--no-optional-locks', 'status', '--porcelain', '-z',
          '--untracked-files=all', '--no-renames', '--ignore-submodules=dirty']


def git(repo, *argv, expected=0):
    """Only fixture commands; no shell, user/global config, hooks or signing."""
    env = client_test_env()
    for key in list(env):
        if key.startswith('GIT_'): env.pop(key)
    env.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM='1',
               GIT_TERMINAL_PROMPT='0', LC_ALL='C', LANG='C')
    command = ['git', '-c', 'user.name=Research Fixture', '-c',
               'user.email=fixture@example.invalid', '-c', 'commit.gpgsign=false',
               '-c', 'core.autocrlf=false', '-c', 'core.hooksPath='+os.devnull, *argv]
    result = subprocess.run(command, cwd=repo, env=env, capture_output=True, timeout=30)
    if result.returncode != expected:
        raise RuntimeError('Fixture Git operation had an unexpected exit status: '+str(argv[0]))
    return {'exitCode': result.returncode, 'stdout': result.stdout.decode('utf-8'),
            'stderr': result.stderr.decode('utf-8')}


def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content if isinstance(content, bytes) else content.encode('utf-8'))


def init(repo, files):
    repo.mkdir(parents=True)
    git(repo, 'init', '-b', 'main')
    for relative, content in files.items(): write(repo/relative, content)
    git(repo, 'add', '--all')
    git(repo, 'commit', '-m', 'synthetic base')


def entries(path):
    return {p.name: ('other' if p.is_symlink() else 'dir' if p.is_dir() else 'file')
            for p in path.iterdir()}


def capture_state(repo, label, transient):
    answer = git(repo, *DISCOVERY)
    top, own, common = answer['stdout'].splitlines()
    directory = Path(own)
    listings = {own.replace('\\', '/'): entries(directory)}
    for name in ('rebase-merge', 'rebase-apply'):
        if (directory/name).is_dir():
            listings[(own+'/'+name).replace('\\', '/')] = entries(directory/name)
    return {'label': label, 'discovery': answer,
            'repository': {'toplevel': top, 'gitDir': own, 'commonDir': common},
            'listings': listings, 'expected_transient': transient,
            'marker_names': sorted(set(listings[own.replace('\\', '/')]) &
                {'MERGE_HEAD', 'CHERRY_PICK_HEAD', 'REVERT_HEAD', 'REBASE_HEAD', 'rebase-merge', 'rebase-apply'})}


def build_git_states(folder):
    repo, linked = folder/'ordinary', folder/'linked'
    init(repo, {'conflict.txt': 'value=base\n'})
    git(repo, 'branch', 'topic')
    write(repo/'conflict.txt', 'value=main\n')
    git(repo, 'commit', '-am', 'main edit')
    git(repo, 'worktree', 'add', str(linked), 'topic')
    write(linked/'conflict.txt', 'value=topic\n')
    git(linked, 'commit', '-am', 'topic edit')
    states = [capture_state(repo, 'ordinary-clean', False)]
    git(repo, 'merge', '--no-edit', 'topic', expected=1)
    if not (Path(states[0]['repository']['gitDir'])/'MERGE_HEAD').is_file():
        raise ValueError('Real conflict did not create MERGE_HEAD')
    states.append(capture_state(repo, 'ordinary-merge-conflict', True))
    git(repo, 'merge', '--abort')
    states.append(capture_state(repo, 'ordinary-merge-aborted', False))
    states.append(capture_state(linked, 'linked-clean', False))
    git(linked, 'merge', '--no-edit', 'main', expected=1)
    states.append(capture_state(linked, 'linked-merge-conflict', True))
    if Path(states[-1]['repository']['commonDir']).joinpath('MERGE_HEAD').exists():
        raise ValueError('Linked marker unexpectedly lives in commonDir')
    git(linked, 'merge', '--abort')
    states.append(capture_state(linked, 'linked-merge-aborted', False))
    git(linked, 'rebase', 'main', expected=1)
    states.append(capture_state(linked, 'linked-rebase-conflict', True))
    git(linked, 'rebase', '--abort')
    states.append(capture_state(linked, 'linked-rebase-aborted', False))
    for state in states:
        if state['expected_transient'] != bool(state['marker_names']):
            raise ValueError('Fixture state/marker oracle disagrees')
    return states


def build_git_paths(folder):
    repo = folder/'paths'
    names = ['plain.ts', 'with spaces.ts', '你好.ts']
    init(repo, {**{name: 'value=0\n' for name in names}, 'binary.dat': b'\0old'})
    clean = git(repo, *STATUS)
    for name in names: write(repo/name, 'value=1\n')
    write(repo/'binary.dat', b'\0new')
    dirty = git(repo, *STATUS)
    numstat = git(repo, '--no-optional-locks', 'diff', '--numstat', '-z', '--no-renames', 'HEAD')
    patches = git(repo, '--no-optional-locks', 'diff', '--raw', '-z', '-p', '--no-renames', 'HEAD', '--', *names)
    rename_repo = folder/'rename'
    init(rename_repo, {'old name.ts': 'unchanged=1\n'})
    git(rename_repo, 'mv', 'old name.ts', 'new name.ts')
    renamed = git(rename_repo, '--no-optional-locks', 'diff', '--cached', '--numstat', '-z', '-M', 'HEAD')
    return {'names': names, 'clean': clean, 'dirty': dirty, 'numstat': numstat,
            'patches': patches, 'rename': renamed}


def ancestor(path, directory, name):
    content = path.read_text(encoding='utf-8')
    return {'dir': str(directory), 'name': name, 'content': content,
            'parts': [{'path': str(path), 'content': content}]}


def build_instruction_case(folder, claude=False):
    root = folder/('claimed' if claude else 'plain')
    for relative, content in {'AGENTS.md': 'Root: preserve the API.\n',
            'src/AGENTS.md': 'Nested: preserve tests.\n',
            'src/lib/AGENTS.md': 'Deep: run checks.\n',
            'src/lib/file.ts': 'export const value = 1\n'}.items():
        write(root/relative, content)
    if claude: write(root/'src/CLAUDE.md', 'Use the local CLAUDE policy.\n')
    sibling = root.with_name(root.name+'-sibling')/'file.ts'
    write(sibling, 'export const sibling = true\n')
    initial = [ancestor(root/'AGENTS.md', root, 'AGENTS.md')]
    nested = [ancestor(root/'src/AGENTS.md', root/'src', 'AGENTS.md'),
              ancestor(root/'src/lib/AGENTS.md', root/'src/lib', 'AGENTS.md')]
    claim = [ancestor(root/'src/CLAUDE.md', root/'src', 'CLAUDE.md')] if claude else []
    return {'root': str(root), 'read_path': str(root/'src/lib/file.ts'),
            'instruction_path': str(root/'src/AGENTS.md'),
            'sibling_path': str(sibling),
            'read_contents': {str(p): p.read_text(encoding='utf-8') for p in
                              (root/'src/lib/file.ts', root/'src/AGENTS.md', sibling)},
            'initial': initial, 'nested': nested, 'claude': claim,
            'expected_frames': ['Contents of '+f['parts'][0]['path']+':\n\n'+f['content']
                                for f in nested if not claude or f['dir'] != str(root/'src')]}


def build_data(folder):
    return {'states': build_git_states(folder), 'paths': build_git_paths(folder),
            'instructions': {'plain': build_instruction_case(folder),
                             'claimed': build_instruction_case(folder, True)},
            'discovery_argv': DISCOVERY, 'status_argv': STATUS}


def prepare(source, suite, destination, data):
    shutil.copytree(source, destination)
    for path in destination.rglob('*'):
        if path.name.endswith(('.test.ts', '.test.tsx')): path.unlink()
    shutil.copy2(ROOT/'research-tests/free-screen'/f'{suite}.test.ts',
                 destination/'tests/free-screen.test.ts')
    (destination/'tests/screen-data.ts').write_text(
        'export default '+json.dumps(data, ensure_ascii=True)+'\n', encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--upstream', required=True, type=Path)
    parser.add_argument('--batches', type=int, choices=(1, 2), default=2)
    args = parser.parse_args()
    if os.name != 'nt': parser.error('Native-engine screen is registered for Windows only; fixture oracle checks are portable')
    sources = {suite: check_upstream(args.upstream.resolve(), suite) for suite in ('diff', 'agents-md')}
    env = client_test_env()
    version = subprocess.check_output(['claude', '--version'], env=env, text=True).strip()
    if version.split()[0] != CLI_VERSION: parser.error('CLI differs from registered version')
    run_id = str(uuid.uuid4())
    private = ROOT/'.private/free-screen'/run_id
    private.mkdir(parents=True)
    shutil.copy2(args.upstream.resolve()/'LICENSE.md', private/'UPSTREAM-LICENSE.md')
    records = {suite: {'schema_version': '1.0.0', 'run_id': str(uuid.uuid4()),
        'screen_batch_id': run_id, 'date': dt.datetime.now(dt.timezone.utc).isoformat(),
        'kind': 'official-client-test-engine', 'suite': suite, 'selection': 'real-fixture-response-replay',
        'version': version, 'platform': os.sys.platform, 'upstream_commit': UPSTREAM_COMMIT,
        'upstream_mod_sha256': tree_hash(source), 'per_test_timeout_ms': 5000,
        'model_calls': 0, 'coding_trials': 0, 'billed_model_cost_usd': 0,
        'scope': 'Captured real filesystem/Git responses; component source and engine hooks; not production transport',
        'repetitions': []} for suite, source in sources.items()}
    for batch in range(1, args.batches+1):
        batch_dir = private/f'batch-{batch}'
        data = build_data(batch_dir/'fixtures')
        (batch_dir/'fixture-data.json').write_text(json.dumps(data, indent=2)+'\n', encoding='utf-8')
        proof = {'states': [{'label': s['label'], 'expected_transient': s['expected_transient'],
                             'marker_names': s['marker_names'],
                             'own_git_dir_differs_from_common': s['repository']['gitDir'] != s['repository']['commonDir']}
                            for s in data['states']], 'real_file_names': data['paths']['names']+['binary.dat'],
                 'fixture_data_sha256': hashlib.sha256(json.dumps(data).encode()).hexdigest()}
        for suite, source in sources.items():
            target = batch_dir/suite
            prepare(source, suite, target, data)
            if tree_hash(source/'hooks') != tree_hash(target/'hooks'):
                raise ValueError('Functional hook implementation changed')
            start = time.monotonic()
            out, err, code, timeout = invoke(['claude', 'plugin', 'test', str(target)], '', private, env, 120)
            raw = out+'\n'+err
            (batch_dir/f'{suite}.log').write_text(raw, encoding='utf-8')
            count = parse_output(raw)
            count.update(trial=batch, process_exit_code=code, timed_out=timeout,
                         elapsed_seconds=round(time.monotonic()-start, 2),
                         log_sha256=hashlib.sha256(raw.encode()).hexdigest(),
                         executed_tree_sha256=tree_hash(target), hooks_implementation_unchanged=True,
                         fixture_proof=proof)
            records[suite]['repetitions'].append(count)
            (private/f'{suite}-summary.json').write_text(json.dumps(records[suite], indent=2)+'\n', encoding='utf-8')
            print(json.dumps({'batch_id': run_id, 'suite': suite, 'batch': batch,
                              'passed': count['passed'], 'failed': count['failed'], 'complete': count['complete']}), flush=True)
            if not count['complete'] or timeout or (code != 0 and count['failed'] == 0):
                raise SystemExit(2)
    raise SystemExit(1 if any(r['failed'] for record in records.values() for r in record['repetitions']) else 0)


if __name__ == '__main__': main()
