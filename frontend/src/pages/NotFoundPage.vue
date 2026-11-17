<script setup lang="ts">
</script>

<template>
  <div class="flex min-h-screen flex-col items-center justify-center bg-slate-50 px-4">
    <p class="text-6xl font-bold text-slate-300">404</p>
    <h2 class="mt-2 text-xl font-bold text-slate-900">Page not found</h2>
    <p class="mt-1 text-sm text-slate-600">The page you are looking for does not exist.</p>
    <RouterLink to="/" class="mt-4 rounded-md bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700">Go to dashboard</RouterLink>
  </div>
</template>
