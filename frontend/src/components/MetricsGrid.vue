<template>
  <div class="mt-8 grid gap-4 md:grid-cols-2">
    <MetricCard
      v-for="item in items"
      :key="item.label"
      :label="item.label"
      :value="item.value"
      :unit="item.unit"
    />
  </div>
</template>

<script setup lang="ts">
import MetricCard from './MetricCard.vue'

interface MetricItem {
  label: string
  value: string | number
  unit: string
}

interface Props {
  items: MetricItem[]
}

defineProps<Props>()
</script>