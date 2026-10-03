"""No decisions and no raw input logging: one metadata file per invocation."""
import hashlib
import json
from pathlib import Path
import sys
import time
import uuid

if __name__ == '__main__':
    event = json.load(sys.stdin)
    identifier = lambda value: hashlib.sha256(str(value).encode()).hexdigest() if value else None
    record = {'event': event.get('hook_event_name'), 'tool': event.get('tool_name'),
              'session_hash': identifier(event.get('session_id')),
              'tool_use_hash': identifier(event.get('tool_use_id')),
              'monotonic_ns': time.monotonic_ns(), 'registration': 'local-observer',
              'invocation_id': str(uuid.uuid4())}
    folder = Path(__file__).resolve().parent/'.audit/hooks'
    folder.mkdir(parents=True, exist_ok=True)
    (folder/(record['invocation_id']+'.json')).write_text(json.dumps(record)+'\n', encoding='utf-8')
    # Exit 0 and no stdout: passive observation only, no allow/deny/block decision.
