import asyncio

from ..db.repository import TelemetryRepository
from ..models.schemas import TelemetryOut


class IngestBuffer:
    def __init__(
        self,
        repository: TelemetryRepository,
        batch_size: int = 100,
        flush_interval: float = 1.0,
    ) -> None:
        self._repository = repository
        self._batch_size = batch_size
        self._flush_interval = flush_interval
        self._queue: asyncio.Queue[TelemetryOut] = asyncio.Queue()
        self._task: asyncio.Task | None = None
        self._stopped = asyncio.Event()

    async def start(self) -> None:
        if self._task:
            return
        self._stopped.clear()
        self._task = asyncio.create_task(self._run())

    async def stop(self) -> None:
        if not self._task:
            return
        self._stopped.set()
        await self._task
        self._task = None

    async def enqueue(self, payload: TelemetryOut) -> None:
        await self._queue.put(payload)

    async def _run(self) -> None:
        buffer: list[TelemetryOut] = []
        while not self._stopped.is_set() or not self._queue.empty():
            try:
                item = await asyncio.wait_for(
                    self._queue.get(), timeout=self._flush_interval
                )
                buffer.append(item)
                if len(buffer) >= self._batch_size:
                    await self._flush(buffer)
                    buffer.clear()
            except asyncio.TimeoutError:
                if buffer:
                    await self._flush(buffer)
                    buffer.clear()

        if buffer:
            await self._flush(buffer)

    async def _flush(self, items: list[TelemetryOut]) -> None:
        await asyncio.to_thread(self._repository.save_many, items)


ingest_buffer = IngestBuffer(TelemetryRepository())
