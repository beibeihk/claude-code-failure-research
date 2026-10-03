"""Extraction must keep assertions and imports while isolating deadline changes."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from runners.run_client_tests import FOCUSED_TESTS, parse_output, prepare_focused_control, run_serial_files, tree_hash


class ClientControlTests(unittest.TestCase):
    def make_source(self, root):
        source = root/'source'
        (source/'hooks').mkdir(parents=True)
        (source/'hooks/register.ts').write_text('original-implementation\n')
        for relative, name in FOCUSED_TESTS:
            path = source/relative
            path.parent.mkdir(parents=True, exist_ok=True)
            assertion = "expect(await $.command.run(Fixtures.DIFF)).toEqual({ text: 'Diff panel shown' })"
            path.write_text("import { describe, expect, test, tier } from 'claude-code/testing'\ntier('builtin')\ndescribe('synthetic', () => {\n  test('"+name+"', async ($, on) => {\n    await $.session.start(Fixtures.SESSION)\n    "+assertion+"\n  })\n\n  test('unrelated case', async () => { throw new Error('unrelated') })\n})\n")
        (source/'tests/unrelated.test.ts').write_text('unrelated suite')
        return source

    def test_default_extraction_preserves_deadline_assertions_and_hooks(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = self.make_source(root)
            destination = prepare_focused_control(source, 'diff', root/'overlay')
            self.assertEqual(tree_hash(source/'hooks'), tree_hash(destination/'hooks'))
            self.assertEqual(len(list(destination.rglob('*.test.ts'))), 2)
            for relative, name in FOCUSED_TESTS:
                text = (destination/relative).read_text()
                self.assertIn("expect(await $.command.run(Fixtures.DIFF)).toEqual", text)
                self.assertIn("test('"+name+"', async", text)
                self.assertNotIn('timeoutMs', text)
                self.assertNotIn('unrelated case', text)
            self.assertIn('unrelated case', (source/FOCUSED_TESTS[0][0]).read_text())

    def test_expanded_deadline_changes_test_option_only(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = self.make_source(root)
            one = prepare_focused_control(source, 'diff', root/'default')
            two = prepare_focused_control(source, 'diff', root/'expanded', 15000)
            for relative, _ in FOCUSED_TESTS:
                expanded = (two/relative).read_text()
                self.assertIn('{ timeoutMs: 15000 }', expanded)
                self.assertEqual(expanded.replace('{ timeoutMs: 15000 }, ', ''), (one/relative).read_text())

    def test_ambiguous_or_changed_upstream_case_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = self.make_source(root)
            (source/FOCUSED_TESTS[0][0]).write_text('unregistered source revision')
            with self.assertRaisesRegex(ValueError, 'Pinned focused test changed'):
                prepare_focused_control(source, 'diff', root/'overlay')

    def test_timeout_kind_is_separate_from_failed_assertion(self):
        result = parse_output('(fail) suite > slow [6000.1ms]\n  Error: timed out after 5000 ms\n(fail) suite > wrong [5ms]\n  AssertionError: expected value\n(pass) suite > normal [1ms]\nRan 3 tests across 1 file.\n')
        self.assertEqual([r['error_kind'] for r in result['test_cases']], ['test-timeout', 'assertion', None])
        self.assertEqual(result['test_cases'][0]['elapsed_ms'], 6000.1)
        self.assertEqual(result['failed_tests'], ['suite > slow', 'suite > wrong'])
        self.assertTrue(result['complete'])

    def test_singular_test_footer_is_complete(self):
        result = parse_output('(pass) synthetic > one [100ms]\nRan 1 test across 1 file.\n')
        self.assertEqual(result['tests_run'], 1)
        self.assertTrue(result['complete'])

    def test_serial_dispatch_activates_one_file_and_restores_exact_bytes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = self.make_source(root)
            original = tree_hash(source)
            seen = []
            def fake(*args):
                active = list(source.rglob('*.test.ts'))
                self.assertEqual(len(active), 1)
                seen.append(active[0].relative_to(source).as_posix())
                return '(pass) synthetic > case [1ms]\nRan 1 tests across 1 file.\n', '', 0, False
            with patch('runners.run_client_tests.invoke', fake):
                raw, counts, exit_code, timed_out = run_serial_files(source, root, {}, 30, 1)
            self.assertEqual(len(seen), 3)
            self.assertTrue(counts['complete'])
            self.assertEqual(counts['passed'], 3)
            self.assertEqual(exit_code, 0)
            self.assertFalse(timed_out)
            self.assertEqual(tree_hash(source), original)

    def test_serial_dispatch_exception_still_restores_private_overlay(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = self.make_source(root)
            original = tree_hash(source)
            with patch('runners.run_client_tests.invoke', side_effect=RuntimeError('synthetic interruption')):
                with self.assertRaisesRegex(RuntimeError, 'synthetic interruption'):
                    run_serial_files(source, root, {}, 30, 1)
            self.assertEqual(tree_hash(source), original)


if __name__ == '__main__':
    unittest.main()
