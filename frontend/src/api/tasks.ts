import type { DashboardMetrics, Paginated, Task, TaskFilters, TaskInput } from '@/types'
import { http } from './client'

const BASE = '/tasks/'

export async function listTasks(filters: TaskFilters = {}): Promise<Paginated<Task>> {
  const params: Record<string, unknown> = { ...filters }
  for (const key of Object.keys(params)) {
    if (params[key] === '' || params[key] === undefined || params[key] === null) delete params[key]
  }
  const { data } = await http.get<Paginated<Task>>(BASE, { params })
  return data
}

export async function getTask(id: string): Promise<Task> {
  const { data } = await http.get<Task>(`${BASE}${id}/`)
  return data
}

export async function createTask(payload: TaskInput): Promise<Task> {
  const { data } = await http.post<Task>(BASE, payload)
  return data
}

export async function updateTask(id: string, payload: TaskInput): Promise<Task> {
  const { data } = await http.put<Task>(`${BASE}${id}/`, payload)
  return data
}

export async function patchTask(id: string, payload: Partial<TaskInput>): Promise<Task> {
  const { data } = await http.patch<Task>(`${BASE}${id}/`, payload)
  return data
}

export async function deleteTask(id: string): Promise<void> {
  await http.delete(`${BASE}${id}/`)
}

/** Dashboard metrics are computed from the user's own tasks via the list API. */
export async function fetchDashboardMetrics(): Promise<DashboardMetrics> {
  const data = await listTasks({ page_size: 100 })
  let page: string | null = data.next
  const tasks: Task[] = [...data.results]
  while (page) {
    const { data: next } = await http.get<Paginated<Task>>(page)
    tasks.push(...next.results)
    page = next.next
  }
  return {
    total: data.count,
    todo: tasks.filter((t) => t.status === 'todo').length,
    in_progress: tasks.filter((t) => t.status === 'in_progress').length,
    done: tasks.filter((t) => t.status === 'done').length,
    high_priority: tasks.filter((t) => t.priority === 'high').length,
  }
}
