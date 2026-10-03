// Original research tests; upstream fixture helpers are linked at run time only.
import { describe, expect, test, tier } from 'claude-code/testing'
import Fixtures from './fixtures'
import Files from '../hooks/files'
import Frames from '../hooks/frames'

tier('builtin')

const BLOCKS = [{ name: 'claudeMd', text: 'original' }]

describe('research-instruction-contract', () => {
  test('fallback delivers AGENTS when the project has no CLAUDE', async ($, on) => {
    Fixtures.projectOf(on, [Fixtures.ancestorOf('/repo/a/b', 'AGENTS.md', 'Run checks.')], [])
    on('prompt.context', ($, e) => ({ blocks: e.blocks, instructionFiles: e.instructionFiles }))
    const context = await $.prompt.context({ blocks: BLOCKS, instructionFiles: [] })
    expect(context.instructionFiles?.map(file => file.content)).toEqual(['Run checks.'])
  })

  test('a project CLAUDE disables the fallback', async ($, on) => {
    Fixtures.projectOf(on, [Fixtures.ancestorOf('/repo/a/b', 'AGENTS.md', 'Run checks.')],
      [Fixtures.ancestorOf('/repo/a/b', 'CLAUDE.md', 'Use project policy.')])
    on('prompt.context', ($, e) => ({ blocks: e.blocks, instructionFiles: e.instructionFiles }))
    const handed = [{ path: '/repo/a/b/CLAUDE.md', kind: 'project' as const, content: 'Use project policy.' }]
    expect((await $.prompt.context({ blocks: BLOCKS, instructionFiles: handed })).instructionFiles).toEqual(handed)
  })

  test('an unreadable instruction walk preserves the existing context', async ($, on) => {
    Fixtures.unreadableProjectOf(on)
    on('prompt.context', ($, e) => ({ blocks: e.blocks, instructionFiles: e.instructionFiles }))
    expect(await $.prompt.context({ blocks: BLOCKS, instructionFiles: [] })).toEqual({ blocks: BLOCKS, instructionFiles: [] })
  })

  test('an imported AGENTS path is not loaded again with mixed separators', () => {
    const file = { path: 'C:\\repo\\AGENTS.md', kind: 'project' as const, content: 'Run checks.' }
    expect(Files.unseenFiles([file], [{ ...file, path: 'C:/repo/AGENTS.md' }])).toEqual([])
  })

  test('equal project instruction content deduplicates a linked file', () => {
    const file = { path: '/repo/AGENTS.md', kind: 'project' as const, content: 'Run checks.\n' }
    expect(Files.unseenFiles([file], [{ ...file, path: '/repo/CLAUDE.md', content: 'Run checks.' }])).toEqual([])
  })

  test('equal user content does not suppress the project instruction', () => {
    const file = { path: '/repo/AGENTS.md', kind: 'project' as const, content: 'Run checks.' }
    expect(Files.unseenFiles([file], [{ ...file, path: '/home/.claude/CLAUDE.md', kind: 'user' as const }])).toEqual([file])
  })

  test('a sibling directory is outside the nested instruction boundary', () => {
    expect(Frames.isBelow('/repo-extra/src/file.ts', '/repo')).toBe(false)
    expect(Frames.isBelow('/repo/src/file.ts', '/repo')).toBe(true)
  })

  test('managed-only filtering preserves managed instructions and removes project instructions', () => {
    const base = { path: '/fixture/CLAUDE.md', content: 'Policy.' }
    expect(Files.isKeptWithoutInstructions({ ...base, kind: 'managed' })).toBe(true)
    expect(Files.isKeptWithoutInstructions({ ...base, kind: 'project' })).toBe(false)
  })
})
