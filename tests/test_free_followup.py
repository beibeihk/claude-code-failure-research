"""Actual Git operations/timestamps and isolated manifest injection oracle."""
import json
from pathlib import Path
import tempfile
import unittest

from runners.run_free_followup import build_head_data, build_option_data, prepare


class FreeFollowupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temp.name)/'generated-fixtures'
        cls.head = build_head_data(cls.root/'heads')
        cls.options = build_option_data(cls.root/'options')

    @classmethod
    def tearDownClass(cls):
        if cls.root.resolve().parent != Path(cls.temp.name).resolve() or not cls.root.is_dir():
            raise ValueError('Refuse cleanup outside the generated temporary target')
        cls.temp.cleanup()

    def test_git_operations_and_unmodified_timestamp_capture(self):
        self.assertEqual(len(self.head['comparisons']), 7)
        states = {s['label']: s for s in self.head['states']}
        self.assertEqual(states['ordinary-initial']['stamps_ns'], states['ordinary-noop']['stamps_ns'])
        for state in states.values():
            for path, nanoseconds in state['stamps_ns'].items():
                self.assertEqual(state['stamps_ms'][path], nanoseconds/1_000_000)
        linked = states['linked-initial']
        self.assertNotEqual(linked['repository']['gitDir'], linked['repository']['commonDir'])
        self.assertEqual(linked['own_head_text'], states['linked-committed']['own_head_text'])
        for pair in self.head['comparisons']:
            self.assertEqual(states[pair['before']]['oid'] != states[pair['after']]['oid'], pair['oid_changes'])

    def test_option_fixture_bytes_and_kinds_are_actual_files(self):
        self.assertEqual({file['kind'] for file in self.options['handed']}, {'managed','user','project','local','memory'})
        for file in self.options['handed']:
            self.assertEqual(Path(file['path']).read_text(encoding='utf-8'), file['content'])
        self.assertEqual(len(self.options['all_nested_frames']), 2)

    def test_manifest_injection_changes_one_field_and_preserves_hooks(self):
        source = self.root/'fake-source'
        (source/'tests').mkdir(parents=True)
        (source/'.claude-plugin').mkdir()
        (source/'hooks').mkdir()
        (source/'hooks/register.ts').write_text('unchanged marker', encoding='utf-8')
        manifest = {'name':'agents-md','userConfig':{'instructionFiles':{'default':'claude-md-or-agents-md','options':['claude-md','managed-only']}}}
        (source/'.claude-plugin/plugin.json').write_text(json.dumps(manifest), encoding='utf-8')
        target = self.root/'fake-target'
        prepare(source, target, 'options.test.ts', self.options, 'managed-only')
        revised = json.loads((target/'.claude-plugin/plugin.json').read_text(encoding='utf-8'))
        self.assertEqual(revised['userConfig']['instructionFiles']['default'], 'managed-only')
        revised['userConfig']['instructionFiles']['default'] = manifest['userConfig']['instructionFiles']['default']
        self.assertEqual(revised, manifest)
        self.assertEqual((target/'hooks/register.ts').read_bytes(), (source/'hooks/register.ts').read_bytes())


if __name__ == '__main__': unittest.main()
