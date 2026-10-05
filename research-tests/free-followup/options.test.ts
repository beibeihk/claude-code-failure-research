// Original N1 assertions. Only the private manifest default selects the mode.
import { describe, expect, test, tier } from 'claude-code/testing'
import type { On } from 'claude-code'
import data from './followup-data'

tier('builtin')
const BLOCKS = [{ name: 'claudeMd', text: '' }]
const EXISTING = 'existing tool context'

function world(on: On) {
  const walks: unknown[] = []
  on('session.root', () => ({ value: data.root }))
  on('session.cwd', () => ({ value: data.root }))
  on('env.get', () => ({ value: undefined }))
  on('ui.log', () => ({ value: undefined }))
  on('fs.ancestors', ($, e) => {
    walks.push(e)
    if (e.below !== undefined) {
      expect(e.below).toBe(data.root)
      expect(e.of).toBe(data.read_path)
      return { value: e.names.includes('AGENTS.md') ? data.nested : data.claude }
    }
    return { value: e.names.includes('AGENTS.md') ? data.initial : [] }
  })
  on('prompt.context', ($, e) => ({ blocks: e.blocks, instructionFiles: e.instructionFiles }))
  on('tool.call', ($, e) => {
    expect(e.tool).toBe('Read')
    expect(e.file_path).toBe(data.read_path)
    return { result: data.read_contents[e.file_path], context: [EXISTING] }
  })
  return walks
}

describe('N1-option-contract', () => {
  test('initial context preserves the exact mode-specific instruction list', async ($, on) => {
    world(on)
    const result = await $.prompt.context({ blocks: BLOCKS, instructionFiles: data.handed })
    const expected = data.mode === 'managed-only'
      ? data.handed.filter(file => ['managed', 'memory'].includes(file.kind))
      : data.mode === 'claude-md-and-agents-md'
        ? [...data.handed, ...data.initial.flatMap(entry => entry.parts.map(part => ({ ...part, kind: 'project' })))]
        : data.handed
    // Ordering is asserted separately from insertion by the engine's renderer.
    const sorted = (files: typeof expected) => [...files].sort((a, b) => a.path.localeCompare(b.path))
    expect(sorted(result.instructionFiles ?? [])).toEqual(sorted(expected))
    if (data.mode === 'claude-md-and-agents-md') {
      expect(result.blocks?.[0]?.text).toContain(data.initial[0].content.trim())
    }
  })

  test('nested delivery follows the option and preserves supplied tool context', async ($, on) => {
    const walks = world(on)
    await $.prompt.context({ blocks: BLOCKS, instructionFiles: data.handed })
    const result = await $.tool.call({ tool: 'Read', file_path: data.read_path })
    expect(result.context).toEqual(data.mode === 'claude-md-and-agents-md'
      ? [EXISTING, ...data.all_nested_frames] : [EXISTING])
    if (data.mode !== 'claude-md-and-agents-md') expect(walks).toEqual([])
  })

  test('already imported AGENTS is not duplicated and filtering remains exact', async ($, on) => {
    const walks = world(on)
    const imported = { ...data.initial[0].parts[0], kind: 'project' as const }
    const handed = [...data.handed, imported]
    const result = await $.prompt.context({ blocks: BLOCKS, instructionFiles: handed })
    const expected = data.mode === 'managed-only'
      ? handed.filter(file => ['managed', 'memory'].includes(file.kind)) : handed
    expect(result.instructionFiles).toEqual(expected)
    if (data.mode !== 'claude-md-and-agents-md') expect(walks).toEqual([])
    expect((result.instructionFiles ?? []).filter(file => file.path === imported.path)).toHaveLength(data.mode === 'managed-only' ? 0 : 1)
  })
})
