<script setup lang="ts">
import { onMounted, ref } from 'vue'
import AlertBanner from '@/components/AlertBanner.vue'
import BaseCard from '@/components/BaseCard.vue'
import { errorMessage, } from '@/api/client'
import { fetchDashboardMetrics } from '@/api/tasks'
import type { DashboardMetrics } from '@/types'

const metrics = ref<DashboardMetrics | null>(null)
const error = ref<string | null>(null)
const loading = ref(true)

onMounted(async () => {
  try {
    metrics.value = await fetchDashboardMetrics()
  } catch (e) {
    error.value = errorMessage(e)
  } finally {
    loading.value = false
  }
})

const cards = [
  { key: 'total', label: 'Total tasks' },
  { key: 'todo', label: 'Pending (to do)' },
  { key: 'in_progress', label: 'In progress' },
  { key: 'done', label: 'Completed' },
  { key: 'high_priority', label: 'High priority' },
] as const
</script>

<template>
  <div>
    <h2 class="mb-4 text-xl font-bold text-slate-900">Dashboard</h2>
    <AlertBanner type="error" :message="error" />

    <div v-if="loading" class="grid grid-cols-1 gap-4 sm:grid-cols-3 lg:grid-cols-5">
      <div v-for="i in 5" :key="i" class="h-24 animate-pulse rounded-lg bg-slate-200"></div>
    </div>

    <div v-else-if="metrics" class="grid grid-cols-1 gap-4 sm:grid-cols-3 lg:grid-cols-5">
      <BaseCard v-for="card in cards" :key="card.key">
        <p class="text-3xl font-bold text-slate-900">{{ metrics[card.key] }}</p>
        <p class="mt-1 text-sm text-slate-600">{{ card.label }}</p>
      </BaseCard>
    </div>
  </div>
</template>
