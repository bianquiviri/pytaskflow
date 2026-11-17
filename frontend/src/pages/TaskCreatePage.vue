<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { createTask } from '@/api/tasks'
import { errorMessage } from '@/api/client'
import AlertBanner from '@/components/AlertBanner.vue'
import BaseButton from '@/components/BaseButton.vue'
import TaskForm from '@/components/TaskForm.vue'
import type { TaskInput } from '@/types'

const router = useRouter()
const submitting = ref(false)
const error = ref<string | null>(null)

async function submit(payload: TaskInput) {
  submitting.value = true
  error.value = null
  try {
    const task = await createTask(payload)
    router.push({ name: 'task-detail', params: { id: task.id } })
  } catch (e) {
    error.value = errorMessage(e)
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="mx-auto max-w-2xl">
    <h2 class="mb-4 text-xl font-bold text-slate-900">New task</h2>
    <AlertBanner type="error" :message="error" />
    <div class="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
      <TaskForm submit-label="Create task" :loading="submitting" @submit="submit">
        <template #actions>
          <div class="flex gap-2">
            <BaseButton type="submit" :loading="submitting">Create task</BaseButton>
            <RouterLink to="/tasks"><BaseButton variant="secondary">Cancel</BaseButton></RouterLink>
          </div>
        </template>
      </TaskForm>
    </div>
  </div>
</template>
