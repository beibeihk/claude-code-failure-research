"""Verify that no-spend policy fails closed and test-engine results stay scoped."""
from pathlib import Path
import unittest
from unittest.mock import patch

from runners import policy, probe_access, run_study
from runners.run_client_tests import client_test_env, parse_output


class NoCostTests(unittest.TestCase):
    def test_policy_blocks_model_access(self):
        with self.assertRaisesRegex(RuntimeError, 'Model calls are disabled'):
            policy.require_model_access()

    def test_missing_policy_does_not_enable_model_access(self):
        with patch.object(policy, 'POLICY', Path('/nonexistent-research-policy.json')):
            with self.assertRaises(FileNotFoundError):
                policy.require_model_access()

    def test_probe_blocked_before_subprocess_or_writes(self):
        with patch.object(probe_access.subprocess, 'run') as launched:
            with self.assertRaisesRegex(RuntimeError, 'Model calls are disabled'):
                probe_access.main()
            launched.assert_not_called()

    def test_direct_study_run_is_also_blocked(self):
        with patch.object(run_study, 'prepare') as prepared:
            with self.assertRaisesRegex(RuntimeError, 'Model calls are disabled'):
                run_study.run_one('prompt', {}, 'unused', 1)
            prepared.assert_not_called()

    def test_client_environment_discards_provider_credentials(self):
        env = client_test_env({'ANTHROPIC_API_KEY': 'synthetic-secret',
                               'ANTHROPIC_BASE_URL': 'https://example.invalid',
                               'CLAUDE_CODE_OAUTH_TOKEN': 'synthetic-secret',
                               'CLAUDE_CODE_GIT_BASH_PATH': 'fixture-bash',
                               'PATH': 'fixture-path'})
        self.assertNotIn('ANTHROPIC_API_KEY', env)
        self.assertNotIn('CLAUDE_CODE_OAUTH_TOKEN', env)
        self.assertEqual(env['ANTHROPIC_BASE_URL'], 'http://127.0.0.1:1')
        self.assertEqual(env['CLAUDE_CODE_GIT_BASH_PATH'], 'fixture-bash')
        self.assertEqual(env['DISABLE_TELEMETRY'], '1')

    def test_complete_failed_suite_is_not_a_transport_failure(self):
        counts = parse_output('(pass) suite > control [12.1ms]\n(fail) suite > candidate [5.0ms]\nRan 2 tests across 1 file.\n')
        self.assertTrue(counts['complete'])
        self.assertEqual(counts['passed'], 1)
        self.assertEqual(counts['failed_tests'], ['suite > candidate'])

    def test_truncated_output_is_not_a_complete_zero_failure_suite(self):
        counts = parse_output('(pass) suite > control\n')
        self.assertFalse(counts['complete'])
        self.assertIsNone(counts['tests_run'])

    def test_empty_suite_is_not_evidence_of_a_pass(self):
        self.assertFalse(parse_output('Ran 0 tests across 0 files.')['complete'])


if __name__ == '__main__':
    unittest.main()
