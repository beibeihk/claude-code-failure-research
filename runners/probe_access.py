"""Minimal official-endpoint probe. Secrets remain inherited in memory, never logged."""
import json
import os
from pathlib import Path
import subprocess
import datetime as dt
import re
from runners.policy import require_model_access

ROOT = Path(__file__).resolve().parents[1]

def official_env():
    env = os.environ.copy()
    for key in list(env):
        if key.startswith('ANTHROPIC_') or (key.startswith('CLAUDE_CODE_') and key not in ('CLAUDE_CODE_GIT_BASH_PATH', 'CLAUDE_CODE_OAUTH_TOKEN')):
            env.pop(key)
    env.pop('CLAUDECODE', None)
    # Do not change the real account's auth files or CODEX_HOME.
    # Preserve a genuine API key only when the inherited endpoint is official.
    if os.environ.get('ANTHROPIC_API_KEY') and os.environ.get('ANTHROPIC_BASE_URL', 'https://api.anthropic.com').rstrip('/') == 'https://api.anthropic.com':
        env['ANTHROPIC_API_KEY'] = os.environ['ANTHROPIC_API_KEY']
    env['ANTHROPIC_BASE_URL'] = 'https://api.anthropic.com'
    return env

def main():
    require_model_access()
    private = ROOT / '.private'
    private.mkdir(exist_ok=True)
    command = ['claude', '-p', 'Return exactly READY without using tools.',
               '--safe-mode', '--setting-sources', '', '--tools', '',
               '--strict-mcp-config', '--mcp-config', '{"mcpServers":{}}',
               '--no-session-persistence', '--output-format', 'stream-json',
               '--verbose', '--model', 'haiku', '--max-budget-usd', '0.05']
    version = subprocess.check_output(['claude', '--version'], text=True).strip()
    started = dt.datetime.now(dt.timezone.utc).isoformat()
    try:
        p = subprocess.run(command, cwd=private, env=official_env(), capture_output=True,
                           text=True, encoding='utf-8', timeout=90)
        (private / 'official-probe.stdout.jsonl').write_text(p.stdout, encoding='utf-8')
        (private / 'official-probe.stderr.txt').write_text(p.stderr, encoding='utf-8')
        events = []
        for line in p.stdout.splitlines():
            try: events.append(json.loads(line))
            except json.JSONDecodeError: pass
        result = next((e for e in reversed(events) if e.get('type')=='result'), {})
        text = result.get('result', '')
        status = 'ready' if p.returncode == 0 and text.strip() == 'READY' else 'blocked'
        reason = ('authentication_required' if re.search(r'not logged in|authentication required|please (?:run /login|log in|login)', text, re.I) else 'api_or_environment_error')
        summary = {'version': version, 'date': started, 'endpoint': 'official',
                   'status': status, 'reason': None if status=='ready' else reason,
                   'process_exit_code': p.returncode, 'result_subtype': result.get('subtype'),
                   'model_usage_keys': list(result.get('modelUsage', {})),
                   'cost_usd': result.get('total_cost_usd'), 'is_coding_run': False}
    except subprocess.TimeoutExpired:
        summary = {'version': version, 'date': started, 'endpoint': 'official',
                   'status': 'blocked', 'reason': 'timeout', 'is_coding_run': False}
    (ROOT/'results').mkdir(exist_ok=True)
    (ROOT/'results/access-probe.json').write_text(json.dumps(summary, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(summary))

if __name__ == '__main__': main()
