<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import AppHeader from './components/AppHeader.vue'
import AlertsPanel from './components/AlertsPanel.vue'
import HealthSummary from './components/HealthSummary.vue'
import MetricsGrid from './components/MetricsGrid.vue'
import RoutePanel from './components/RoutePanel.vue'
import TelemetryTrends from './components/TelemetryTrends.vue'
import { useTelemetry } from './composables/useTelemetry'

type AlertItem = {
	label: string
	level: 'ok' | 'watch' | 'high'
	tag: string
}

const { telemetry, health, status, lastUpdatedAge, trends } = useTelemetry()

const metrics = computed(() => [
	{ label: 'Speed', value: Math.round(telemetry.speed), unit: 'km/h' },
	{ label: 'Brake Pressure', value: telemetry.brake_pressure.toFixed(1), unit: 'bar' },
	{ label: 'Fuel', value: Math.round(telemetry.fuel_level).toLocaleString(), unit: 'liters' },
	{ label: 'Power', value: Math.round(telemetry.voltage), unit: 'V' },
])

const alerts = computed<AlertItem[]>(() => {
	if (!telemetry.alerts.length) {
		return [{ label: 'No active alerts', level: 'ok', tag: 'OK' }]
	}
	return telemetry.alerts.map((alert) => ({
		label: alert.replace(/_/g, ' '),
		level: 'high',
		tag: 'Alert',
	}))
})

const factors = computed(() =>
	health.top_factors.length
		? health.top_factors.map((factor) => factor.name)
		: ['n/a']
)

const statusLabel = computed(() => (status.value === 'online' ? 'Online' : 'Offline'))
const theme = ref<'light' | 'dark'>('light')

const toggleTheme = () => {
	theme.value = theme.value === 'light' ? 'dark' : 'light'
}

onMounted(() => {
	const saved = localStorage.getItem('theme')
	if (saved === 'light' || saved === 'dark') {
		theme.value = saved
	} else if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
		theme.value = 'dark'
	}
})

watch(
	theme,
	(value) => {
		document.documentElement.classList.toggle('theme-dark', value === 'dark')
		localStorage.setItem('theme', value)
	},
	{ immediate: true }
)

const speedSeries = computed(() => [
	{ name: 'Speed', color: '#0f766e', data: trends.speed },
	{ name: 'Brake', color: '#eab308', data: trends.brake_pressure },
])

const tempSeries = computed(() => [
	{ name: 'Engine', color: '#dc2626', data: trends.temp_engine },
	{ name: 'Oil', color: '#f97316', data: trends.temp_oil },
])

const electricalSeries = computed(() => [
	{ name: 'Voltage', color: '#2563eb', data: trends.voltage },
	{ name: 'Current', color: '#7c3aed', data: trends.current },
])

const routeProgress = computed(() => (telemetry.timestamp ? telemetry.timestamp % 100 : 0))
</script>

<template>
	<div class="min-h-screen grid-overlay">
		<AppHeader
			:status-label="statusLabel"
			:last-updated="lastUpdatedAge"
			:theme="theme"
			route-label="Route A-17"
			@toggle-theme="toggleTheme"
		/>

		<main class="mx-auto grid w-full max-w-6xl gap-6 px-6 pb-12 lg:grid-cols-[2fr,1fr]">
			<section class="space-y-6">
				<HealthSummary :score="health.score" :status="health.status" :factors="factors" />
				<MetricsGrid :items="metrics" />
				<div class="grid gap-6 xl:grid-cols-2">
					<TelemetryTrends title="Speed & Brake Pressure" :series="speedSeries" />
					<TelemetryTrends title="Temps" :series="tempSeries" />
				</div>
				<TelemetryTrends title="Electrical" :series="electricalSeries" />
			</section>

			<aside class="flex flex-col gap-6">
				<RoutePanel :progress="routeProgress" segment="Current segment: 142 km to checkpoint." />
				<AlertsPanel :alerts="alerts" />
			</aside>
		</main>
	</div>
</template>
