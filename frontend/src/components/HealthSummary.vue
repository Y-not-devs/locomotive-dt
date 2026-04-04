<template>
  <section class="panel p-6 shadow-lg">
    <div class="flex items-start justify-between">
      <div>
        <p class="text-xs uppercase tracking-[0.35em] text-muted">Health Index</p>
        <div class="mt-2 text-5xl font-semibold text-strong">{{ score }}</div>
        <p class="mt-2 text-sm text-muted">Status: {{ status }}</p>
      </div>
      <div class="flex flex-col gap-2 text-sm text-slate-600">
        <div
          v-for="factor in factors"
          :key="factor"
          class="rounded-xl border border-panel bg-white/60 px-3 py-2"
        >
          Top factor: {{ factor }}
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
interface Props {
  score: number
  status: string
  factors: string[]
}

defineProps<Props>()
</script>