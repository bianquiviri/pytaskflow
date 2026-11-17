import { customRef } from 'vue'

/** Ref that propagates changes after a quiet period — used for search inputs. */
export function useDebouncedRef<T>(initial: T, delayMs = 350) {
  let timeout: ReturnType<typeof setTimeout> | undefined
  let value = initial
  return customRef<T>((track, trigger) => ({
    get() {
      track()
      return value
    },
    set(newValue: T) {
      clearTimeout(timeout)
      timeout = setTimeout(() => {
        value = newValue
        trigger()
      }, delayMs)
    },
  }))
}
