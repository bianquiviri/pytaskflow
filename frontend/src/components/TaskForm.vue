<script setup lang="ts">
import { computed } from 'vue'
import type { TaskInput, TaskPriority, TaskStatus } from '@/types'

defineProps<{ submitLabel?: string; loading?: boolean }>()

const emit = defineEmits<{ submit: [payload: TaskInput] }>()

// Editable field models bound by the parent page.
const title = defineModel<string>('title', { default: '' })
const description = defineModel<string>('description', { default: '' })
const status = defineModel<TaskStatus>('status', { default: 'todo' })
const priority = defineModel<TaskPriority>('priority', { default: 'medium' })
const dueDate = defineModel<string>('dueDate', { default: '' })

const titleError = computed(() => (title.value.trim() === '' ? 'Title is required.' : ''))

function submit() {
  if (titleError.value) return
  emit('submit', {
    title: title.value.trim(),
    description: description.value,
    status: status.value,
    priority: priority.value,
    due_date: dueDate.value ? new Date(dueDate.value).toISOString() : null,
  })
}
</script>

<template>
  <form novalidate class="space-y-4" @submit.prevent="submit">
    <div>
      <label for="task-title" class="mb-1 block text-sm font-medium text-slate-700">Title <span class="text-red-500">*</span></label>
      <input
        id="task-title"
        v-model="title"
        type="text"
        placeholder="What needs to be done?"
        class="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200"
        :class="{ 'border-red-400': titleError }"
        required
      />
      <p v-if="titleError" class="mt-1 text-xs text-red-600" role="alert">{{ titleError }}</p>
    </div>

    <div>
      <label for="task-description" class="mb-1 block text-sm font-medium text-slate-700">Description</label>
      <textarea
        id="task-description"
        v-model="description"
        rows="4"
        class="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200"
      ></textarea>
    </div>

    <div class="grid grid-cols-1 gap-4 sm:grid-cols-3">
      <div>
        <label for="task-status" class="mb-1 block text-sm font-medium text-slate-700">Status</label>
        <select id="task-status" v-model="status" class="w-full rounded-md border border-slate-300 px-3 py-2 text-sm">
          <option value="todo">To do</option>
          <option value="in_progress">In progress</option>
          <option value="done">Done</option>
        </select>
      </div>
      <div>
        <label for="task-priority" class="mb-1 block text-sm font-medium text-slate-700">Priority</label>
        <select id="task-priority" v-model="priority" class="w-full rounded-md border border-slate-300 px-3 py-2 text-sm">
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
        </select>
      </div>
      <div>
        <label for="task-due" class="mb-1 block text-sm font-medium text-slate-700">Due date</label>
        <input id="task-due" v-model="dueDate" type="datetime-local" class="w-full rounded-md border border-slate-300 px-3 py-2 text-sm" />
      </div>
    </div>

    <slot name="actions" :valid="!titleError" />
  </form>
</template>
