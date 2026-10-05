// Original N3 tests; unchanged source probe consumes real captured timestamps.
import { describe, expect, test, tier } from 'claude-code/testing'
import Git from '../hooks/git'
import data from './followup-data'

tier('builtin')

async function keyOf(state: typeof data.states[number]) {
  const normalize = (path: string) => path.replaceAll('\\', '/')
  return Git.headKeyOf({
    run: async argv => {
      expect([...argv]).toEqual(data.verify_head_argv)
      return state.head_answer
    },
    readFile: async path => {
      const key = normalize(path)
      expect(state.texts[key], 'only actual captured file bytes are read').toBeDefined()
      return state.texts[key]
    },
    entryKindsOf: async path => {
      const listing = state.listings[normalize(path)]
      expect(listing, 'every consulted directory was really listed').toBeDefined()
      return new Map(Object.entries(listing))
    },
    mtimeOf: async path => {
      const key = normalize(path)
      expect(state.stamps_ms[key], 'no synthetic timestamp is substituted').toBeDefined()
      return state.stamps_ms[key]
    },
  }, state.repository)
}

describe('N3-real-head-ref-oracle', () => {
  for (const pair of data.comparisons) {
    test(pair.before+' -> '+pair.after, async () => {
      const before = data.states.find(state => state.label === pair.before)!
      const after = data.states.find(state => state.label === pair.after)!
      expect(before.oid !== after.oid).toBe(pair.oid_changes)
      const a = await keyOf(before)
      const b = await keyOf(after)
      expect(a !== b).toBe(pair.key_changes)
      if (pair.before === 'linked-initial') {
        expect(before.repository.gitDir === before.repository.commonDir).toBe(false)
        expect(before.own_head_text).toBe(after.own_head_text)
      }
      console.log('RESEARCH_OBSERVATION '+JSON.stringify({ before: pair.before, after: pair.after,
        oid_changed: before.oid !== after.oid, key_changed: a !== b,
        own_head_text_changed: pair.own_head_text_changed }))
    })
  }
})
