<script setup lang="ts">
interface Props {
  statusLabel: string
  routeLabel: string
  lastUpdated: number | null
  theme: 'light' | 'dark'
}

defineProps<Props>()
const emit = defineEmits<{ (e: 'toggle-theme'): void }>()
</script>

<template>
  <header class="mx-auto flex w-full max-w-6xl items-center justify-between px-6 py-6">
    <div>
      <p class="text-xs uppercase tracking-[0.3em] text-muted">Locomotive DT</p>
      <h1 class="text-2xl font-semibold text-strong">Cabin Control Dashboard</h1>
    </div>
    <div class="flex items-center gap-3 text-sm text-muted">
      <div
        class="rounded-full border px-3 py-1"
        :class="
          statusLabel === 'Online'
            ? 'border-emerald-600/40 bg-emerald-50 text-emerald-700'
            : 'border-rose-600/40 bg-rose-50 text-rose-700'
        "
      >
        {{ statusLabel }}
      </div>
      <div class="rounded-full border border-panel px-3 py-1">
        {{ lastUpdated === null ? 'No data yet' : `Updated ${lastUpdated}s ago` }}
      </div>
      <div class="rounded-full border border-panel px-3 py-1">{{ routeLabel }}</div>
      <div class="flex items-center gap-2">
        <span class="text-xs text-muted">Theme</span>
        <button
          type="button"
          class="toggle"
          role="switch"
          :aria-checked="theme === 'dark'"
          aria-label="Toggle theme"
          @click="emit('toggle-theme')"
        >
          <span class="toggle-track" :class="theme === 'dark' ? 'is-dark' : ''">
            <span class="toggle-thumb"></span>
          </span>
        </button>
      </div>
    </div>
  </header>
</template>