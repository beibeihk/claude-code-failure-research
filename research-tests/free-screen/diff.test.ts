// Original tests; data is captured from real synthetic files/Git at run time.
import { describe, expect, test, tier } from 'claude-code/testing'
import Git from '../hooks/git'
import data from './screen-data'

tier('builtin')

describe('FS01-real-state-replay', () => {
  for (const state of data.states) {
    test(state.label, async () => {
      const repository = await Git.repositoryOf(async argv => {
        expect([...argv]).toEqual(data.discovery_argv)
        return state.discovery
      })
      expect(repository).toEqual(state.repository)
      const transient = await Git.isTransient(async path => {
        const key = path.replaceAll('\\', '/')
        const listing = state.listings[key]
        expect(listing, 'all consulted directories were really captured').toBeDefined()
        return new Map(Object.entries(listing))
      }, repository!.gitDir)
      expect(transient).toBe(state.expected_transient)
    })
  }
})

describe('FS02-real-path-replay', () => {
  test('clean and dirty status retain actual supported path spellings', async () => {
    const read = async (answer: typeof data.paths.dirty) => Git.dirtyPathsOf(async argv => {
      expect([...argv]).toEqual(data.status_argv)
      return answer
    })
    expect([...(await read(data.paths.clean))!]).toEqual([])
    expect([...(await read(data.paths.dirty))!].sort()).toEqual([...data.paths.names, 'binary.dat'].sort())
  })

  test('real text and binary numstat retain exact counts and identities', () => {
    const parsed = Git.parseNumstat(data.paths.numstat.stdout, 50)
    expect(parsed.stats).toEqual({ filesCount: 4, linesAdded: 3, linesRemoved: 3 })
    expect(parsed.files.map(file => file.path).sort()).toEqual([...data.paths.names, 'binary.dat'].sort())
    expect(parsed.files.find(file => file.path === 'binary.dat')?.isBinary).toBe(true)
    for (const name of data.paths.names) {
      expect(parsed.files.find(file => file.path === name)).toMatchObject({ added: 1, removed: 1, isBinary: false })
    }
  })

  test('real raw patch bodies pair to space and non-ASCII paths', () => {
    const bodies = Git.parseFileDiffs(data.paths.patches.stdout, data.paths.names)
    expect([...bodies.keys()].sort()).toEqual([...data.paths.names].sort())
    for (const name of data.paths.names) {
      expect(JSON.stringify(bodies.get(name))).toContain('value=1')
      expect(JSON.stringify(bodies.get(name))).toContain('value=0')
    }
  })

  test('real staged rename retains both file identities without invented line edits', () => {
    const parsed = Git.parseNumstat(data.paths.rename.stdout, 50)
    expect(parsed.stats).toEqual({ filesCount: 1, linesAdded: 0, linesRemoved: 0 })
    expect(parsed.files[0]).toMatchObject({ path: 'new name.ts', renamedFrom: 'old name.ts', added: 0, removed: 0 })
  })
})
