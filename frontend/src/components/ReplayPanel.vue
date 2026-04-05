<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

type TelemetryOut = {
	health: { score: number; status: string }
	telemetry: { timestamp: number }
}

type HistoryResponse = {
	items: TelemetryOut[]
}

const minutes = ref(10)
const loading = ref(false)
const error = ref<string | null>(null)
const lastCount = ref(0)
const lastTimestamp = ref<number | null>(null)

const defaultApiBase = `${window.location.protocol}//${window.location.hostname}:8000/api`
const apiBase = window.localStorage.getItem('api_base_url') ?? defaultApiBase
const apiKey = window.localStorage.getItem('api_key') ?? 'changeme'

const timeLabel = computed(() => {
	if (!lastTimestamp.value) return 'n/a'
	return new Date(lastTimestamp.value * 1000).toLocaleTimeString()
})

const refresh = async () => {
	loading.value = true
	error.value = null
	try {
		const response = await fetch(`${apiBase}/history?minutes=${minutes.value}`, {
			headers: { 'X-API-Key': apiKey },
		})
		if (!response.ok) {
			throw new Error(`HTTP ${response.status}`)
		}
		const data: HistoryResponse = await response.json()
		lastCount.value = data.items.length
		lastTimestamp.value = data.items.length
			? data.items[data.items.length - 1].telemetry.timestamp
			: null
	} catch (err) {
		error.value = err instanceof Error ? err.message : 'Failed to load history'
	} finally {
		loading.value = false
	}
}

const exportReport = async (format: 'csv' | 'pdf') => {
	loading.value = true
	error.value = null
	try {
		const response = await fetch(
			`${apiBase}/history/export/${format}?minutes=${minutes.value}`,
			{ headers: { 'X-API-Key': apiKey } }
		)
		if (!response.ok) {
			throw new Error(`HTTP ${response.status}`)
		}
		const blob = await response.blob()
		const filename = `telemetry-${minutes.value}m.${format}`
		downloadBlob(blob, filename)
	} catch (err) {
		error.value = err instanceof Error ? err.message : 'Export failed'
	} finally {
		loading.value = false
	}
}

const downloadBlob = (blob: Blob, filename: string) => {
	const url = window.URL.createObjectURL(blob)
	const anchor = document.createElement('a')
	anchor.href = url
	anchor.download = filename
	anchor.click()
	window.URL.revokeObjectURL(url)
}

onMounted(refresh)
</script>

<template>
	<div class="panel p-6 shadow-lg">
		<div class="flex items-center justify-between">
			<p class="text-xs uppercase tracking-[0.3em] text-muted">Replay & Export</p>
			<button class="text-xs text-muted" @click="refresh">Refresh</button>
		</div>

		<div class="mt-4 grid gap-3">
			<label class="text-xs text-muted">Replay window</label>
			<select v-model.number="minutes" class="rounded-lg border border-panel bg-white/60 px-3 py-2 text-sm">
				<option :value="5">Last 5 minutes</option>
				<option :value="10">Last 10 minutes</option>
				<option :value="15">Last 15 minutes</option>
			</select>
			<div class="flex items-center justify-between text-xs text-muted">
				<span>Records: {{ lastCount }}</span>
				<span>Latest: {{ timeLabel }}</span>
			</div>
		</div>

		<div class="mt-4 grid grid-cols-2 gap-3">
			<button
				class="rounded-xl border border-panel bg-white/80 px-3 py-2 text-sm transition hover:-translate-y-0.5 hover:border-emerald-400 hover:bg-emerald-50/80 hover:text-emerald-700 active:translate-y-0"
				:disabled="loading"
				@click="exportReport('csv')"
			>
				Export CSV
			</button>
			<button
				class="rounded-xl border border-panel bg-white/80 px-3 py-2 text-sm transition hover:-translate-y-0.5 hover:border-indigo-400 hover:bg-indigo-50/80 hover:text-indigo-700 active:translate-y-0"
				:disabled="loading"
				@click="exportReport('pdf')"
			>
				Export PDF
			</button>
		</div>

		<p v-if="error" class="mt-3 text-xs text-red-500">{{ error }}</p>
		<p v-else class="mt-3 text-xs text-muted">Use exports for reports and audit trails.</p>
	</div>
</template>
