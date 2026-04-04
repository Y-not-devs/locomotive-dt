from pathlib import Path

from app.schemas.contracts import TrackMapBuilderRequestDTO, TrackMapSectionInputDTO
from app.services.track_map import TrackMapService


def _build_service() -> TrackMapService:
    return TrackMapService(
        config_path=Path(__file__).resolve().parents[1] / "app" / "config" / "track_map_templates.json"
    )


def test_track_map_layout_contains_locomotive_and_segments() -> None:
    service = _build_service()

    layout = service.build_layout(
        template_id="mainline_demo",
        position_km=12.4,
        current_section=None,
    )

    assert layout.segments
    assert layout.locomotive.segment_id == "north_yard"
    assert layout.current_section == "North-Yard"


def test_track_map_preview_builds_custom_route() -> None:
    service = _build_service()

    preview = service.build_layout_from_sections(
        TrackMapBuilderRequestDTO(
            template_id="custom",
            template_label="Custom",
            position_km=4.0,
            sections=[
                TrackMapSectionInputDTO(
                    id="a",
                    name="Alpha",
                    length_km=5,
                    curve="straight",
                    restricted=False,
                    station_name="Alpha",
                ),
                TrackMapSectionInputDTO(
                    id="b",
                    name="Beta",
                    length_km=7,
                    curve="arc_up",
                    restricted=True,
                    speed_limit_kph=35,
                ),
            ],
        )
    )

    assert len(preview.segments) == 2
    assert preview.restrictions[0].speed_limit_kph == 35
    assert preview.total_distance_km == 12
