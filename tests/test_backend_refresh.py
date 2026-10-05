"""Real-Git patch capture agrees with the independently named byte oracle."""
from pathlib import Path
import tempfile
import unittest

from runners.run_backend_refresh import build_backend_data


class BackendRefreshFixtureTests(unittest.TestCase):
    def test_captured_patches_follow_real_commit_and_checkout_bases(self):
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name)/'backend-fixtures'
        try:
            data = build_backend_data(root)
            for scenario in data['scenarios']:
                states = scenario['states']
                self.assertEqual([s['expected_stats']['filesCount'] for s in states], [2, 0, 1, 0, 1])
                self.assertEqual(states[0]['oid'], states[3]['oid'])
                self.assertNotEqual(states[0]['oid'], states[1]['oid'])
                self.assertEqual(states[1]['oid'], states[2]['oid'])
                self.assertEqual(states[3]['oid'], states[4]['oid'])
                self.assertEqual(states[0]['repository']['gitDir'] != states[0]['repository']['commonDir'], scenario['kind']=='linked')
                for state in states:
                    patches = [c['answer']['stdout'] for c in state['calls'] if '--raw' in c['argv']]
                    if not state['expected_hunks']:
                        self.assertEqual(patches, [])
                        continue
                    self.assertEqual(len(patches), 1)
                    for _, body in state['expected_hunks']:
                        for row in body['hunks'][0]['lines'][:2]:
                            self.assertIn('\n'+row+'\n', patches[0])
                after_commit = states[2]['expected_hunks'][0][1]['hunks'][0]['lines']
                self.assertEqual(after_commit[:2], ['-committed=plain.txt', '+after-commit=plain.txt'])
                after_checkout = states[4]['expected_hunks'][0][1]['hunks'][0]['lines']
                self.assertEqual(after_checkout[:2], ['-base=税收.txt', '+after-checkout=税收.txt'])
        finally:
            if root.resolve().parent != Path(temporary.name).resolve():
                raise ValueError('Refuse cleanup outside generated temporary fixtures')
            temporary.cleanup()


if __name__ == '__main__': unittest.main()
