<script setup lang="ts">
defineProps<{ title?: string }>()
</script>

<template>
  <section class="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
    <h2 v-if="title" class="mb-3 text-sm font-semibold text-slate-700">{{ title }}</h2>
    <slot />
  </section>
</template>
