<script setup lang="ts">
defineProps<{ type?: 'info' | 'error' | 'success'; message: string | null }>()
</script>

<template>
  <div
    v-if="message"
    role="alert"
    :class="[
      'mb-4 rounded-md border px-3 py-2 text-sm',
      type === 'error' ? 'border-red-300 bg-red-50 text-red-700' : '',
      type === 'success' ? 'border-green-300 bg-green-50 text-green-700' : '',
      (!type || type === 'info') ? 'border-blue-300 bg-blue-50 text-blue-700' : '',
    ]"
  >
    {{ message }}
  </div>
</template>
