<script setup lang="ts">
import { computed } from 'vue'
interface Props {
  segment: string
  progress: number
}

const props = defineProps<Props>()
const markerX = computed(() => Math.min(96, Math.max(4, 4 + props.progress * 0.92)))

const speedLimits = [
  { at: 22, speed: 70 },
  { at: 46, speed: 60 },
  { at: 73, speed: 80 },
]

const speedMarkers = computed(() =>
  speedLimits.map((limit) => ({
    x: Math.min(96, Math.max(4, 4 + limit.at * 0.92)),
    speed: limit.speed,
  }))
)
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
        <g v-for="(limit, index) in speedMarkers" :key="index">
          <line :x1="limit.x" y1="14" :x2="limit.x" y2="26" stroke="var(--rail-alert)" stroke-width="1.5" />
          <circle :cx="limit.x" cy="12" r="3.2" fill="var(--rail-alert)" />
          <text :x="limit.x" y="8" text-anchor="middle" font-size="4" fill="var(--rail-alert)">
            {{ limit.speed }}
          </text>
        </g>
        <circle :cx="markerX" cy="20" r="4" fill="#22c55e" stroke="#ffffff" stroke-width="1.5" />
        <circle cx="4" cy="20" r="3" fill="var(--rail-branch)" />
        <circle cx="96" cy="20" r="3" fill="var(--rail-branch)" />
      </svg>
    </div>

    <p class="mt-4 text-sm text-muted">{{ segment }}</p>
    <p class="mt-2 text-xs text-muted">Speed limits marked on track.</p>
  </div>
</template>
