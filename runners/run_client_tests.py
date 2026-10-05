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
    footer = re.search(r'Ran (\d+) tests? across (\d+) files?\.', plain)
    matches = list(re.finditer(r'^\s*\((pass|fail)\) (.+?)(?: \[([0-9.]+)ms\])?\s*$', plain, re.M))
    test_cases = []
    for ordinal, match in enumerate(matches):
        following = plain[match.end():matches[ordinal+1].start() if ordinal+1 < len(matches) else len(plain)]
        error_kind = None
        if match.group(1) == 'fail':
            if re.search(r'timed out after \d+ ms', following): error_kind = 'test-timeout'
            elif 'AssertionError' in following: error_kind = 'assertion'
            elif re.search(r'(?:Reference|Type|Syntax)Error:', following): error_kind = 'test-runtime-exception'
            else: error_kind = 'unknown'
        test_cases.append({'name': match.group(2), 'status': match.group(1),
                           'elapsed_ms': float(match.group(3)) if match.group(3) else None,
                           'error_kind': error_kind})
    observations = []
    for line in plain.splitlines():
        if line.startswith('RESEARCH_OBSERVATION '):
            observations.append(json.loads(line.removeprefix('RESEARCH_OBSERVATION ')))
    return {'passed': len(passed), 'failed': len(failed), 'failed_tests': failed,
            'tests_run': int(footer.group(1)) if footer else None,
            'files_run': int(footer.group(2)) if footer else None,
            'observations': observations, 'test_cases': test_cases,
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


FOCUSED_TESTS = (
    ('tests/register.test.ts', 'the start asks nothing of git and registers /diff'),
    ('tests/views/detail/detail-view.test.ts', 'each hunk draws as a diff Code named by the path'),
)


def prepare_focused_control(source, suite, destination, timeout_ms=None, instrument=False):
    """Extract two pinned upstream cases privately; keep their assertions intact."""
    if suite != 'diff':
        raise ValueError('Focused timeout investigation is registered only for diff.')
    if timeout_ms is not None and timeout_ms < 1:
        raise ValueError('Test timeout must be positive.')
    shutil.copytree(source, destination)
    selected = {}
    for relative, name in FOCUSED_TESTS:
        text = (source/relative).read_text(encoding='utf-8')
        marker = "  test('"+name+"', async ($, on) => {"
        if text.count(marker) != 1:
            raise ValueError('Pinned focused test changed; refuse extraction.')
        start = text.index(marker)
        end = text.index('\n  test(', start + len(marker))
        body = text[start:end].rstrip()
        describe_at = text.index("describe('")
        describe_end = text.index('\n', describe_at)
        header = text[:describe_end+1]
        if timeout_ms is not None:
            body = body.replace(marker, "  test('"+name+"', { timeoutMs: "+str(timeout_ms)+" }, async ($, on) => {", 1)
        if instrument:
            # Date is an ECMAScript global, unlike the unavailable Node process
            # global. These probes are a separate, explicitly instrumented arm.
            first = body.index('\n')
            body = body[:first+1]+"    const probeStart = Date.now()\n    const marks: { phase: string; elapsed_ms: number }[] = []\n    const mark = (phase: string) => marks.push({ phase, elapsed_ms: Date.now() - probeStart })\n"+body[first+1:]
            if relative == 'tests/register.test.ts':
                body = body.replace('    await $.session.start(Fixtures.SESSION)',
                                    "    mark('before-first-engine-call')\n    await $.session.start(Fixtures.SESSION)\n    mark('after-session-start')", 1)
            else:
                body = body.replace('    const tree = await $.ui.render(Fixtures.VIEW_PANE)',
                                    "    mark('before-first-engine-call')\n    const tree = await $.ui.render(Fixtures.VIEW_PANE)\n    mark('after-ui-render')", 1)
            closing = body.rfind('\n  })')
            if closing < 0: raise ValueError('Focused body closing changed.')
            body = body[:closing]+"\n    mark('assertions-complete')\n    console.log('RESEARCH_OBSERVATION ' + JSON.stringify({ case_name: "+json.dumps(name)+", marks }))"+body[closing:]
        selected[relative] = header+body+'\n})\n'
    for path in destination.rglob('*'):
        if path.name.endswith(('.test.ts', '.test.tsx')):
            path.unlink()
    for relative, content in selected.items():
        (destination/relative).write_text(content, encoding='utf-8')
    return destination


def run_serial_files(target, private, env, timeout_seconds, trial, cli='claude'):
    """Only this run's private overlay is renamed; original test bytes restored."""
    test_paths = sorted(p for p in target.rglob('*') if p.name.endswith(('.test.ts', '.test.tsx')))
    if not test_paths: raise ValueError('No test files to dispatch.')
    expected_hash = tree_hash(target)
    disabled = {p: p.with_name(p.name+'.inactive') for p in test_paths}
    logs, file_runs = [], []
    try:
        for path, inactive in disabled.items(): path.rename(inactive)
        for ordinal, path in enumerate(test_paths, 1):
            disabled[path].rename(path)
            try:
                started = time.monotonic()
                stdout, stderr, exit_code, timed_out = invoke(
                    [cli,'plugin','test',str(target)], '', private, env, timeout_seconds)
                raw = stdout+'\n'+stderr
                relative = path.relative_to(target).as_posix()
                (private/f'trial-{trial}-file-{ordinal}.log').write_text(raw, encoding='utf-8')
                logs.append('FILE '+relative+'\n'+raw)
                counts = parse_output(raw)
                counts.update({'file':relative, 'process_exit_code':exit_code, 'timed_out':timed_out,
                               'elapsed_seconds':round(time.monotonic()-started,2),
                               'log_sha256':hashlib.sha256(raw.encode()).hexdigest()})
                file_runs.append(counts)
            finally:
                path.rename(disabled[path])
            if timed_out or not counts['complete']: break
    finally:
        for path, inactive in disabled.items():
            if inactive.exists(): inactive.rename(path)
    if tree_hash(target) != expected_hash:
        raise RuntimeError('Private test overlay was not restored exactly.')
    raw = '\n'.join(logs)
    result = {'passed':sum(r['passed'] for r in file_runs), 'failed':sum(r['failed'] for r in file_runs),
              'failed_tests':[name for r in file_runs for name in r['failed_tests']],
              'tests_run':sum(r['tests_run'] or 0 for r in file_runs), 'files_run':len(file_runs),
              'test_cases':[c for r in file_runs for c in r['test_cases']],
              'observations':[o for r in file_runs for o in r['observations']],
              'complete':len(file_runs)==len(test_paths) and all(r['complete'] for r in file_runs),
              'file_runs':file_runs, 'overlay_restored':True}
    timed_out = any(r['timed_out'] for r in file_runs)
    exit_code = 2 if timed_out or not result['complete'] else 1 if result['failed'] else 0
    if any(r['process_exit_code']!=0 and not r['failed'] for r in file_runs): exit_code=2
    return raw, result, exit_code, timed_out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--upstream', required=True, type=Path)
    parser.add_argument('--suite', choices=SUITES, default='agents-md')
    parser.add_argument('--selection', choices=('upstream', 'research', 'upstream-portable-control', 'upstream-focused', 'upstream-serial-files'), default='research')
    parser.add_argument('--repetitions', type=int, default=1)
    parser.add_argument('--timeout-seconds', type=int, default=120)
    parser.add_argument('--test-timeout-ms', type=int, help='Focused control only: explicitly change the per-case deadline')
    parser.add_argument('--instrument', action='store_true', help='Focused control only: record synthetic phase timing')
    args = parser.parse_args()
    if args.repetitions < 1 or args.timeout_seconds < 1:
        parser.error('Counts and timeout must be positive.')
    if (args.test_timeout_ms is not None or args.instrument) and args.selection != 'upstream-focused':
        parser.error('Per-case deadlines and phase probes apply only to the focused control.')
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
    elif args.selection in ('upstream-portable-control', 'upstream-serial-files'):
        target = prepare_portable_control(source, args.suite, private/'plugin')
    elif args.selection == 'upstream-focused':
        target = prepare_focused_control(source, args.suite, private/'plugin', args.test_timeout_ms, args.instrument)
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
              'per_test_timeout_ms': args.test_timeout_ms or 5000,
              'instrumented': args.instrument,
              'dispatch': 'sequential-test-files' if args.selection=='upstream-serial-files' else 'engine-default',
              'model_calls': 0, 'coding_trials': 0, 'billed_model_cost_usd': 0,
              'network_observation': 'not packet-captured; no model invocations in this command; loopback provider guard and nonessential traffic disabled',
              'repetitions': []}
    for trial in range(1, args.repetitions+1):
        start = time.monotonic()
        if args.selection == 'upstream-serial-files':
            raw, counts, exit_code, timed_out = run_serial_files(target, private, env, args.timeout_seconds, trial)
        else:
            stdout, stderr, exit_code, timed_out = invoke(
                ['claude', 'plugin', 'test', str(target)], '', private, env, args.timeout_seconds)
            raw = stdout + '\n' + stderr
            counts = parse_output(raw)
        (private/f'trial-{trial}.log').write_text(raw, encoding='utf-8')
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
