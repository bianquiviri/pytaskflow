<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { deleteTask, getTask, patchTask } from '@/api/tasks'
import { errorMessage } from '@/api/client'
import AlertBanner from '@/components/AlertBanner.vue'
import TaskBadge from '@/components/TaskBadge.vue'
import BaseButton from '@/components/BaseButton.vue'
import BaseModal from '@/components/BaseModal.vue'
import { dueDateLabel, formatDateTime } from '@/utils/format'
import type { Task } from '@/types'

const route = useRoute()
const router = useRouter()
const taskId = route.params.id as string

const task = ref<Task | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)
const deleting = ref(false)
const showDeleteModal = ref(false)

onMounted(async () => {
  try {
    task.value = await getTask(taskId)
  } catch (e) {
    error.value = errorMessage(e)
  } finally {
    loading.value = false
  }
})

async function changeStatus(next: Task['status']) {
  if (!task.value) return
  try {
    task.value = await patchTask(taskId, { status: next })
  } catch (e) {
    error.value = errorMessage(e)
  }
}

async function confirmDelete() {
  deleting.value = true
  try {
    await deleteTask(taskId)
    router.push({ name: 'task-list' })
  } catch (e) {
    error.value = errorMessage(e)
    showDeleteModal.value = false
  } finally {
    deleting.value = false
  }
}
</script>

<template>
  <div class="mx-auto max-w-2xl">
    <AlertBanner type="error" :message="error" />
    <div v-if="loading" class="h-64 animate-pulse rounded-lg bg-slate-200"></div>
    <template v-else-if="task">
      <div class="mb-4 flex items-center justify-between">
        <h2 class="text-xl font-bold text-slate-900">{{ task.title }}</h2>
        <RouterLink :to="{ name: 'task-edit', params: { id: taskId } }">
          <BaseButton variant="secondary" size="sm">Edit</BaseButton>
        </RouterLink>
      </div>

      <div class="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
        <dl class="grid grid-cols-2 gap-x-4 gap-y-3 text-sm sm:grid-cols-3">
          <div>
            <dt class="text-slate-500">Status</dt>
            <dd class="mt-1"><TaskBadge kind="status" :value="task.status" /></dd>
          </div>
          <div>
            <dt class="text-slate-500">Priority</dt>
            <dd class="mt-1"><TaskBadge kind="priority" :value="task.priority" /></dd>
          </div>
          <div>
            <dt class="text-slate-500">Due date</dt>
            <dd class="mt-1" :class="{ 'font-semibold text-red-600': dueDateLabel(task.due_date) === 'overdue' }">
              {{ formatDateTime(task.due_date) }}
            </dd>
          </div>
          <div>
            <dt class="text-slate-500">Created</dt>
            <dd class="mt-1">{{ formatDateTime(task.created_at) }}</dd>
          </div>
          <div>
            <dt class="text-slate-500">Updated</dt>
            <dd class="mt-1">{{ formatDateTime(task.updated_at) }}</dd>
          </div>
          <div>
            <dt class="text-slate-500">Owner</dt>
            <dd class="mt-1">{{ task.owner_email }}</dd>
          </div>
        </dl>

        <div class="mt-4 border-t border-slate-200 pt-4">
          <dt class="text-slate-500">Description</dt>
          <dd class="mt-1 whitespace-pre-line text-sm text-slate-800">{{ task.description || 'No description.' }}</dd>
        </div>

        <div class="mt-4 flex flex-wrap items-center gap-2 border-t border-slate-200 pt-4">
          <span class="text-xs font-medium uppercase text-slate-500">Change status:</span>
          <BaseButton v-for="option in (['todo', 'in_progress', 'done'] as const)" :key="option" size="sm" variant="secondary" :disabled="task.status === option" @click="changeStatus(option)">
            {{ option.replace('_', ' ') }}
          </BaseButton>
          <BaseButton size="sm" variant="danger" class="ml-auto" @click="showDeleteModal = true">Delete</BaseButton>
        </div>
      </div>

      <BaseModal v-model="showDeleteModal" title="Delete this task?" :loading="deleting" @confirm="confirmDelete" @cancel="showDeleteModal = false">
        “{{ task.title }}” will be permanently removed. This action cannot be undone.
      </BaseModal>
    </template>
  </div>
</template>
