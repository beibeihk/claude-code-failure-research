// Original X2 sequence contracts. Replies were captured from actual local Git.
import { describe, expect, test, tier } from 'claude-code/testing'
import Git from '../hooks/git'
import data from './followup-data'

tier('builtin')

describe('X2-backend-commit-checkout', () => {
  for (const scenario of data.scenarios) {
    test(scenario.kind+' five-state sequence', async () => {
      let state = scenario.states[0]
      let discoveryCount = 0
      let baselineCount = 0
      let calls: string[][] = []
      const violations: string[] = []
      const forbidden = async (operation: string) => {
        violations.push(operation)
        throw new Error('Unregistered host operation: '+operation)
      }
      const backend = await Git.gitBackendOf({
        run: async (argv, init) => {
          const captured = state.calls.find(call => JSON.stringify(call.argv) === JSON.stringify([...argv]))
          if (!captured || JSON.stringify(init) !== JSON.stringify(captured.init)) {
            violations.push('uncaptured argv/init')
            throw new Error('Git argv/init differs from registered capture')
          }
          calls.push([...argv])
          if (argv.includes('rev-parse')) discoveryCount++
          if (argv.includes('status')) baselineCount++
          return captured.answer
        },
        entryKindsOf: async path => {
          expect(path).toBe(state.repository.gitDir)
          return new Map(Object.entries(state.git_entries))
        },
        readFile: () => forbidden('readFile'),
        mtimeOf: () => forbidden('mtimeOf'),
        nowMs: () => forbidden('nowMs'),
        sessionStartMsOf: () => 0,
        onBranchBase: () => { violations.push('branch-base callback') },
      })
      expect(backend).not.toBeNull()
      expect(backend!.repository).toEqual(state.repository)
      for (let index = 0; index < scenario.states.length; index++) {
        state = scenario.states[index]
        calls = []
        const outcome = await backend!.fetchDiff('uncommitted')
        expect(outcome.kind).toBe('data')
        if (outcome.kind !== 'data') throw new Error('No data for registered stable state')
        expect(outcome.data.stats).toEqual(state.expected_stats)
        expect(outcome.data.files).toEqual(state.expected_files)
        expect(outcome.data.mode).toBe('uncommitted')
        expect(outcome.data.baseRef).toBe('HEAD')
        expect(outcome.data.source).toEqual({ kind: 'working-tree', base: 'HEAD' })
        expect(outcome.data.stalePaths).toEqual([])
        expect(outcome.data.isUnborn).toBe(false)
        expect(outcome.data.isUntrackedWithheld).toBe(false)
        const bodies = await backend!.fetchHunks(outcome.data, outcome.data.files)
        expect([...bodies]).toEqual(state.expected_hunks)
        expect(violations).toEqual([])
        expect(discoveryCount).toBe(1)
        expect(baselineCount).toBe(1)
        const expectedCalls = state.calls.filter(call => !call.argv.includes('rev-parse') &&
          (index === 0 || !call.argv.includes('status'))).map(call => call.argv)
        expect(calls).toEqual(expectedCalls)
        console.log('RESEARCH_OBSERVATION '+JSON.stringify({ scenario: scenario.kind,
          stage: state.label, files_count: outcome.data.stats.filesCount,
          lines_added: outcome.data.stats.linesAdded, lines_removed: outcome.data.stats.linesRemoved,
          hunks_count: bodies.size, exact_bytes_match: true, argv_init_match: true,
          backend_reused: true, baseline_reads: baselineCount }))
      }
    })
  }
})
