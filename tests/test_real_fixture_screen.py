"""Check the actual fixture oracle and scope before native-engine replay."""
import tempfile
import unittest
from pathlib import Path

from runners.run_free_screen import build_data, STATUS


class RealFixtureScreenTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.data = build_data(Path(cls.temp.name)/'screen')

    @classmethod
    def tearDownClass(cls):
        # tempfile owns precisely this generated test folder, never user files.
        target = Path(cls.temp.name).resolve()
        if target.parent == target or not (target/'screen').is_dir():
            raise ValueError('Refuse cleanup outside the generated fixture target')
        cls.temp.cleanup()

    def test_real_conflict_markers_and_own_worktree_git_directory(self):
        states = {s['label']: s for s in self.data['states']}
        self.assertEqual(len(states), 8)
        linked = states['linked-merge-conflict']
        self.assertNotEqual(linked['repository']['gitDir'], linked['repository']['commonDir'])
        self.assertIn('MERGE_HEAD', linked['marker_names'])
        self.assertIn('REBASE_HEAD', states['linked-rebase-conflict']['marker_names'])
        for label in ('ordinary-clean', 'ordinary-merge-aborted', 'linked-clean',
                      'linked-merge-aborted', 'linked-rebase-aborted'):
            self.assertEqual(states[label]['marker_names'], [])

    def test_actual_nul_status_and_rename_records(self):
        paths = self.data['paths']
        self.assertEqual(paths['clean']['stdout'], '')
        self.assertTrue(paths['dirty']['stdout'].endswith('\0'))
        actual = sorted(record[3:] for record in paths['dirty']['stdout'].split('\0') if record)
        self.assertEqual(actual, sorted(paths['names']+['binary.dat']))
        self.assertIn('\0old name.ts\0new name.ts\0', paths['rename']['stdout'])
        self.assertIn('--no-renames', STATUS)

    def test_nested_frames_have_exact_real_file_bytes_and_boundary_control(self):
        for fixture in self.data['instructions'].values():
            self.assertTrue(Path(fixture['sibling_path']).is_file())
            for file in fixture['initial']+fixture['nested']+fixture['claude']:
                self.assertEqual(Path(file['parts'][0]['path']).read_text(encoding='utf-8'), file['content'])
            for path, content in fixture['read_contents'].items():
                self.assertEqual(Path(path).read_text(encoding='utf-8'), content)
        self.assertEqual(len(self.data['instructions']['plain']['expected_frames']), 2)
        self.assertEqual(len(self.data['instructions']['claimed']['expected_frames']), 1)


if __name__ == '__main__': unittest.main()
