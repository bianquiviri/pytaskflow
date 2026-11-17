<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getTask, updateTask } from '@/api/tasks'
import { errorMessage } from '@/api/client'
import AlertBanner from '@/components/AlertBanner.vue'
import BaseButton from '@/components/BaseButton.vue'
import TaskForm from '@/components/TaskForm.vue'
import { fromDatetimeLocal, toDatetimeLocal } from '@/utils/format'
import type { Task, TaskInput, TaskPriority, TaskStatus } from '@/types'

const route = useRoute()
const router = useRouter()

const taskId = route.params.id as string
const loading = ref(true)
const submitting = ref(false)
const error = ref<string | null>(null)

const title = ref('')
const description = ref('')
const status = ref<TaskStatus>('todo')
const priority = ref<TaskPriority>('medium')
const dueDate = ref('')

onMounted(async () => {
  try {
    const task: Task = await getTask(taskId)
    title.value = task.title
    description.value = task.description
    status.value = task.status
    priority.value = task.priority
    dueDate.value = toDatetimeLocal(task.due_date)
  } catch (e) {
    error.value = errorMessage(e)
  } finally {
    loading.value = false
  }
})

async function submit(payload: TaskInput) {
  submitting.value = true
  error.value = null
  try {
    await updateTask(taskId, { ...payload, due_date: fromDatetimeLocal(dueDate.value) })
    router.push({ name: 'task-detail', params: { id: taskId } })
  } catch (e) {
    error.value = errorMessage(e)
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="mx-auto max-w-2xl">
    <h2 class="mb-4 text-xl font-bold text-slate-900">Edit task</h2>
    <AlertBanner type="error" :message="error" />
    <div v-if="loading" class="h-64 animate-pulse rounded-lg bg-slate-200"></div>
    <div v-else class="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
      <TaskForm submit-label="Save changes" :loading="submitting" @submit="submit">
        <template #actions>
          <div class="flex gap-2">
            <BaseButton type="submit" :loading="submitting">Save changes</BaseButton>
            <RouterLink :to="{ name: 'task-detail', params: { id: taskId } }">
              <BaseButton variant="secondary">Cancel</BaseButton>
            </RouterLink>
          </div>
        </template>
      </TaskForm>
    </div>
  </div>
</template>
