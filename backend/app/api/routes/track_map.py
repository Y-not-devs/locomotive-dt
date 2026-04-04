from fastapi import APIRouter, Depends, Query

from app.dependencies import get_repository, get_track_map_service
from app.repositories.telemetry import InMemoryTelemetryRepository
from app.schemas.contracts import TrackMapBuilderRequestDTO, TrackMapLayoutDTO, TrackMapTemplateDTO
from app.services.track_map import TrackMapService

router = APIRouter(prefix="/track-map")


@router.get("/templates", response_model=list[TrackMapTemplateDTO])
async def list_track_map_templates(
    track_map_service: TrackMapService = Depends(get_track_map_service),
) -> list[TrackMapTemplateDTO]:
    return track_map_service.list_templates()


@router.get("/layout", response_model=TrackMapLayoutDTO)
async def get_track_map_layout(
    locomotive_id: str = Query(..., description="Locomotive identifier"),
    template_id: str | None = Query(default=None, description="Track map template id"),
    position_km: float | None = Query(default=None, ge=0.0),
    track_map_service: TrackMapService = Depends(get_track_map_service),
    repository: InMemoryTelemetryRepository = Depends(get_repository),
) -> TrackMapLayoutDTO:
    latest = await repository.latest_for_locomotive(locomotive_id=locomotive_id)
    effective_position = position_km
    current_section = None

    if latest is not None:
        if template_id is None:
            current_section = latest.telemetry.route_section
        if effective_position is None:
            effective_position = latest.telemetry.position_km

    return track_map_service.build_layout(
        template_id=template_id,
        position_km=effective_position or 0.0,
        current_section=current_section,
    )


@router.post("/preview", response_model=TrackMapLayoutDTO)
async def preview_track_map_layout(
    payload: TrackMapBuilderRequestDTO,
    track_map_service: TrackMapService = Depends(get_track_map_service),
) -> TrackMapLayoutDTO:
    return track_map_service.build_layout_from_sections(payload)
