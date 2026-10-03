"""Fetch public reports privately and write our screening decisions, not failure claims."""
import concurrent.futures
import datetime as dt
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
ITEMS = [
 (10871,'F07','software','Plugin hooks delivered twice','Known duplicate; historical closed report. Re-test current clean baseline before interpreting.'),
 (9602,'F07','software','Hook UI repeats messages','Distinguish duplicate display from duplicate process invocation; known closed report.'),
 (97155,'F03','model-behavior','Completion without running failing tests','Priority for V01; existing exact-topic report, no new issue without distinct evidence.'),
 (95495,'F03','model-behavior','Unverified assertions stated as facts','Existing broad behavior report; requires repeated objective verification.'),
 (94650,'F03','model-behavior','Overclaimed fix adequacy','Needs scope-specific verifier; title alone cannot prove falsity.'),
 (95494,'F01','model-behavior','Scope override and unsupported test claims','Existing report; no public transcript replication; V01 checks objective constraints.'),
 (97261,'F08','documentation-or-software','Doctor skips AGENTS checks','Current doctor prompt-audit added in 2.1.283; distinguish older diagnostics from current command.'),
 (98796,'F08','software','Nested AGENTS with at-mention','Native AGENTS loading differs from CLAUDE; check documented loading triggers before calling bug.'),
 (96117,'F08','documented-behavior','CLAUDE.local disables AGENTS fallback','Current memory docs explicitly document this condition; default fallback is not itself a new bug.'),
 (96544,'F08','software','AGENTS loading indicator absent','Indicator absence is not proof instructions absent. Use source/behavior triangulation.'),
 (90913,'F09','model-behavior','Compaction summary invents a prior claim','Needs paired summaries; current resume fixes do not establish this behavior fixed.'),
 (95760,'F09','software-or-environment','Watcher state after compaction or restart','Need process lifecycle evidence; do not infer running state from narrative.'),
 (89248,'F09','software','Scheduled notifications after compaction','Current feature availability and timing are confounds; no scheduler test in V01.'),
 (98744,'F12','software','PostToolUse absent for MCP','Known recent report; separate MCP from builtin tool control and inspect actual hook delivery.'),
 (97977,'F15','software','Desktop hook delivery absent','Surface comparison needed; native CLI results cannot demonstrate Desktop failure.'),
 (97820,'F10','software-or-configuration','Synchronous hooks delay subagents','Synchronous hooks can block by design; use fast hook, async ablation and elapsed time.'),
 (77851,'F12','feature-or-software','PostToolUse observes rewritten input','Check documented updatedInput semantics; loss of original input may be feature request.'),
 (98395,'F06','software','Auto classifier empty verdict','Known report; compare dontAsk versus auto with same allowed command. Never test boundary bypass publicly.'),
 (97766,'F06','environment-or-software','Classifier unavailable blocks tool','Separate service outage, network and client behavior; no finding without official endpoint.'),
 (98770,'F06','software-or-configuration','Whitelist on retry mismatches','Validate deny > ask > allow before blaming implementation; scope only unexpected refusal.'),
 (91414,'F14','software','MCP first turn waits for subscriptions','Use local synthetic MCP server and measured protocol timestamps; exact-topic duplicate exists.'),
 (16837,'F14','software-or-configuration','MCP timeout capped unexpectedly','Older report; verify current timeout setting and units.'),
 (83495,'F14','software','Concurrent MCP startup lacks jitter','Distinguish server overload from recovery; fake server can test transport locally.'),
 (91043,'F10','software','Subagent structured failures dropped','Requires result/error records; existing issue, no claim based on parent prose alone.'),
 (83412,'F10','software','Subagent budget limit lacks handoff','Budget and model failures need separate outcome classes; never score interrupted child as success.'),
 (75318,'F13','software-or-environment','Subagent stream failure recovery','2.1.288 changelog changes partial-response recovery; current-version retest required.'),
 (62069,'F12','software','Remote control leaves idle children','Availability-dependent lifecycle task; do not connect user devices for an unneeded probe.'),
 (71158,'F14','configuration-or-software','Plugin MCP cold-start auth failure','Plugin auth and official CLI core are different components; no credentials in public fixtures.')
]

def fetch(item):
    number, taxonomy, route, topic, decision = item
    p = subprocess.run(['gh','api', f'repos/anthropics/claude-code/issues/{number}'],
                       capture_output=True, text=True, encoding='utf-8')
    if p.returncode: raise RuntimeError('Candidate read failed; details withheld')
    data = json.loads(p.stdout)
    (ROOT/'.private/candidates'/f'{number}.json').write_text(json.dumps(data), encoding='utf-8')
    body = data.get('body') or ''
    impact = 4 if taxonomy in ('F01','F03','F06','F09','F10') else 3
    scores = {'real_user_impact': impact, 'agent_relevance': 4,
              'reproducibility': 0, 'novelty': 0, 'evidence_quality': 0,
              'minimal_repro': 0, 'research_value': 4, 'anthropic_relevance': 4}
    return {'id': f'C{ITEMS.index(item)+1:02d}', 'source_issue': number,
            'source_url': data['html_url'], 'source_state': data['state'],
            'source_updated_at': data['updated_at'], 'source_body_sha256': hashlib.sha256(body.encode()).hexdigest(),
            'topic': topic, 'taxonomy': taxonomy, 'classification_hypothesis': route,
            'status': 'screened-existing-report', 'evidence_level': None,
            'own_coding_trials': 0, 'duplicate_risk': 'known existing report',
            'decision': decision, 'scores': scores,
            'score_interpretation': 'Prioritization judgments only. Zero evidence/repro scores mean not tested, not disproven.'}

def main():
    (ROOT/'.private/candidates').mkdir(parents=True, exist_ok=True)
    (ROOT/'reports').mkdir(exist_ok=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        cards = list(pool.map(fetch, ITEMS))
    result = {'screened_at': dt.datetime.now(dt.timezone.utc).isoformat(),
              'candidate_count': len(cards), 'confirmed_by_this_project': 0,
              'scope': 'Public report screening; not experimental validation', 'candidates': cards}
    (ROOT/'reports/candidate-screening.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    lines = ['# Candidate screening', '', 'These are existing public reports, not failures established by this project.',
             'No behavioral coding trial has been run. All candidates have known duplicate risk.', '',
             '| ID | Topic | Taxonomy | Source | Screening decision |', '|---|---|---|---|---|']
    for c in cards:
        lines.append(f"| {c['id']} | {c['topic']} | {c['taxonomy']} | [#{c['source_issue']}]({c['source_url']}) | {c['decision']} |")
    lines += ['', 'The JSON companion contains all eight 0–5 priority scores. They are provisional judgments;',
              'novelty and experimental evidence scores remain zero. Source bodies are private; public hashes permit snapshot auditing.', '']
    (ROOT/'reports/candidate-screening.md').write_text('\n'.join(lines), encoding='utf-8')
    print(json.dumps({'screened': len(cards), 'confirmed': 0}))

if __name__ == '__main__': main()
