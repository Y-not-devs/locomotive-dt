<template>
  <div class="panel p-6 shadow-lg">
    <div class="flex items-center justify-between">
      <p class="text-xs uppercase tracking-[0.3em] text-muted">{{ title }}</p>
      <span class="text-xs text-muted">Last 2 min</span>
    </div>
    <div class="mt-4 h-48">
      <VChart class="h-full w-full" :option="option" autoresize />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { use } from 'echarts/core'
import { LineChart } from 'echarts/charts'
import { GridComponent, LegendComponent, TooltipComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import VChart from 'vue-echarts'

use([LineChart, GridComponent, LegendComponent, TooltipComponent, CanvasRenderer])

type TrendPoint = {
  t: number
  v: number
}

type SeriesItem = {
  name: string
  color: string
  data: TrendPoint[]
}

interface Props {
  title: string
  series: SeriesItem[]
}

const props = defineProps<Props>()

const option = computed(() => ({
  animation: false,
  grid: { left: 12, right: 18, top: 24, bottom: 44, containLabel: true },
  tooltip: { trigger: 'axis' },
  legend: { top: 0, textStyle: { color: '#475569', fontSize: 11 } },
  dataZoom: [
    { type: 'inside', xAxisIndex: 0, filterMode: 'none' },
    { type: 'slider', xAxisIndex: 0, height: 16, bottom: 8 },
  ],
  xAxis: {
    type: 'time',
    axisLabel: { color: '#94a3b8', fontSize: 10 },
    axisLine: { lineStyle: { color: '#e2e8f0' } },
    splitLine: { show: false },
  },
  yAxis: {
    type: 'value',
    axisLabel: { color: '#94a3b8', fontSize: 10 },
    splitLine: { lineStyle: { color: '#e2e8f0' } },
  },
  series: props.series.map((item) => ({
    name: item.name,
    type: 'line',
    showSymbol: false,
    smooth: true,
    lineStyle: { width: 2, color: item.color },
    areaStyle: { color: `${item.color}22` },
    data: item.data.map((point) => [point.t, point.v]),
  })),
}))
</script>