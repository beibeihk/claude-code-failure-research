import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from analyzers.hooks import analyze

class HookTests(unittest.TestCase):
    def test_distinct_tools_not_duplicate(self):
        records=[{'event':'PreToolUse','tool_use_hash':str(i),'session_hash':'s','registration':'r','monotonic_ns':i} for i in (1,2)]
        self.assertEqual(analyze(records)['potential_duplicate_deliveries'],[])
    def test_two_registrations_not_duplicate(self):
        records=[{'event':'PreToolUse','tool_use_hash':'t','session_hash':'s','registration':r,'monotonic_ns':1} for r in ('a','b')]
        self.assertEqual(analyze(records)['potential_duplicate_deliveries'],[])
    def test_duplicate_same_registration_flagged(self):
        record={'event':'PreToolUse','tool_use_hash':'t','session_hash':'s','registration':'a','monotonic_ns':1}
        self.assertEqual(analyze([record,record])['potential_duplicate_deliveries'][0]['count'],2)
    def test_order_diagnostic(self):
        records=[{'event':'PreToolUse','tool_use_hash':'t','session_hash':'s','monotonic_ns':2},
                 {'event':'PostToolUse','tool_use_hash':'t','session_hash':'s','monotonic_ns':1}]
        self.assertEqual(analyze(records)['potential_order_mismatches'],['t'])
    def test_observer_never_logs_sensitive_input(self):
        with tempfile.TemporaryDirectory() as folder:
            script=Path(folder)/'record_hook.py'
            shutil.copy(Path(__file__).resolve().parents[1]/'fixtures/hooks-ledger/record_hook.py',script)
            payload={'hook_event_name':'PreToolUse','tool_name':'Read','session_id':'synthetic','tool_use_id':'t',
                     'tool_input':{'file_path':'fictional-private-path'},'secret':'fictional-sensitive-content'}
            p=subprocess.run([sys.executable,str(script)],input=json.dumps(payload),text=True,capture_output=True)
            self.assertEqual(p.returncode,0); self.assertEqual(p.stdout,'')
            text=next((Path(folder)/'.audit/hooks').glob('*.json')).read_text()
            self.assertNotIn('fictional',text); self.assertNotIn('tool_input',text)

if __name__=='__main__': unittest.main()
