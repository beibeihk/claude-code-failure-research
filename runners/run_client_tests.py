"""Run Claude Code's official mod test engine without login or model requests.

Anthropic source is read from a separately obtained pinned official checkout.
Private overlays keep its license and implementation out of our MIT repository.
"""
import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
import uuid

from runners.run_study import invoke

ROOT = Path(__file__).resolve().parents[1]
UPSTREAM_COMMIT = '1c229fcd1e1e4e452e29a8f116b45fe4cfe2c528'
CLI_VERSION = '2.1.288'
SUITES = ('agents-md', 'diff', 'telemetry', 'sec-default')


def client_test_env(inherited=None):
    env = dict(os.environ if inherited is None else inherited)
    for key in list(env):
        if (key.startswith('ANTHROPIC_') or key.startswith('CLAUDE_CODE_')
                or key.startswith('CLAUDE_') or key == 'CLAUDECODE'):
            if key != 'CLAUDE_CODE_GIT_BASH_PATH':
                env.pop(key)
    # Defense in depth: any accidental provider request targets a closed local
    # endpoint. The test engine answers all world interactions from hooks.
    env.update({'ANTHROPIC_BASE_URL': 'http://127.0.0.1:1',
                'DISABLE_TELEMETRY': '1', 'DISABLE_ERROR_REPORTING': '1',
                'DISABLE_AUTOUPDATER': '1',
                'CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC': '1'})
    return env


def parse_output(output):
    plain = re.sub(r'\x1b\[[0-9;]*[A-Za-z]', '', output)
    passed = re.findall(r'^\s*\(pass\) (.+?)(?: \[[0-9.]+ms\])?\s*$', plain, re.M)
    failed = re.findall(r'^\s*\(fail\) (.+?)(?: \[[0-9.]+ms\])?\s*$', plain, re.M)
    footer = re.search(r'Ran (\d+) tests across (\d+) files?\.', plain)
    observations = []
    for line in plain.splitlines():
        if line.startswith('RESEARCH_OBSERVATION '):
            observations.append(json.loads(line.removeprefix('RESEARCH_OBSERVATION ')))
    return {'passed': len(passed), 'failed': len(failed), 'failed_tests': failed,
            'tests_run': int(footer.group(1)) if footer else None,
            'files_run': int(footer.group(2)) if footer else None,
            'observations': observations,
            'complete': bool(footer and int(footer.group(1)) > 0 and int(footer.group(1)) == len(passed) + len(failed))}


def tree_hash(folder):
    digest = hashlib.sha256()
    for path in sorted(p for p in folder.rglob('*') if p.is_file()):
        digest.update(path.relative_to(folder).as_posix().encode())
        digest.update(b'\0')
        digest.update(path.read_bytes())
        digest.update(b'\0')
    return digest.hexdigest()


def check_upstream(upstream, suite):
    def git(*args):
        return subprocess.check_output(['git', '-C', str(upstream), *args], text=True).strip()
    if git('rev-parse', 'HEAD') != UPSTREAM_COMMIT:
        raise ValueError('Upstream differs from the pinned commit; preregister a revision first.')
    if git('status', '--porcelain', '--untracked-files=all', '--', 'mods/'+suite, 'LICENSE.md'):
        raise ValueError('Upstream mod or license has local changes; use an unmodified checkout.')
    remote = git('remote', 'get-url', 'origin')
    remote = remote.rstrip('/').removesuffix('.git')
    if remote not in ('https://github.com/anthropics/claude-code', 'git@github.com:anthropics/claude-code'):
        raise ValueError('Expected an official anthropics/claude-code checkout.')
    return upstream / 'mods' / suite


def prepare_overlay(source, suite, destination):
    own_tests = ROOT / 'research-tests' / suite
    if not own_tests.is_dir():
        raise ValueError('No authored tests for this suite; use --selection upstream.')
    shutil.copytree(source, destination)
    for path in destination.rglob('*'):
        if path.name.endswith(('.test.ts', '.test.tsx')):
            path.unlink()
    for path in own_tests.glob('*.test.ts'):
        shutil.copy2(path, destination / 'tests' / path.name)
    return destination


def prepare_portable_control(source, suite, destination):
    if suite != 'diff':
        raise ValueError('Portable upstream control is registered only for diff.')
    shutil.copytree(source, destination)
    test_file = destination / 'tests' / 'register.test.ts'
    text = test_file.read_text(encoding='utf-8')
    original = "const isGitDir = e.path === '/work/.git'"
    revised = "const isGitDir = e.path.replaceAll('\\\\', '/').replace(/^[A-Za-z]:/, '') === '/work/.git'"
    if text.count(original) != 1:
        raise ValueError('Pinned virtual fixture location changed; refuse an ambiguous patch.')
    test_file.write_text(text.replace(original, revised), encoding='utf-8')
    return destination


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--upstream', required=True, type=Path)
    parser.add_argument('--suite', choices=SUITES, default='agents-md')
    parser.add_argument('--selection', choices=('upstream', 'research', 'upstream-portable-control'), default='research')
    parser.add_argument('--repetitions', type=int, default=1)
    parser.add_argument('--timeout-seconds', type=int, default=120)
    args = parser.parse_args()
    if args.repetitions < 1 or args.timeout_seconds < 1:
        parser.error('Counts and timeout must be positive.')
    if args.suite == 'diff' and args.selection == 'research' and os.name != 'nt':
        parser.error('The authored virtual-path diagnostic is registered for native Windows only; upstream suites can run on other platforms.')
    source = check_upstream(args.upstream.resolve(), args.suite)
    env = client_test_env()
    version = subprocess.check_output(['claude', '--version'], text=True, env=env).strip()
    if version.split()[0] != CLI_VERSION:
        parser.error('CLI differs from the registered version; refresh the protocol first.')
    run_id = str(uuid.uuid4())
    private = ROOT / '.private' / 'client-tests' / run_id
    private.mkdir(parents=True)
    if args.selection == 'research':
        target = prepare_overlay(source, args.suite, private/'plugin')
    elif args.selection == 'upstream-portable-control':
        target = prepare_portable_control(source, args.suite, private/'plugin')
    else:
        target = source
    # Preserve the upstream license with every private source overlay.
    if args.selection != 'upstream':
        shutil.copy2(args.upstream.resolve()/'LICENSE.md', private/'UPSTREAM-LICENSE.md')
    record = {'schema_version': '1.0.0', 'run_id': run_id,
              'date': dt.datetime.now(dt.timezone.utc).isoformat(),
              'kind': 'official-client-test-engine', 'suite': args.suite,
              'selection': args.selection, 'version': version, 'platform': sys.platform,
              'upstream_commit': UPSTREAM_COMMIT, 'upstream_mod_sha256': tree_hash(source),
              'executed_tree_sha256': tree_hash(target),
              'hooks_implementation_unchanged': tree_hash(source/'hooks') == tree_hash(target/'hooks'),
              'model_calls': 0, 'coding_trials': 0, 'billed_model_cost_usd': 0,
              'network_observation': 'not packet-captured; no model invocations in this command; loopback provider guard and nonessential traffic disabled',
              'repetitions': []}
    for trial in range(1, args.repetitions+1):
        start = time.monotonic()
        stdout, stderr, exit_code, timed_out = invoke(
            ['claude', 'plugin', 'test', str(target)], '', private, env, args.timeout_seconds)
        raw = stdout + '\n' + stderr
        (private/f'trial-{trial}.log').write_text(raw, encoding='utf-8')
        counts = parse_output(raw)
        counts.update({'trial': trial, 'process_exit_code': exit_code, 'timed_out': timed_out,
                       'elapsed_seconds': round(time.monotonic()-start, 2),
                       'log_sha256': hashlib.sha256(raw.encode()).hexdigest()})
        record['repetitions'].append(counts)
        print(json.dumps({'run_id': run_id, 'suite': args.suite, 'trial': trial,
                          'passed': counts['passed'], 'failed': counts['failed'],
                          'complete': counts['complete']}), flush=True)
        if timed_out or not counts['complete']:
            break
    (private/'summary.json').write_text(json.dumps(record, indent=2)+'\n', encoding='utf-8')
    # Public export remains a separate reviewed step: these labels and any
    # authored observation payload must be inspected before copying metadata.
    if any(r['timed_out'] or not r['complete'] for r in record['repetitions']):
        raise SystemExit(2)
    if any(r['failed'] for r in record['repetitions']):
        raise SystemExit(1)
    if any(r['process_exit_code'] != 0 for r in record['repetitions']):
        raise SystemExit(2)


if __name__ == '__main__':
    main()
