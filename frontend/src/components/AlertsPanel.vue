<template>
  <div class="panel p-6 shadow-lg">
    <p class="text-xs uppercase tracking-[0.3em] text-muted">Alerts</p>
    <div class="mt-4 space-y-3 text-sm">
      <div
        v-for="alert in alerts"
        :key="alert.label"
        class="flex items-center justify-between rounded-xl border px-3 py-2"
        :class="levelClass[alert.level]"
      >
        {{ alert.label }}
        <span class="text-xs">{{ alert.tag }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface AlertItem {
  label: string
  level: 'ok' | 'watch' | 'high'
  tag: string
}

interface Props {
  alerts: AlertItem[]
}

defineProps<Props>()

const levelClass: Record<AlertItem['level'], string> = {
  ok: 'border-emerald-200 bg-emerald-50 text-emerald-700',
  watch: 'border-amber-200 bg-amber-50 text-amber-700',
  high: 'border-rose-200 bg-rose-50 text-rose-700',
}
</script>