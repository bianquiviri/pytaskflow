<script setup lang="ts">
defineProps<{
  modelValue: string
  label: string
  type?: string
  required?: boolean
  autocomplete?: string
  placeholder?: string
  error?: string
}>()

defineEmits<{ 'update:modelValue': [value: string] }>()
</script>

<template>
  <div class="mb-4">
    <label :for="label" class="mb-1 block text-sm font-medium text-slate-700">
      {{ label }}<span v-if="required" class="text-red-500"> *</span>
    </label>
    <input
      :id="label"
      :type="type ?? 'text'"
      :value="modelValue"
      :required="required"
      :autocomplete="autocomplete"
      :placeholder="placeholder"
      :aria-invalid="error ? 'true' : 'false'"
      class="w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-200"
      :class="{ 'border-red-400 focus:border-red-500 focus:ring-red-200': error }"
      @input="$emit('update:modelValue', ($event.target as HTMLInputElement).value)"
    />
    <p v-if="error" class="mt-1 text-xs text-red-600" role="alert">{{ error }}</p>
  </div>
</template>
