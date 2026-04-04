import { computed, onBeforeUnmount, onMounted, reactive, ref } from 'vue'

type HealthFactor = {
  name: string
  impact: number
}

type HealthIndex = {
  score: number
  status: string
  top_factors: HealthFactor[]
}

type TelemetrySnapshot = {
  timestamp: number
  speed: number
  traction_force: number
  brake_pressure: number
  fuel_level: number
  voltage: number
  current: number
  temp_oil: number
  temp_engine: number
  alerts: string[]
}

type TrendPoint = {
  t: number
  v: number
}

type StreamPayload = {
  telemetry: TelemetrySnapshot
  health: HealthIndex
}

const defaults: TelemetrySnapshot = {
  timestamp: 0,
  speed: 0,
  traction_force: 0,
  brake_pressure: 0,
  fuel_level: 0,
  voltage: 0,
  current: 0,
  temp_oil: 0,
  temp_engine: 0,
  alerts: [],
}

const defaultHealth: HealthIndex = {
  score: 0,
  status: 'unknown',
  top_factors: [],
}

export function useTelemetry() {
  const telemetry = reactive<TelemetrySnapshot>({ ...defaults })
  const health = reactive<HealthIndex>({ ...defaultHealth })
  const status = ref<'online' | 'offline'>('offline')
  const lastUpdated = ref<number | null>(null)
  const trends = reactive({
    speed: [] as TrendPoint[],
    brake_pressure: [] as TrendPoint[],
    temp_engine: [] as TrendPoint[],
    temp_oil: [] as TrendPoint[],
    voltage: [] as TrendPoint[],
    current: [] as TrendPoint[],
  })
  let socket: WebSocket | null = null
  let reconnectTimer: number | undefined

  const wsUrl = import.meta.env.VITE_WS_URL ?? 'ws://localhost:8000/ws/telemetry'
  const apiKey = import.meta.env.VITE_API_KEY ?? 'changeme'

  const connect = () => {
    if (socket) {
      socket.close()
    }
    status.value = 'offline'
    socket = new WebSocket(`${wsUrl}?api_key=${encodeURIComponent(apiKey)}`)

    socket.onopen = () => {
      status.value = 'offline'
    }

    socket.onmessage = (event) => {
      try {
        const payload: StreamPayload = JSON.parse(event.data)
        Object.assign(telemetry, payload.telemetry)
        Object.assign(health, payload.health)
        lastUpdated.value = Date.now()
        status.value = 'online'
        const timestamp = payload.telemetry.timestamp * 1000
        pushPoint(trends.speed, timestamp, payload.telemetry.speed)
        pushPoint(trends.brake_pressure, timestamp, payload.telemetry.brake_pressure)
        pushPoint(trends.temp_engine, timestamp, payload.telemetry.temp_engine)
        pushPoint(trends.temp_oil, timestamp, payload.telemetry.temp_oil)
        pushPoint(trends.voltage, timestamp, payload.telemetry.voltage)
        pushPoint(trends.current, timestamp, payload.telemetry.current)
      } catch {
        status.value = 'offline'
      }
    }

    socket.onclose = () => {
      status.value = 'offline'
      reconnectTimer = window.setTimeout(connect, 1500)
    }

    socket.onerror = () => {
      status.value = 'offline'
      socket?.close()
    }
  }

  onMounted(() => {
    connect()
  })

  onBeforeUnmount(() => {
    if (reconnectTimer) {
      window.clearTimeout(reconnectTimer)
    }
    socket?.close()
  })

  const lastUpdatedAge = computed(() => {
    if (!lastUpdated.value) {
      return null
    }
    return Math.floor((Date.now() - lastUpdated.value) / 1000)
  })

  return { telemetry, health, status, lastUpdated, lastUpdatedAge, trends }
}

function pushPoint(target: TrendPoint[], timestamp: number, value: number) {
  target.push({ t: timestamp, v: value })
  if (target.length > 120) {
    target.splice(0, target.length - 120)
  }
}
