"""Read-only upstream snapshot collection; never publish full upstream documents."""
import concurrent.futures
import base64
import datetime as dt
import hashlib
import json
import shutil
from pathlib import Path
import subprocess
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
TOPICS = ['overview', 'cli-reference', 'headless', 'hooks', 'hooks-guide',
          'permissions', 'settings', 'memory', 'sub-agents', 'plugins',
          'mcp', 'remote-control', 'github-actions', 'permission-modes', 'auto-mode-config', 'sandboxing',
          'how-claude-code-works', 'common-workflows', 'model-config', 'context-window']
QUERIES = ['hook duplicate', 'tests pass', 'AGENTS.md', 'compaction resume',
           'PostToolUse', 'permission auto', 'diff stale', 'MCP timeout',
           'subagent failure', 'instructions ignored', 'tool retry', 'remote reconnect']

def gh(*args):
    p = subprocess.run(['gh', *args], capture_output=True, text=True, encoding='utf-8')
    if p.returncode:
        raise RuntimeError('GitHub read failed (details withheld)')
    return json.loads(p.stdout)

def fetch(topic):
    url = f'https://code.claude.com/docs/en/{topic}.md'
    # curl uses the configured Windows proxy; urllib can hit a blocked direct route.
    curl = shutil.which('curl.exe') or shutil.which('curl')
    if not curl: return {'topic':topic, 'url':url, 'status':'unavailable', 'reason':'curl_not_installed'}
    p = subprocess.run([curl, '-fLsS', '--max-time', '45', url], capture_output=True)
    if p.returncode:
        return {'topic': topic, 'url': url, 'status': 'unavailable', 'exit_code': p.returncode}
    data = p.stdout
    (ROOT / '.private' / 'sources' / (topic + '.md')).write_bytes(data)
    return {'topic': topic, 'url': url, 'status': 'retrieved', 'bytes': len(data),
            'sha256': hashlib.sha256(data).hexdigest()}

def main():
    (ROOT / '.private' / 'sources').mkdir(parents=True, exist_ok=True)
    (ROOT / 'results' / 'source-audit').mkdir(parents=True, exist_ok=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        docs = list(pool.map(fetch, TOPICS))
    upstream = gh('api', 'repos/anthropics/claude-code/commits/main')
    release = gh('api', 'repos/anthropics/claude-code/releases/latest')
    files = []
    paths = ['README.md', 'SECURITY.md', 'CHANGELOG.md'] + [
        '.github/ISSUE_TEMPLATE/'+name for name in ['bug_report.yml', 'model_behavior.yml',
        'github_connection.yml', 'feature_request.yml', 'documentation.yml', 'config.yml']]
    for path in paths:
        item = gh('api', f"repos/anthropics/claude-code/contents/{path}?ref={upstream['sha']}")
        data = base64.b64decode(item['content'])
        (ROOT/'.private/sources'/Path(path).name).write_bytes(data)
        files.append({'path': path, 'url': f"https://github.com/anthropics/claude-code/blob/{upstream['sha']}/{path}",
                      'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)})
    snapshot = {'retrieved_at': dt.datetime.now(dt.timezone.utc).isoformat(),
                'upstream_sha': upstream['sha'], 'release': release['tag_name'],
                'release_published_at': release['published_at'], 'docs': docs, 'repository_files': files}
    (ROOT / 'results/source-audit/snapshot.json').write_text(json.dumps(snapshot, indent=2)+'\n', encoding='utf-8')
    searches = []
    for query in QUERIES:
        hits = gh('search', 'issues', '--repo', 'anthropics/claude-code', query,
                  '--limit', '8', '--json', 'number,title,state,url,updatedAt')
        searches.append({'query': query, 'hits': hits})
    (ROOT / 'results/source-audit/issue-search.json').write_text(json.dumps(searches, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'docs_retrieved': sum(d['status']=='retrieved' for d in docs),
                      'docs_attempted': len(docs), 'issue_searches': len(searches),
                      'release': release['tag_name']}))

if __name__ == '__main__':
    main()
