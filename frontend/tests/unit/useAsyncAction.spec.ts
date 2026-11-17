import { describe, expect, it, vi } from 'vitest'
import { useAsyncAction } from '@/composables/useAsyncAction'

describe('useAsyncAction', () => {
  it('exposes loading while the action runs', async () => {
    let resolve: () => void = () => {}
    const action = vi.fn(() => new Promise<void>((r) => (resolve = r)))
    const { loading, error, run } = useAsyncAction(action)
    const pending = run()
    expect(loading.value).toBe(true)
    resolve()
    await pending
    expect(loading.value).toBe(false)
    expect(error.value).toBeNull()
  })

  it('captures errors without throwing', async () => {
    const action = vi.fn(async () => {
      throw new Error('boom')
    })
    const { error, run } = useAsyncAction(action)
    await run()
    expect(error.value).toBe('boom')
  })

  it('passes through arguments', async () => {
    const action = vi.fn(async (a: number, b: number) => a + b)
    const { run } = useAsyncAction(action)
    await run(2, 3)
    expect(action).toHaveBeenCalledWith(2, 3)
  })
})
