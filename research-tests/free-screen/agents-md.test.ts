// Original engine-hook tests. Walk replies use bytes from real fixture files.
import { describe, expect, test, tier } from 'claude-code/testing'
import type { On } from 'claude-code'
import data from './screen-data'

tier('builtin')

const BLOCKS = [{ name: 'claudeMd', text: '' }]
type World = typeof data.instructions.plain

function world(on: On, fixture: World) {
  let failed = false
  on('session.root', () => ({ value: fixture.root }))
  on('session.cwd', () => ({ value: fixture.root }))
  on('env.get', () => ({ value: undefined }))
  on('ui.log', () => ({ value: undefined }))
  on('fs.ancestors', ($, e) => {
    if (e.below !== undefined) {
      expect(e.below).toBe(fixture.root)
      expect([fixture.read_path, fixture.instruction_path]).toContain(e.of)
      const agents = e.of === fixture.instruction_path ? fixture.nested.slice(0, 1) : fixture.nested
      return { value: e.names.includes('AGENTS.md') ? agents : fixture.claude }
    }
    return { value: e.names.includes('AGENTS.md') ? fixture.initial : [] }
  })
  on('prompt.context', ($, e) => ({ blocks: e.blocks, instructionFiles: e.instructionFiles }))
  on('tool.call', ($, e) => {
    expect(e.tool).toBe('Read')
    if (failed) return { result: 'fixture read failed', isError: true }
    expect(fixture.read_contents[e.file_path]).toBeDefined()
    const content = fixture.read_contents[e.file_path]
    return { result: e.limit === undefined ? content : content.split('\n').slice(0, e.limit).join('\n') }
  })
  return { fail: (value: boolean) => { failed = value } }
}

describe('FS03-real-instruction-replay', () => {
  test('first successful nested Read attaches exact bytes once; new context resets delivery', async ($, on) => {
    const fixture = data.instructions.plain
    world(on, fixture)
    const initial = await $.prompt.context({ blocks: BLOCKS, instructionFiles: [] })
    expect(initial.instructionFiles?.map(file => file.content)).toEqual(fixture.initial.map(file => file.content))
    const call = { tool: 'Read' as const, file_path: fixture.read_path }
    expect((await $.tool.call(call)).context).toEqual(fixture.expected_frames)
    expect((await $.tool.call(call)).context ?? []).toEqual([])
    await $.prompt.context({ blocks: BLOCKS, instructionFiles: [] })
    expect((await $.tool.call(call)).context).toEqual(fixture.expected_frames)
  })

  test('failed Read consumes no delivery; subsequent successful Read attaches', async ($, on) => {
    const fixture = data.instructions.plain
    const control = world(on, fixture)
    await $.prompt.context({ blocks: BLOCKS, instructionFiles: [] })
    control.fail(true)
    const call = { tool: 'Read' as const, file_path: fixture.read_path }
    expect((await $.tool.call(call)).context ?? []).toEqual([])
    control.fail(false)
    expect((await $.tool.call(call)).context).toEqual(fixture.expected_frames)
  })

  test('sibling root gets no nested attachment; inside-root positive control still attaches', async ($, on) => {
    const fixture = data.instructions.plain
    world(on, fixture)
    await $.prompt.context({ blocks: BLOCKS, instructionFiles: [] })
    expect((await $.tool.call({ tool: 'Read', file_path: fixture.sibling_path })).context ?? []).toEqual([])
    expect((await $.tool.call({ tool: 'Read', file_path: fixture.read_path })).context).toEqual(fixture.expected_frames)
  })

  test('whole direct instruction Read marks that file delivered', async ($, on) => {
    const fixture = data.instructions.plain
    world(on, fixture)
    await $.prompt.context({ blocks: BLOCKS, instructionFiles: [] })
    expect((await $.tool.call({ tool: 'Read', file_path: fixture.instruction_path })).context ?? []).toEqual([])
    expect((await $.tool.call({ tool: 'Read', file_path: fixture.read_path })).context).toEqual(fixture.expected_frames.slice(1))
  })

  test('partial direct instruction Read does not suppress later full attachment', async ($, on) => {
    const fixture = data.instructions.plain
    world(on, fixture)
    await $.prompt.context({ blocks: BLOCKS, instructionFiles: [] })
    expect((await $.tool.call({ tool: 'Read', file_path: fixture.instruction_path, limit: 1 })).context ?? []).toEqual([])
    expect((await $.tool.call({ tool: 'Read', file_path: fixture.read_path })).context).toEqual(fixture.expected_frames)
  })

  test('nested CLAUDE claims its own directory while a deeper AGENTS still attaches', async ($, on) => {
    const fixture = data.instructions.claimed
    world(on, fixture)
    await $.prompt.context({ blocks: BLOCKS, instructionFiles: [] })
    expect((await $.tool.call({ tool: 'Read', file_path: fixture.read_path })).context).toEqual(fixture.expected_frames)
    expect(fixture.expected_frames).toHaveLength(1)
  })
})
