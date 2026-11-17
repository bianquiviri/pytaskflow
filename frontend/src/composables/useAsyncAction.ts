import { ref, type Ref } from 'vue'

/** Wraps an async action with loading + error state for buttons/forms. */
export function useAsyncAction<Args extends unknown[]>(action: (...args: Args) => Promise<unknown>) {
  const loading: Ref<boolean> = ref(false)
  const error: Ref<string | null> = ref(null)
  let lastError: unknown = null

  async function run(...args: Args): Promise<void> {
    loading.value = true
    error.value = null
    lastError = null
    try {
      await action(...args)
    } catch (e) {
      lastError = e
      error.value = e instanceof Error ? e.message : 'Something went wrong'
    } finally {
      loading.value = false
    }
  }

  return { loading, error, run, getLastError: () => lastError }
}
