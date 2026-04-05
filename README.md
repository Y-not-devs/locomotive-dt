# Цифровой двойник локомотива

Визуальный цифровой двойник с дашбордом телеметрии в реальном времени, индексом здоровья и потоковым бэкендом.

## Стек

- Frontend: Vue 3 + TypeScript + Vite + Bun
- Realtime: WebSocket
- Backend: FastAPI + Python
- Документация API: Swagger / OpenAPI
- Хранилище: SQLite
- Инфраструктура: Docker Compose

## Назначение

- Дашборд телеметрии в реальном времени (скорость, давление, температура, электрика, алерты)
- Индекс здоровья с топ‑факторами влияния
- Прогресс по маршруту
- Окно replay и экспорт отчетов (CSV/PDF)
- Потоковая доставка с реконнектом + симулятор для демо

## Структура репозитория

```text
.
|-- backend/                 # FastAPI сервис, WebSocket хаб, доменные сервисы
|   |-- src/                 # Актуальный код бэкенда (FastAPI + сервисы)
|   |-- simulator/           # Симулятор телеметрии по WebSocket
|   |-- Dockerfile
|-- docs/                    # Архитектурные заметки
|-- frontend/                # Vue дашборд
|   |-- src/                 # UI компоненты и composables
|   |-- Dockerfile
|-- docker-compose.yml
`-- .env.example
```

## Быстрый запуск (Docker)

1. Скопируйте `.env.example` в `.env`.
2. Запустите `docker compose up --build`.

## Запуск через Docker

```bash
# сначала скопируйте .env.example в .env
docker compose up --build
```

## Конфигурация

- Корневой env: `.env.example` содержит `BACKEND_PORT`, `FRONTEND_PORT`, `DB_PATH`, `API_KEY`.
- Frontend env: `frontend/.env.example` содержит `VITE_API_BASE_URL`, `VITE_WS_URL`, `VITE_API_KEY`.
- API key обязателен для REST и WebSocket.

## API

- REST базовый путь: `/api`
- WebSocket ingest: `/ws/telemetry` (прием телеметрии)
- WebSocket stream: `/ws/telemetry/stream` (только подписка)
- Экспорт CSV: `/api/history/export/csv`
- Экспорт PDF: `/api/history/export/pdf`

## Текущее состояние

- FastAPI приложение с REST и WebSocket, авторизация по API key
- Индекс здоровья, топ‑факторы и пайплайн алертов
- SQLite‑хранение с replay, CSV и PDF экспортом
- Vue дашборд с графиками, индексом здоровья, алертами и прогрессом маршрута
- Симулятор, стримящий телеметрию в бэкенд
