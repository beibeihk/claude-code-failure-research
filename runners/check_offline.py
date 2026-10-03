"""Record real offline validation, explicitly excluding model experiments."""
import datetime as dt
import json
from pathlib import Path
import re
import subprocess
import sys

from runners.validate_repository import validate
ROOT=Path(__file__).resolve().parents[1]

def main():
    p=subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-v'],
                     cwd=ROOT,capture_output=True,text=True,encoding='utf-8')
    text=p.stdout+p.stderr
    (ROOT/'.private').mkdir(exist_ok=True)
    (ROOT/'.private/offline-validation.log').write_text(text,encoding='utf-8')
    match=re.search(r'Ran (\d+) tests in ([0-9.]+)s',text)
    if p.returncode or not match:
        print('Offline tests failed; inspect ignored .private/offline-validation.log')
        raise SystemExit(1)
    repository=validate()
    plan=subprocess.run([sys.executable,'-m','runners.run_study','--repetitions','1'],
                        cwd=ROOT,capture_output=True,text=True,encoding='utf-8')
    if plan.returncode or json.loads(plan.stdout).get('execute') is not False:
        raise RuntimeError('Dry-run validation failed')
    result={'validated_at':dt.datetime.now(dt.timezone.utc).isoformat(),
            'kind':'offline-harness-validation', 'python_version':sys.version.split()[0],
            'tests_passed':int(match.group(1)), 'tests_failed':0,
            'duration_seconds':float(match.group(2)), 'repository_checks':repository,
            'runner_dry_run':'pass', 'real_claude_model_calls':0,
            'notes':'Includes mocked CLI integration and actual fixture oracle tests; not agent performance evidence'}
    (ROOT/'results/offline-validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result))

if __name__=='__main__': main()
