<script setup lang="ts">
defineProps<{ modelValue: boolean; title: string; loading?: boolean }>()
defineEmits<{ confirm: []; cancel: [] }>()
</script>

<template>
  <Teleport to="body">
    <div v-if="modelValue" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4" role="dialog" aria-modal="true">
      <div class="w-full max-w-md rounded-lg bg-white p-5 shadow-lg">
        <h3 class="mb-2 text-base font-semibold text-slate-900">{{ title }}</h3>
        <p class="mb-4 text-sm text-slate-600"><slot /></p>
        <div class="flex justify-end gap-2">
          <button class="rounded-md border border-slate-300 px-3 py-1.5 text-sm hover:bg-slate-100" @click="$emit('cancel')">Cancel</button>
          <button class="rounded-md bg-red-600 px-3 py-1.5 text-sm text-white hover:bg-red-700 disabled:opacity-60" :disabled="loading" @click="$emit('confirm')">
            <span v-if="loading" class="mr-1 inline-block h-3 w-3 animate-spin rounded-full border-2 border-white/40 border-t-white"></span>
            Confirm
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>
