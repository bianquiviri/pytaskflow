<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useTasksStore } from '@/stores/tasks'
import { useDebouncedRef } from '@/composables/useDebouncedRef'
import { useAsyncAction } from '@/composables/useAsyncAction'
import AlertBanner from '@/components/AlertBanner.vue'
import AppPagination from '@/components/AppPagination.vue'
import TaskBadge from '@/components/TaskBadge.vue'
import BaseButton from '@/components/BaseButton.vue'
import { dueDateLabel, formatDate } from '@/utils/format'
import { watch } from 'vue'
import type { TaskFilters, TaskPriority, TaskStatus } from '@/types'

const store = useTasksStore()
const search = useDebouncedRef(store.filters.search ?? '', 350)

const load = useAsyncAction((filters?: Partial<TaskFilters>) => store.fetchTasks(filters))
const { run: fetchPage } = load

onMounted(() => fetchPage())
watch(search, (value) => store.fetchTasks({ search: value, page: 1 }))

const pageSize = computed(() => store.filters.page_size ?? 20)
const emptyState = computed(() => !store.loading && store.tasks.length === 0)

function applyFilter(patch: Partial<TaskFilters>) {
  fetchPage({ ...patch, page: 1 })
}
</script>

<template>
  <div>
    <div class="mb-4 flex flex-wrap items-center justify-between gap-3">
      <h2 class="text-xl font-bold text-slate-900">Tasks</h2>
      <RouterLink to="/tasks/new"><BaseButton>New task</BaseButton></RouterLink>
    </div>

    <div class="mb-4 flex flex-wrap gap-3">
      <input
        v-model="search"
        type="search"
        placeholder="Search tasks…"
        aria-label="Search tasks"
        class="w-full max-w-xs rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200 sm:w-64"
      />
      <select
        aria-label="Filter by status"
        :value="store.filters.status"
        class="rounded-md border border-slate-300 px-3 py-2 text-sm"
        @change="applyFilter({ status: ($event.target as HTMLSelectElement).value as TaskStatus | '' })"
      >
        <option value="">All statuses</option>
        <option value="todo">To do</option>
        <option value="in_progress">In progress</option>
        <option value="done">Done</option>
      </select>
      <select
        aria-label="Filter by priority"
        :value="store.filters.priority"
        class="rounded-md border border-slate-300 px-3 py-2 text-sm"
        @change="applyFilter({ priority: ($event.target as HTMLSelectElement).value as TaskPriority | '' })"
      >
        <option value="">All priorities</option>
        <option value="low">Low</option>
        <option value="medium">Medium</option>
        <option value="high">High</option>
      </select>
      <select
        aria-label="Order tasks"
        :value="store.filters.ordering"
        class="rounded-md border border-slate-300 px-3 py-2 text-sm"
        @change="applyFilter({ ordering: ($event.target as HTMLSelectElement).value })"
      >
        <option value="-created_at">Newest first</option>
        <option value="due_date">Due date (earliest)</option>
        <option value="-due_date">Due date (latest)</option>
        <option value="priority">Priority (low → high)</option>
        <option value="-priority">Priority (high → low)</option>
      </select>
    </div>

    <AlertBanner type="error" :message="store.error" />

    <div v-if="store.loading" class="space-y-2">
      <div v-for="i in 5" :key="i" class="h-12 animate-pulse rounded-md bg-slate-200"></div>
    </div>

    <p v-else-if="emptyState" class="rounded-lg border border-dashed border-slate-300 bg-white p-10 text-center text-sm text-slate-500">
      No tasks found. Create your first task to get started.
    </p>

    <div v-else class="overflow-hidden rounded-lg border border-slate-200 bg-white">
      <table class="w-full text-left text-sm">
        <thead class="bg-slate-100 text-xs uppercase text-slate-500">
          <tr>
            <th class="px-4 py-2">Title</th>
            <th class="px-4 py-2">Status</th>
            <th class="px-4 py-2">Priority</th>
            <th class="px-4 py-2">Due date</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="task in store.tasks" :key="task.id" class="border-t border-slate-200 hover:bg-slate-50">
            <td class="px-4 py-2">
              <RouterLink :to="{ name: 'task-detail', params: { id: task.id } }" class="font-medium text-blue-600 hover:underline">
                {{ task.title }}
              </RouterLink>
            </td>
            <td class="px-4 py-2"><TaskBadge kind="status" :value="task.status" /></td>
            <td class="px-4 py-2"><TaskBadge kind="priority" :value="task.priority" /></td>
            <td class="px-4 py-2">
              <span :class="{ 'font-semibold text-red-600': dueDateLabel(task.due_date) === 'overdue' }">
                {{ formatDate(task.due_date) }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <AppPagination :page="store.filters.page ?? 1" :count="store.count" :page-size="pageSize" @change="fetchPage({ page: $event })" />
  </div>
</template>
