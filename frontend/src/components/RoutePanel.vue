<script setup lang="ts">
import { computed } from 'vue'
interface Props {
  segment: string
  progress: number
}

const props = defineProps<Props>()
const markerX = computed(() => Math.min(96, Math.max(4, 4 + props.progress * 0.92)))
</script>

<template>
  <div class="panel p-6 shadow-lg">
    <div class="flex items-center justify-between">
      <p class="text-xs uppercase tracking-[0.3em] text-muted">Route Monitor</p>
      <span class="text-xs text-muted">{{ progress }}% complete</span>
    </div>

    <div class="mt-4 rounded-2xl border border-panel bg-white/40 p-4">
      <svg viewBox="0 0 100 40" class="h-24 w-full">
        <line x1="4" y1="20" x2="96" y2="20" stroke="var(--rail-base)" stroke-width="4" />
        <line x1="4" y1="20" :x2="markerX" y2="20" stroke="var(--rail-active)" stroke-width="4" />
        <circle :cx="markerX" cy="20" r="4" fill="#22c55e" stroke="#ffffff" stroke-width="1.5" />
        <circle cx="4" cy="20" r="3" fill="var(--rail-branch)" />
        <circle cx="96" cy="20" r="3" fill="var(--rail-branch)" />
      </svg>
    </div>

    <p class="mt-4 text-sm text-muted">{{ segment }}</p>
  </div>
</template>
