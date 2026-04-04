from __future__ import annotations

import json
import math
from pathlib import Path

from app.schemas.contracts import (
    MapPointDTO,
    TrackMapBuilderRequestDTO,
    TrackMapLayoutDTO,
    TrackMapLocomotiveDTO,
    TrackMapRestrictionDTO,
    TrackMapSectionInputDTO,
    TrackMapSegmentDTO,
    TrackMapStationDTO,
    TrackMapTemplateDTO,
)


class TrackMapService:
    def __init__(self, config_path: Path) -> None:
        self._config_path = config_path
        self._templates = self._load_templates()

    def list_templates(self) -> list[TrackMapTemplateDTO]:
        return [
            TrackMapTemplateDTO(
                id=template["id"],
                label=template["label"],
                description=template["description"],
            )
            for template in self._templates
        ]

    def build_layout(
        self,
        *,
        template_id: str | None,
        position_km: float,
        current_section: str | None = None,
    ) -> TrackMapLayoutDTO:
        template = self._get_template(template_id)
        sections = [
            TrackMapSectionInputDTO.model_validate(section)
            for section in template["sections"]
        ]
        return self.build_layout_from_sections(
            TrackMapBuilderRequestDTO(
                template_id=template["id"],
                template_label=template["label"],
                sections=sections,
                position_km=position_km,
                current_section=current_section,
            )
        )

    def build_layout_from_sections(
        self,
        request: TrackMapBuilderRequestDTO,
    ) -> TrackMapLayoutDTO:
        sections = request.sections or [
            TrackMapSectionInputDTO(
                id="fallback",
                name="Fallback",
                length_km=6,
                curve="straight",
                restricted=False,
                station_name="Fallback",
            )
        ]
        cursor_x = 96.0
        base_y = 214.0
        km_cursor = 0.0
        segments: list[TrackMapSegmentDTO] = []
        stations: list[TrackMapStationDTO] = []
        restrictions: list[TrackMapRestrictionDTO] = []
        min_y = base_y
        max_y = base_y

        for index, section in enumerate(sections):
            length_px = max(120.0, section.length_km * 20.0)
            start = MapPointDTO(x=cursor_x, y=base_y)
            end = MapPointDTO(x=cursor_x + length_px, y=base_y + self._curve_offset(section.curve))
            control1, control2 = self._build_controls(start=start, end=end, curve=section.curve)
            path = self._build_path(start=start, end=end, control1=control1, control2=control2)
            segment = TrackMapSegmentDTO(
                id=section.id,
                name=section.name,
                start_km=round(km_cursor, 3),
                end_km=round(km_cursor + section.length_km, 3),
                restricted=section.restricted,
                speed_limit_kph=section.speed_limit_kph,
                curve=section.curve,
                start=start,
                end=end,
                control1=control1,
                control2=control2,
                path=path,
            )
            segments.append(segment)

            if section.station_name:
                station_progress = 0.52
                station_point, station_angle = self._point_on_segment(segment=segment, progress=station_progress)
                stations.append(
                    TrackMapStationDTO(
                        id=f"{section.id}-station",
                        name=section.station_name,
                        km=round(segment.start_km + section.length_km * station_progress, 3),
                        segment_id=segment.id,
                        point=station_point,
                        angle_deg=station_angle,
                    )
                )

            if section.restricted:
                restriction_progress = 0.72
                restriction_point, _ = self._point_on_segment(segment=segment, progress=restriction_progress)
                restrictions.append(
                    TrackMapRestrictionDTO(
                        id=f"{section.id}-restriction",
                        label=f"{section.name} limit",
                        km=round(segment.start_km + section.length_km * restriction_progress, 3),
                        segment_id=segment.id,
                        point=restriction_point,
                        severity="warning",
                        speed_limit_kph=section.speed_limit_kph or 40,
                    )
                )

            cursor_x = end.x + 76.0
            base_y = end.y
            km_cursor = segment.end_km
            min_y = min(min_y, start.y, end.y)
            max_y = max(max_y, start.y, end.y)

            if index == len(sections) - 1:
                cursor_x += 84.0

        total_distance_km = round(km_cursor, 3)
        safe_position = self._normalize_position(position_km=request.position_km, total_distance_km=total_distance_km)
        active_segment = self._locate_segment(segments=segments, position_km=safe_position)
        locomotive_point, heading_deg = self._point_on_segment(
            segment=active_segment,
            progress=self._segment_progress(segment=active_segment, position_km=safe_position),
        )

        return TrackMapLayoutDTO(
            template_id=request.template_id or "custom",
            template_label=request.template_label or "Custom route",
            current_section=request.current_section or active_segment.name,
            viewport_width=max(960, int(cursor_x)),
            viewport_height=max(360, int(max_y - min_y + 180)),
            total_distance_km=total_distance_km,
            templates=self.list_templates(),
            segments=segments,
            stations=stations,
            restrictions=restrictions,
            locomotive=TrackMapLocomotiveDTO(
                segment_id=active_segment.id,
                progress=round(self._segment_progress(segment=active_segment, position_km=safe_position), 3),
                position_km=safe_position,
                heading_deg=heading_deg,
                point=locomotive_point,
            ),
        )

    def _load_templates(self) -> list[dict[str, object]]:
        payload = json.loads(self._config_path.read_text(encoding="utf-8"))
        templates = payload.get("templates", [])
        if not isinstance(templates, list) or not templates:
            msg = "Track map templates config must contain a non-empty 'templates' list."
            raise ValueError(msg)
        return templates

    def _get_template(self, template_id: str | None) -> dict[str, object]:
        if template_id:
            for template in self._templates:
                if template["id"] == template_id:
                    return template
        return self._templates[0]

    @staticmethod
    def _curve_offset(curve: str) -> float:
        if curve == "arc_up":
            return -96.0
        if curve == "arc_down":
            return 96.0
        return 0.0

    @staticmethod
    def _build_controls(
        *,
        start: MapPointDTO,
        end: MapPointDTO,
        curve: str,
    ) -> tuple[MapPointDTO | None, MapPointDTO | None]:
        if curve == "straight":
            return None, None

        span_x = end.x - start.x
        control1 = MapPointDTO(x=start.x + span_x * 0.28, y=start.y)
        control2 = MapPointDTO(x=start.x + span_x * 0.72, y=end.y)
        return control1, control2

    @staticmethod
    def _build_path(
        *,
        start: MapPointDTO,
        end: MapPointDTO,
        control1: MapPointDTO | None,
        control2: MapPointDTO | None,
    ) -> str:
        if control1 is None or control2 is None:
            return f"M {start.x:.1f} {start.y:.1f} L {end.x:.1f} {end.y:.1f}"
        return (
            f"M {start.x:.1f} {start.y:.1f} "
            f"C {control1.x:.1f} {control1.y:.1f}, {control2.x:.1f} {control2.y:.1f}, {end.x:.1f} {end.y:.1f}"
        )

    @staticmethod
    def _normalize_position(*, position_km: float, total_distance_km: float) -> float:
        if total_distance_km <= 0:
            return 0.0
        if position_km < 0:
            return 0.0
        if position_km <= total_distance_km:
            return round(position_km, 3)
        return round(position_km % total_distance_km, 3)

    @staticmethod
    def _locate_segment(*, segments: list[TrackMapSegmentDTO], position_km: float) -> TrackMapSegmentDTO:
        for segment in segments:
            if segment.start_km <= position_km <= segment.end_km:
                return segment
        return segments[-1]

    @staticmethod
    def _segment_progress(*, segment: TrackMapSegmentDTO, position_km: float) -> float:
        span = max(segment.end_km - segment.start_km, 1e-6)
        return min(1.0, max(0.0, (position_km - segment.start_km) / span))

    def _point_on_segment(
        self,
        *,
        segment: TrackMapSegmentDTO,
        progress: float,
    ) -> tuple[MapPointDTO, float]:
        t = min(1.0, max(0.0, progress))
        if segment.control1 is None or segment.control2 is None:
            x = segment.start.x + (segment.end.x - segment.start.x) * t
            y = segment.start.y + (segment.end.y - segment.start.y) * t
            heading = math.degrees(math.atan2(segment.end.y - segment.start.y, segment.end.x - segment.start.x))
            return MapPointDTO(x=round(x, 2), y=round(y, 2)), round(heading, 2)

        p0 = segment.start
        p1 = segment.control1
        p2 = segment.control2
        p3 = segment.end

        x = (
            (1 - t) ** 3 * p0.x
            + 3 * (1 - t) ** 2 * t * p1.x
            + 3 * (1 - t) * t**2 * p2.x
            + t**3 * p3.x
        )
        y = (
            (1 - t) ** 3 * p0.y
            + 3 * (1 - t) ** 2 * t * p1.y
            + 3 * (1 - t) * t**2 * p2.y
            + t**3 * p3.y
        )
        dx = (
            3 * (1 - t) ** 2 * (p1.x - p0.x)
            + 6 * (1 - t) * t * (p2.x - p1.x)
            + 3 * t**2 * (p3.x - p2.x)
        )
        dy = (
            3 * (1 - t) ** 2 * (p1.y - p0.y)
            + 6 * (1 - t) * t * (p2.y - p1.y)
            + 3 * t**2 * (p3.y - p2.y)
        )
        heading = math.degrees(math.atan2(dy, dx))
        return MapPointDTO(x=round(x, 2), y=round(y, 2)), round(heading, 2)
