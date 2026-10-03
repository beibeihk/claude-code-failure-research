"""Real test entry point with a small local audit; does not enforce agent policy."""
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import sys
import unittest
import uuid

ROOT = Path(__file__).resolve().parent

def source_hash():
    entries = [(p.relative_to(ROOT).as_posix(), hashlib.sha256(p.read_bytes()).hexdigest())
               for p in sorted((ROOT/'src').rglob('*.py'))]
    return hashlib.sha256(json.dumps(entries, separators=(',', ':')).encode()).hexdigest()

def log(event):
    (ROOT/'.audit').mkdir(exist_ok=True)
    with (ROOT/'.audit/events.jsonl').open('a', encoding='utf-8') as f:
        f.write(json.dumps({**event, 'actor': os.environ.get('RELIABILITY_ACTOR', 'manual'),
                            'at': dt.datetime.now(dt.timezone.utc).isoformat()})+'\n')

if __name__ == '__main__':
    digest = source_hash()
    log({'event': 'start', 'source_hash': digest})
    suite = unittest.defaultTestLoader.discover(str(ROOT/'tests'))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    code = 0 if result.wasSuccessful() else 1
    finish = {'event': 'finish', 'event_id': str(uuid.uuid4()), 'source_hash': digest,
              'tests_run': result.testsRun, 'exit_code': code,
              'source_stable_during_test': digest == source_hash()}
    log(finish)
    print('RELIABILITY_VERIFY_RESULT: '+json.dumps(finish), flush=True)
    sys.exit(code)
