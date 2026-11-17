<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{ page: number; count: number; pageSize: number }>()
const emit = defineEmits<{ change: [page: number] }>()

const totalPages = computed(() => Math.max(1, Math.ceil(props.count / props.pageSize)))
const hasPrev = computed(() => props.page > 1)
const hasNext = computed(() => props.page < totalPages.value)
</script>

<template>
  <nav v-if="count > 0" class="mt-4 flex items-center justify-between" aria-label="Pagination">
    <button
      class="rounded border border-slate-300 px-3 py-1.5 text-sm hover:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-50"
      :disabled="!hasPrev"
      @click="hasPrev && emit('change', page - 1)"
    >
      Previous
    </button>
    <span class="text-sm text-slate-600">Page {{ page }} of {{ totalPages }} ({{ count }} tasks)</span>
    <button
      class="rounded border border-slate-300 px-3 py-1.5 text-sm hover:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-50"
      :disabled="!hasNext"
      @click="hasNext && emit('change', page + 1)"
    >
      Next
    </button>
  </nav>
</template>
