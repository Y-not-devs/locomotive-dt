<template>
  <div class="panel-card p-4">
    <p class="text-xs uppercase tracking-[0.3em] text-muted">{{ label }}</p>
    <div class="mt-4 flex items-end gap-2">
      <span class="text-3xl font-semibold text-strong">{{ value }}</span>
      <span class="text-sm text-muted">{{ unit }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  label: string
  value: string | number
  unit: string
}

const props = defineProps<Props>()
</script>