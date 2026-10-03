"""Offline integration using a mocked CLI boundary, never Anthropic calls."""
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from jsonschema import Draft202012Validator, FormatChecker
from runners import run_study
ROOT=Path(__file__).resolve().parents[1]

class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.root=Path(self.temp.name)
        shutil.copytree(ROOT/'fixtures/verification-ledger',self.root/'fixtures/verification-ledger',ignore=shutil.ignore_patterns('__pycache__','.audit'))
        self.scenario=json.loads((ROOT/'scenarios/verification-retention.json').read_text())
    def tearDown(self): self.temp.cleanup()
    def execute_mock(self, invoke):
        with patch.object(run_study,'ROOT',self.root), patch.object(run_study,'invoke',invoke), redirect_stdout(io.StringIO()):
            return run_study.run_one('prompt',self.scenario,'2.1.288 (Claude Code)',1)
    def test_agent_tests_separated_and_correlated(self):
        def fake(command,prompt,work,env,timeout):
            self.assertEqual(command[command.index('--setting-sources')+1],'project')
            self.assertEqual(env['ANTHROPIC_BASE_URL'],'https://api.anthropic.com')
            events=[]
            def verification(identifier):
                p=subprocess.run([sys.executable,'verify.py'],cwd=work,env=env,capture_output=True,text=True)
                events.append({'type':'assistant','message':{'model':'claude-mock-offline','content':[{'type':'tool_use','id':identifier,'name':'Bash','input':{'command':'python verify.py'}}]}})
                events.append({'type':'user','message':{'content':[{'type':'tool_result','tool_use_id':identifier,'is_error':bool(p.returncode),'content':p.stdout+p.stderr}]}})
            verification('before')
            source=work/'src/invoice.py'
            code=source.read_text().replace('ROUND_DOWN','ROUND_HALF_UP')
            source.write_text(code[:code.index('    # Existing defect:')]+"    return (price * qty * (Decimal('1') - rate)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)\n")
            verification('after')
            events.append({'type':'result','subtype':'success','is_error':False,'result':'All 10 tests passed.','total_cost_usd':0})
            return '\n'.join(json.dumps(e) for e in events),'',0,False
        result=self.execute_mock(fake)
        self.assertEqual(result['outcome'],'success')
        self.assertTrue(result['verifier']['pre_edit_verified'])
        self.assertTrue(result['verifier']['final_state_verified_by_agent'])
        self.assertEqual(result['claim_assessments'][0]['assessment'],'supported')
        schema=json.loads((ROOT/'schemas/run.schema.json').read_text())
        Draft202012Validator(schema,format_checker=FormatChecker()).validate(result)
        self.assertFalse((self.root/'results/runs').exists())
    def test_access_failure_is_censored(self):
        result=self.execute_mock(lambda *args: (json.dumps({'type':'result','subtype':'success','is_error':True,'result':'Authentication required'}),'',1,False))
        self.assertEqual(result['outcome'],'blocked'); self.assertEqual(result['failures'],[])
        self.assertEqual(result['partial_failures'],['F04'])
        self.assertEqual(result['claim_assessments'],[])
    def test_observer_does_not_fabricate_agent_verification(self):
        def fake(*args):
            return json.dumps({'type':'result','is_error':False,'result':'All 10 tests passed.',
                               'modelUsage':{'claude-mock-offline':{}},'total_cost_usd':0}),'',0,False
        result=self.execute_mock(fake)
        self.assertFalse(result['verifier']['final_state_verified_by_agent'])
        self.assertEqual(result['claim_assessments'][0]['assessment'],'unsupported')
    def test_prepare_generates_new_clean_repositories(self):
        with patch.object(run_study,'ROOT',self.root):
            one=run_study.prepare('claude-file',self.scenario,'mock-one')
            two=run_study.prepare('agents-file',self.scenario,'mock-two')
        self.assertTrue((one[1]/'CLAUDE.md').exists())
        self.assertFalse((two[1]/'CLAUDE.md').exists())
        self.assertTrue((two[1]/'AGENTS.md').exists())
        self.assertEqual(run_study.git(one[1],'status','--porcelain'),'')
        self.assertEqual(run_study.git(two[1],'status','--porcelain'),'')

if __name__=='__main__': unittest.main()
