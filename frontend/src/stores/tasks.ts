import { defineStore } from 'pinia'
import { computed, reactive, ref } from 'vue'
import * as tasksApi from '@/api/tasks'
import type { Task, TaskFilters } from '@/types'

export const useTasksStore = defineStore('tasks', () => {
  const tasks = ref<Task[]>([])
  const count = ref(0)
  const filters = reactive<TaskFilters>({ status: '', priority: '', search: '', ordering: '-created_at', page: 1 })
  const loading = ref(false)
  const error = ref<string | null>(null)

  const hasNextPage = computed(() => filters.page !== undefined && count.value > filters.page * (filters.page_size ?? 20))
  const hasPreviousPage = computed(() => (filters.page ?? 1) > 1)

  async function fetchTasks(nextFilters: Partial<TaskFilters> = {}): Promise<void> {
    Object.assign(filters, nextFilters)
    loading.value = true
    error.value = null
    try {
      const page = await tasksApi.listTasks(filters)
      tasks.value = page.results
      count.value = page.count
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to load tasks'
      throw e
    } finally {
      loading.value = false
    }
  }

  function reset(): void {
    Object.assign(filters, { status: '', priority: '', search: '', ordering: '-created_at', page: 1 })
    tasks.value = []
    count.value = 0
  }

  return { tasks, count, filters, loading, error, hasNextPage, hasPreviousPage, fetchTasks, reset }
})
