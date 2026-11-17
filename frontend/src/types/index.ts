/** Domain types mirroring the TaskFlow API contracts (docs/api/conventions.md). */

export type TaskStatus = 'todo' | 'in_progress' | 'done'
export type TaskPriority = 'low' | 'medium' | 'high'

export interface User {
  id: string
  email: string
  first_name: string
  last_name: string
  full_name: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface AuthTokens {
  access: string
  refresh: string
}

export interface Task {
  id: string
  title: string
  description: string
  status: TaskStatus
  priority: TaskPriority
  due_date: string | null
  owner_email: string
  created_at: string
  updated_at: string
}

export interface Paginated<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export interface DashboardMetrics {
  total: number
  todo: number
  in_progress: number
  done: number
  high_priority: number
}

export interface TaskInput {
  title: string
  description: string
  status: TaskStatus
  priority: TaskPriority
  due_date: string | null
}

export interface TaskFilters {
  status?: TaskStatus | ''
  priority?: TaskPriority | ''
  search?: string
  ordering?: string
  page?: number
  page_size?: number
}
