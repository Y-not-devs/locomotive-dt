from fastapi import APIRouter, Depends, Query

from app.dependencies import get_repository
from app.repositories.telemetry import InMemoryTelemetryRepository
from app.schemas.contracts import AlertDTO, LiveTelemetryEnvelopeDTO, ReplayWindowDTO

router = APIRouter()


@router.get("/telemetry/recent", response_model=list[LiveTelemetryEnvelopeDTO])
async def get_recent_telemetry(
    locomotive_id: str = Query(..., description="Locomotive identifier"),
    limit: int = Query(60, ge=1, le=600),
    repository: InMemoryTelemetryRepository = Depends(get_repository),
) -> list[LiveTelemetryEnvelopeDTO]:
    return await repository.list_recent(locomotive_id=locomotive_id, limit=limit)


@router.get("/telemetry/replay", response_model=ReplayWindowDTO)
async def get_replay_window(
    locomotive_id: str = Query(..., description="Locomotive identifier"),
    seconds: int = Query(300, ge=60, le=3600),
    repository: InMemoryTelemetryRepository = Depends(get_repository),
) -> ReplayWindowDTO:
    items = await repository.replay_window(locomotive_id=locomotive_id, seconds=seconds)
    return ReplayWindowDTO(locomotive_id=locomotive_id, seconds=seconds, items=items)


@router.get("/alerts/active", response_model=list[AlertDTO])
async def get_active_alerts(
    locomotive_id: str = Query(..., description="Locomotive identifier"),
    repository: InMemoryTelemetryRepository = Depends(get_repository),
) -> list[AlertDTO]:
    return await repository.list_active_alerts(locomotive_id=locomotive_id)
