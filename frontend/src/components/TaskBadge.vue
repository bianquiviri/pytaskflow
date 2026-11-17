<script setup lang="ts">
import type { TaskPriority, TaskStatus } from '@/types'
import { computed } from 'vue'

const props = defineProps<{ kind: 'status' | 'priority'; value: TaskStatus | TaskPriority }>()

const classes = computed(() => {
  if (props.kind === 'status') {
    const map: Record<TaskStatus, string> = {
      todo: 'bg-slate-200 text-slate-700',
      in_progress: 'bg-amber-100 text-amber-800',
      done: 'bg-green-100 text-green-800',
    }
    return map[props.value as TaskStatus] ?? 'bg-slate-200 text-slate-700'
  }
  const map: Record<TaskPriority, string> = {
    low: 'bg-blue-100 text-blue-700',
    medium: 'bg-orange-100 text-orange-700',
    high: 'bg-red-100 text-red-700',
  }
  return map[props.value as TaskPriority] ?? 'bg-slate-200 text-slate-700'
})

const labels: Record<string, string> = {
  todo: 'To do',
  in_progress: 'In progress',
  done: 'Done',
  low: 'Low',
  medium: 'Medium',
  high: 'High',
}
</script>

<template>
  <span :class="['inline-block rounded px-2 py-0.5 text-xs font-medium capitalize', classes]">{{ labels[value] ?? value }}</span>
</template>
