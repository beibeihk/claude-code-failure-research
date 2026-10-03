// Original control/diagnostic tests; upstream helpers stay in the private overlay.
import { describe, expect, test, tier } from 'claude-code/testing'
import Fixtures from './fixtures'
import Limits from '../hooks/limits'

tier('builtin')

describe('research-merge-fixture-diagnostic', () => {
  for (const portableStub of [false, true]) {
    test(`virtual POSIX merge listing, portableStub=${portableStub}`, async ($, on) => {
      const script = { ...Fixtures.REPOSITORY, 'rev-parse --verify': 'merging' }
      let listing = Fixtures.MERGING.map(([name, kind]) => ({ name, kind, size: 0, isLink: false }))
      const paths: string[] = []
      on('fs.list', ($, e) => {
        paths.push(e.path)
        // This adapts only the /work synthetic fixture, not real path identity.
        // On Windows the engine canonicalizes /work into C:\work.
        const spelled = portableStub ? e.path.replaceAll('\\', '/').replace(/^[A-Za-z]:/, '') : e.path
        return { value: spelled === '/work/.git' ? listing : [] }
      })
      const world = Fixtures.inRepository(on, script)
      await $.session.start(Fixtures.SESSION)
      await $.command.run(Fixtures.DIFF)
      await world.clock.advance(300)
      const before = Fixtures.textOf(await $.ui.render(Fixtures.PANE))
      listing = []
      script['rev-parse --verify'] = 'merged'
      await world.clock.advance(Limits.HEAD_POLL_MS + Fixtures.SETTLE_MS)
      const after = Fixtures.textOf(await $.ui.render(Fixtures.PANE))
      console.log('RESEARCH_OBSERVATION ' + JSON.stringify({ portable_stub: portableStub, paths,
        before_unavailable: before.includes('Diff unavailable'), after_changed: after.includes('1 file changed') }))
      // The literal fixture is a negative control on Windows. It cannot answer
      // the engine's canonical C:\work\.git request; this is not a product bug.
      // This diagnostic protocol is registered for native Windows only.
      expect(before.includes('Diff unavailable')).toBe(portableStub)
      expect(after).toContain('1 file changed')
    })
  }

  test('without merge markers the pane shows the ordinary diff', async ($, on) => {
    on('fs.list', () => ({ value: [] }))
    const world = Fixtures.inRepository(on)
    await $.session.start(Fixtures.SESSION)
    await $.command.run(Fixtures.DIFF)
    await world.clock.advance(Fixtures.SETTLE_MS)
    expect(Fixtures.textOf(await $.ui.render(Fixtures.PANE))).toContain('1 file changed')
  })
})
