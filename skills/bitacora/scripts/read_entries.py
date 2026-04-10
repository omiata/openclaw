#!/usr/bin/env python3
from __future__ import annotations

import argparse
from collections import Counter
import difflib
import json
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from save_entry import (
    DEFAULT_DATA_DIR,
    ENTRY_DELIMITER,
    ascii_fold,
    entry_from_block,
    format_visible_date,
    humanize_category_name,
    humanize_project_name,
    humanize_resource_type,
    humanize_state_label,
    humanize_summary_quality_label,
    normalize_name,
    normalize_state,
    normalize_summary_quality,
)

REMINDER_CRON_EXPRESSION = "0 20 * * *"
REMINDER_TIMEZONE = "Europe/Madrid"

REQUIRED_FIELDS = (
    "id",
    "fecha",
    "proyecto",
    "categoria",
    "tipo",
    "titulo",
    "resumen",
    "calidad_resumen",
    "estado",
)
SEARCHABLE_FIELDS = ("titulo", "resumen", "tags", "contenido_adicional")
HUMAN_FIELD_LABELS = {
    "titulo": "el título",
    "resumen": "el resumen",
    "tags": "los tags",
    "contenido_adicional": "la nota personal",
}


@dataclass
class ParseWarning:
    position: int
    message: str
    entry_id: Optional[str] = None


@dataclass
class StoredEntry:
    entry_id: str
    fecha: str
    proyecto: str
    categoria: str
    tipo: str
    titulo: str
    resumen: str
    contenido: str
    source_path: Path
    position: int
    fuente: Optional[str] = None
    tags: list[str] = field(default_factory=list)
    contenido_adicional: Optional[str] = None
    calidad_resumen: str = "fallback"
    estado: str = "nuevo"
    fecha_actualizacion: Optional[str] = None


@dataclass
class ListingResult:
    project: str
    file_path: Path
    total_entries: int
    matched_entries: list[StoredEntry]
    warnings: list[ParseWarning]
    requested_category: Optional[str] = None
    normalized_category: Optional[str] = None
    requested_state: Optional[str] = None
    normalized_state: Optional[str] = None
    suggested_categories: list[str] = field(default_factory=list)


@dataclass
class OperationalViewResult:
    project: str
    file_path: Path
    total_entries: int
    matched_entries: list[StoredEntry]
    warnings: list[ParseWarning]
    view_name: str


@dataclass
class SearchMatch:
    field_name: str
    context: str


@dataclass
class SearchHit:
    entry: StoredEntry
    matches: list[SearchMatch]


@dataclass
class SearchResult:
    project: str
    file_path: Path
    total_entries: int
    query: str
    matched_hits: list[SearchHit]
    warnings: list[ParseWarning]


@dataclass
class CategoryIndexItem:
    categoria: str
    total_entries: int
    latest_update: Optional[str]


@dataclass
class TypeIndexItem:
    tipo: str
    total_entries: int


@dataclass
class ProjectOverviewResult:
    project: str
    file_path: Path
    total_entries: int
    category_index: list[CategoryIndexItem]
    type_index: list[TypeIndexItem]
    latest_update: Optional[str]
    warnings: list[ParseWarning]


@dataclass
class GlobalProjectSummary:
    project: str
    total_entries: int
    category_count: int
    type_count: int
    latest_update: Optional[str]


@dataclass
class GlobalWarningGroup:
    project: str
    warnings: list[ParseWarning]


@dataclass
class GlobalStatsResult:
    total_entries: int
    total_projects: int
    projects: list[GlobalProjectSummary]
    top_categories: list[CategoryIndexItem]
    type_index: list[TypeIndexItem]
    warning_groups: list[GlobalWarningGroup]


@dataclass
class EntryLookupResult:
    project: str
    file_path: Path
    total_entries: int
    requested_entry_id: str
    entry: Optional[StoredEntry]
    warnings: list[ParseWarning]


@dataclass
class PaginationWindow:
    total: int
    offset: int
    limit: int
    start_index: int
    end_index: int
    visible_count: int
    has_previous: bool
    has_more: bool
    visible_items: list


def paginate_items(items: list, offset: int, limit: int) -> PaginationWindow:
    safe_limit = max(limit, 1)
    safe_offset = max(offset, 0)
    total = len(items)
    start_index = min(safe_offset, total)
    end_index = min(start_index + safe_limit, total)
    visible_items = items[start_index:end_index]
    return PaginationWindow(
        total=total,
        offset=safe_offset,
        limit=safe_limit,
        start_index=start_index,
        end_index=end_index,
        visible_count=len(visible_items),
        has_previous=start_index > 0,
        has_more=end_index < total,
        visible_items=visible_items,
    )


def build_pagination_label(window: PaginationWindow, *, noun: str = "resultados") -> str:
    if window.total == 0:
        return f"0 {noun}"
    if window.visible_count == 0:
        return f"sin más {noun}"
    return f"{window.start_index + 1} a {window.end_index} de {window.total} {noun}"


def build_next_page_hint(window: PaginationWindow, *, technical: bool = True) -> Optional[str]:
    if not window.has_more:
        return None
    next_offset = window.end_index
    next_position = next_offset + 1
    if technical:
        return f"Siguiente página disponible con --offset {next_offset}."
    return f"Si quieres, pide 'más' o 'siguiente página' y te enseño desde la entrada {next_position}."


def build_end_of_results_hint(window: PaginationWindow, *, technical: bool = True) -> Optional[str]:
    if window.total == 0 or window.offset < window.total:
        return None
    if technical:
        return f"No hay más resultados. El último tramo disponible llega hasta {window.total}."
    return "No hay más resultados. Ya has llegado al final."


def extract_entry_id(raw_block: str) -> Optional[str]:
    match = re.search(r'^id:\s+"?([^"\n]+)"?$', raw_block, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return None


def split_entry_blocks(content: str) -> list[tuple[int, str]]:
    blocks: list[tuple[int, str]] = []
    for raw_block in content.split(ENTRY_DELIMITER):
        block = raw_block.strip()
        if not block:
            continue
        blocks.append((len(blocks) + 1, block))
    return blocks


def parse_entry_block(block: str, position: int, source_path: Path) -> StoredEntry:
    entry = entry_from_block(block)

    missing_fields = [
        field
        for field in REQUIRED_FIELDS
        if getattr(entry, "entry_id" if field == "id" else field, None) in (None, "")
    ]
    if missing_fields:
        raise ValueError(f"Faltan campos obligatorios: {', '.join(missing_fields)}")

    return StoredEntry(
        entry_id=entry.entry_id,
        fecha=entry.fecha,
        proyecto=entry.proyecto,
        categoria=entry.categoria,
        tipo=entry.tipo,
        titulo=entry.titulo,
        resumen=entry.resumen,
        contenido=entry.contenido,
        source_path=source_path,
        position=position,
        fuente=entry.fuente,
        tags=list(entry.tags),
        contenido_adicional=entry.contenido_adicional,
        calidad_resumen=entry.calidad_resumen,
        estado=entry.estado,
        fecha_actualizacion=entry.fecha_actualizacion,
    )


def load_entries(project: str, data_dir: Path = DEFAULT_DATA_DIR) -> tuple[list[StoredEntry], list[ParseWarning], Path]:
    normalized_project = normalize_name(project)
    file_path = data_dir / f"{normalized_project}.md"
    if not file_path.exists():
        return [], [], file_path

    try:
        content = file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        warning = ParseWarning(position=0, message=f"Archivo no legible como UTF-8: {exc}")
        return [], [warning], file_path

    entries: list[StoredEntry] = []
    warnings: list[ParseWarning] = []
    for position, block in split_entry_blocks(content):
        try:
            entries.append(parse_entry_block(block, position=position, source_path=file_path))
        except Exception as exc:
            warnings.append(
                ParseWarning(
                    position=position,
                    entry_id=extract_entry_id(block),
                    message=str(exc),
                )
            )

    return sort_entries(entries), warnings, file_path


def parse_entry_datetime(fecha: str) -> datetime:
    try:
        return datetime.fromisoformat(fecha.replace("Z", "+00:00"))
    except ValueError:
        return datetime.min.replace(tzinfo=timezone.utc)


def sort_entries(entries: list[StoredEntry]) -> list[StoredEntry]:
    return sorted(entries, key=lambda entry: parse_entry_datetime(entry.fecha), reverse=True)


def build_category_index(entries: list[StoredEntry]) -> list[CategoryIndexItem]:
    counters: Counter[str] = Counter()
    latest_by_category: dict[str, str] = {}

    for entry in entries:
        counters[entry.categoria] += 1
        if entry.categoria not in latest_by_category:
            latest_by_category[entry.categoria] = entry.fecha

    return sorted(
        [
            CategoryIndexItem(
                categoria=category,
                total_entries=total,
                latest_update=latest_by_category.get(category),
            )
            for category, total in counters.items()
        ],
        key=lambda item: (-item.total_entries, item.categoria),
    )


def build_type_index(entries: list[StoredEntry]) -> list[TypeIndexItem]:
    counters: Counter[str] = Counter(entry.tipo for entry in entries)
    return sorted(
        [TypeIndexItem(tipo=resource_type, total_entries=total) for resource_type, total in counters.items()],
        key=lambda item: (-item.total_entries, item.tipo),
    )


def build_project_overview(project: str, data_dir: Path = DEFAULT_DATA_DIR) -> ProjectOverviewResult:
    entries, warnings, file_path = load_entries(project=project, data_dir=data_dir)
    category_index = build_category_index(entries)
    type_index = build_type_index(entries)
    latest_update = entries[0].fecha if entries else None
    return ProjectOverviewResult(
        project=normalize_name(project),
        file_path=file_path,
        total_entries=len(entries),
        category_index=category_index,
        type_index=type_index,
        latest_update=latest_update,
        warnings=warnings,
    )


def build_global_stats(data_dir: Path = DEFAULT_DATA_DIR) -> GlobalStatsResult:
    project_files = sorted(path for path in data_dir.glob("*.md") if path.is_file())
    project_summaries: list[GlobalProjectSummary] = []
    warning_groups: list[GlobalWarningGroup] = []
    all_entries: list[StoredEntry] = []

    for file_path in project_files:
        project = file_path.stem
        entries, warnings, _ = load_entries(project=project, data_dir=data_dir)
        all_entries.extend(entries)
        category_index = build_category_index(entries)
        type_index = build_type_index(entries)
        latest_update = entries[0].fecha if entries else None
        project_summaries.append(
            GlobalProjectSummary(
                project=project,
                total_entries=len(entries),
                category_count=len(category_index),
                type_count=len(type_index),
                latest_update=latest_update,
            )
        )
        if warnings:
            warning_groups.append(GlobalWarningGroup(project=project, warnings=warnings))

    project_summaries.sort(key=lambda item: (-item.total_entries, item.project))
    return GlobalStatsResult(
        total_entries=len(all_entries),
        total_projects=len(project_summaries),
        projects=project_summaries,
        top_categories=build_category_index(all_entries),
        type_index=build_type_index(all_entries),
        warning_groups=warning_groups,
    )


def filter_entries_by_category(entries: list[StoredEntry], category: str) -> tuple[str, list[StoredEntry]]:
    normalized_category = normalize_name(category)
    matched = [entry for entry in entries if normalize_name(entry.categoria) == normalized_category]
    return normalized_category, matched


def filter_entries_by_state(entries: list[StoredEntry], state: str) -> tuple[str, list[StoredEntry]]:
    normalized_state = normalize_state(state)
    matched = [entry for entry in entries if normalize_state(entry.estado) == normalized_state]
    return normalized_state, matched


def filter_entries_by_summary_quality(entries: list[StoredEntry], quality: str) -> tuple[str, list[StoredEntry]]:
    normalized_quality = normalize_summary_quality(quality)
    matched = [entry for entry in entries if normalize_summary_quality(entry.calidad_resumen) == normalized_quality]
    return normalized_quality, matched


def normalize_search_text(value: str) -> str:
    return " ".join(ascii_fold(value).lower().split())


def build_search_context(value: str, query: str, radius: int = 45) -> str:
    compact_original = " ".join(value.split())
    if not compact_original:
        return ""

    compact_normalized = normalize_search_text(compact_original)
    if not compact_normalized:
        return compact_original[: radius * 2]

    index = compact_normalized.find(query)
    if index < 0:
        return compact_original[: radius * 2]

    start = max(index - radius, 0)
    end = min(index + len(query) + radius, len(compact_original))
    snippet = compact_original[start:end].strip()
    if start > 0:
        snippet = f"...{snippet}"
    if end < len(compact_original):
        snippet = f"{snippet}..."
    return snippet


def find_entry_matches(entry: StoredEntry, query: str) -> list[SearchMatch]:
    matches: list[SearchMatch] = []
    field_values = {
        "titulo": entry.titulo,
        "resumen": entry.resumen,
        "tags": ", ".join(entry.tags),
        "contenido_adicional": entry.contenido_adicional or "",
    }

    for field_name in SEARCHABLE_FIELDS:
        raw_value = field_values[field_name]
        normalized_value = normalize_search_text(raw_value)
        if raw_value and query in normalized_value:
            matches.append(
                SearchMatch(
                    field_name=field_name,
                    context=build_search_context(raw_value, query),
                )
            )
    return matches


def suggest_categories(entries: list[StoredEntry], category: str, limit: int = 3) -> list[str]:
    available = sorted({entry.categoria for entry in entries})
    normalized_map = {normalize_name(candidate): candidate for candidate in available}
    matches = difflib.get_close_matches(normalize_name(category), list(normalized_map.keys()), n=limit, cutoff=0.6)
    return [normalized_map[match] for match in matches]


def list_entries(
    project: str,
    data_dir: Path = DEFAULT_DATA_DIR,
    category: Optional[str] = None,
    state: Optional[str] = None,
) -> ListingResult:
    entries, warnings, file_path = load_entries(project=project, data_dir=data_dir)
    matched_entries = entries
    normalized_category: Optional[str] = None
    normalized_state: Optional[str] = None
    suggestions: list[str] = []

    if category is not None:
        normalized_category, matched_entries = filter_entries_by_category(matched_entries, category)
        suggestions = suggest_categories(entries, category) if not matched_entries else []

    if state is not None:
        normalized_state, matched_entries = filter_entries_by_state(matched_entries, state)

    if category is None and state is None:
        return ListingResult(
            project=normalize_name(project),
            file_path=file_path,
            total_entries=len(entries),
            matched_entries=entries,
            warnings=warnings,
        )

    return ListingResult(
        project=normalize_name(project),
        file_path=file_path,
        total_entries=len(entries),
        matched_entries=matched_entries,
        warnings=warnings,
        requested_category=category,
        normalized_category=normalized_category,
        requested_state=state,
        normalized_state=normalized_state,
        suggested_categories=suggestions,
    )


def list_recent_entries(project: str, data_dir: Path = DEFAULT_DATA_DIR, limit: int = 5) -> OperationalViewResult:
    entries, warnings, file_path = load_entries(project=project, data_dir=data_dir)
    return OperationalViewResult(
        project=normalize_name(project),
        file_path=file_path,
        total_entries=len(entries),
        matched_entries=entries[: max(limit, 0)],
        warnings=warnings,
        view_name="recent",
    )


def list_entries_by_summary_quality(
    project: str,
    quality: str,
    data_dir: Path = DEFAULT_DATA_DIR,
) -> OperationalViewResult:
    entries, warnings, file_path = load_entries(project=project, data_dir=data_dir)
    normalized_quality, matched_entries = filter_entries_by_summary_quality(entries, quality)
    return OperationalViewResult(
        project=normalize_name(project),
        file_path=file_path,
        total_entries=len(entries),
        matched_entries=matched_entries,
        warnings=warnings,
        view_name=f"summary_quality:{normalized_quality}",
    )


def list_pending_enrichment_entries(project: str, data_dir: Path = DEFAULT_DATA_DIR) -> OperationalViewResult:
    entries, warnings, file_path = load_entries(project=project, data_dir=data_dir)
    matched_entries = [
        entry
        for entry in entries
        if normalize_summary_quality(entry.calidad_resumen) == "fallback" and normalize_state(entry.estado) != "descartado"
    ]
    return OperationalViewResult(
        project=normalize_name(project),
        file_path=file_path,
        total_entries=len(entries),
        matched_entries=matched_entries,
        warnings=warnings,
        view_name="pending_enrichment",
    )


def search_entries(project: str, query: str, data_dir: Path = DEFAULT_DATA_DIR) -> SearchResult:
    normalized_query = normalize_search_text(query)
    if not normalized_query:
        raise ValueError("La búsqueda no puede quedar vacía")

    entries, warnings, file_path = load_entries(project=project, data_dir=data_dir)
    matched_hits: list[SearchHit] = []
    for entry in entries:
        matches = find_entry_matches(entry, normalized_query)
        if matches:
            matched_hits.append(SearchHit(entry=entry, matches=matches))

    return SearchResult(
        project=normalize_name(project),
        file_path=file_path,
        total_entries=len(entries),
        query=query.strip(),
        matched_hits=matched_hits,
        warnings=warnings,
    )


def get_entry_by_id(project: str, entry_id: str, data_dir: Path = DEFAULT_DATA_DIR) -> EntryLookupResult:
    normalized_entry_id = entry_id.strip()
    if not normalized_entry_id:
        raise ValueError("El id de entrada no puede quedar vacío")

    entries, warnings, file_path = load_entries(project=project, data_dir=data_dir)
    entry = next((candidate for candidate in entries if candidate.entry_id == normalized_entry_id), None)
    return EntryLookupResult(
        project=normalize_name(project),
        file_path=file_path,
        total_entries=len(entries),
        requested_entry_id=normalized_entry_id,
        entry=entry,
        warnings=warnings,
    )


def format_entry_summary(entry: StoredEntry) -> str:
    lines = [
        f"- {entry.titulo}",
        f"  id: {entry.entry_id}",
        f"  categoría: {entry.categoria} | tipo: {entry.tipo} | fecha: {entry.fecha}",
        f"  estado: {entry.estado} | calidad_resumen: {entry.calidad_resumen}",
        f"  resumen: {entry.resumen}",
    ]
    if entry.fuente:
        lines.append(f"  fuente: {entry.fuente}")
    if entry.tags:
        lines.append(f"  tags: {', '.join(entry.tags)}")
    return "\n".join(lines)


def format_entry_summary_human(entry: StoredEntry) -> str:
    lines = [f"- {entry.titulo}"]
    meta = " · ".join(
        (
            humanize_category_name(entry.categoria),
            humanize_resource_type(entry.tipo),
            format_visible_date(entry.fecha),
        )
    )
    lines.append(f"  {meta}")
    lines.append(f"  {entry.resumen}")
    if entry.calidad_resumen == "fallback":
        lines.append(f"  {humanize_summary_quality_label(entry.calidad_resumen)}")
    if entry.tags:
        lines.append(f"  Tags: {', '.join(entry.tags)}")
    return "\n".join(lines)


def format_search_hit(hit: SearchHit) -> str:
    lines = [
        f"- {hit.entry.titulo}",
        f"  id: {hit.entry.entry_id}",
        f"  categoría: {hit.entry.categoria} | tipo: {hit.entry.tipo} | fecha: {hit.entry.fecha}",
    ]
    for match in hit.matches:
        lines.append(f"  coincidencia en {match.field_name}: {match.context}")
    return "\n".join(lines)


def format_search_hit_human(hit: SearchHit) -> str:
    lines = [f"- {hit.entry.titulo}"]
    meta = " · ".join(
        (
            humanize_category_name(hit.entry.categoria),
            humanize_resource_type(hit.entry.tipo),
            format_visible_date(hit.entry.fecha),
        )
    )
    lines.append(f"  {meta}")
    for match in hit.matches:
        field_label = HUMAN_FIELD_LABELS.get(match.field_name, match.field_name)
        lines.append(f"  Aparece en {field_label}: {match.context}")
    return "\n".join(lines)


def format_entry_full(entry: StoredEntry) -> str:
    lines = [
        f"ID: {entry.entry_id}",
        f"Proyecto: {entry.proyecto}",
        f"Categoría: {entry.categoria}",
        f"Tipo: {entry.tipo}",
        f"Fecha: {entry.fecha}",
        f"Estado: {entry.estado}",
        f"Calidad resumen: {entry.calidad_resumen}",
        f"Título: {entry.titulo}",
        f"Resumen: {entry.resumen}",
    ]
    if entry.fecha_actualizacion:
        lines.append(f"Fecha actualización: {entry.fecha_actualizacion}")
    if entry.fuente:
        lines.append(f"Fuente: {entry.fuente}")
    if entry.tags:
        lines.append(f"Tags: {', '.join(entry.tags)}")
    if entry.contenido_adicional:
        lines.append("Nota personal:")
        lines.append(entry.contenido_adicional)
    return "\n".join(lines)


def format_entry_full_human(entry: StoredEntry) -> str:
    lines = [entry.titulo]
    lines.append(
        " · ".join(
            (
                humanize_project_name(entry.proyecto),
                humanize_category_name(entry.categoria),
                humanize_resource_type(entry.tipo),
                format_visible_date(entry.fecha),
            )
        )
    )
    lines.append(f"Estado: {humanize_state_label(entry.estado)}")
    lines.append(f"Resumen: {entry.resumen}")
    if entry.fecha_actualizacion:
        lines.append(f"Última edición: {format_visible_date(entry.fecha_actualizacion)}")
    if entry.fuente:
        lines.append(f"Fuente: {entry.fuente}")
    if entry.tags:
        lines.append(f"Tags: {', '.join(entry.tags)}")
    if entry.contenido_adicional:
        lines.append("Nota personal:")
        lines.append(entry.contenido_adicional)
    return "\n".join(lines)


def format_warning(warning: ParseWarning) -> str:
    location = f"id {warning.entry_id}" if warning.entry_id else f"posición {warning.position}"
    return f"- {location}: {warning.message}"


def build_overview_sections(overview: ProjectOverviewResult) -> list[str]:
    lines: list[str] = []

    lines.append("Índice de categorías:")
    if overview.category_index:
        for item in overview.category_index:
            latest = item.latest_update or "sin fecha válida"
            lines.append(
                f"- {item.categoria}: {item.total_entries} entradas | última actualización: {latest}"
            )
    else:
        lines.append("- Sin entradas válidas para indexar categorías.")

    lines.append("Índice de tipos:")
    if overview.type_index:
        for item in overview.type_index:
            lines.append(f"- {item.tipo}: {item.total_entries} entradas")
    else:
        lines.append("- Sin entradas válidas para indexar tipos.")

    lines.append("Estadísticas:")
    lines.append(f"- total entradas: {overview.total_entries}")
    lines.append(f"- categorías distintas: {len(overview.category_index)}")
    lines.append(f"- tipos presentes: {len(overview.type_index)}")
    lines.append(f"- última actualización: {overview.latest_update or 'sin fecha válida'}")
    if overview.category_index:
        top_categories = ", ".join(
            f"{item.categoria} ({item.total_entries})" for item in overview.category_index[:5]
        )
        lines.append(f"- categorías más usadas: {top_categories}")
    else:
        lines.append("- categorías más usadas: ninguna")

    return lines


def build_global_stats_output(result: GlobalStatsResult) -> str:
    return build_global_stats_output_technical(result)


def build_global_stats_output_technical(result: GlobalStatsResult) -> str:
    lines = [
        f"Estadísticas globales: {result.total_entries} entradas válidas en {result.total_projects} proyectos."
    ]

    if result.projects:
        for project in result.projects:
            latest = project.latest_update or "sin fecha válida"
            lines.append(
                f"- {project.project}: {project.total_entries} entradas | "
                f"{project.category_count} categorías | {project.type_count} tipos | "
                f"última actualización: {latest}"
            )
    else:
        lines.append("No hay proyectos para mostrar.")

    lines.append("Categorías más usadas:")
    if result.top_categories:
        for item in result.top_categories[:10]:
            lines.append(f"- {item.categoria}: {item.total_entries} entradas")
    else:
        lines.append("- Sin categorías válidas.")

    lines.append("Tipos presentes:")
    if result.type_index:
        for item in result.type_index:
            lines.append(f"- {item.tipo}: {item.total_entries} entradas")
    else:
        lines.append("- Sin tipos válidos.")

    if result.warning_groups:
        total_warnings = sum(len(group.warnings) for group in result.warning_groups)
        lines.append(f"Avisos de lectura globales: {total_warnings}")
        for group in result.warning_groups:
            for warning in group.warnings:
                lines.append(f"- {group.project} / {format_warning(warning)[2:]}")

    return "\n".join(lines)


def build_global_stats_output_human(result: GlobalStatsResult) -> str:
    lines = [
        f"Resumen global: {result.total_entries} entradas válidas en {result.total_projects} proyectos."
    ]

    if result.projects:
        for project in result.projects:
            latest = format_visible_date(project.latest_update) if project.latest_update else "sin fecha legible"
            lines.append(
                f"- {humanize_project_name(project.project)}: {project.total_entries} entradas, "
                f"{project.category_count} categorías, {project.type_count} tipos, última actualización {latest}"
            )
    else:
        lines.append("No hay proyectos para mostrar.")

    if result.top_categories:
        lines.append("Categorías más usadas:")
        for item in result.top_categories[:10]:
            lines.append(f"- {humanize_category_name(item.categoria)}: {item.total_entries}")

    if result.type_index:
        lines.append("Tipos presentes:")
        for item in result.type_index:
            lines.append(f"- {humanize_resource_type(item.tipo)}: {item.total_entries}")

    if result.warning_groups:
        total_warnings = sum(len(group.warnings) for group in result.warning_groups)
        lines.append(f"Avisos de lectura: {total_warnings}")
        for group in result.warning_groups:
            for warning in group.warnings:
                lines.append(f"- {humanize_project_name(group.project)} / {format_warning(warning)[2:]}")

    return "\n".join(lines)


def build_output(
    result: ListingResult,
    max_entries: int = 20,
    overview: Optional[ProjectOverviewResult] = None,
    *,
    technical: bool = True,
    offset: int = 0,
) -> str:
    if technical:
        return build_output_technical(result, max_entries=max_entries, overview=overview, offset=offset)
    return build_output_human(result, max_entries=max_entries, overview=overview, offset=offset)


def build_output_technical(
    result: ListingResult,
    max_entries: int = 20,
    overview: Optional[ProjectOverviewResult] = None,
    offset: int = 0,
) -> str:
    if result.requested_category is None and result.requested_state is None:
        header = f"Proyecto {result.project}: {result.total_entries} entradas válidas."
    elif result.requested_category is not None and result.requested_state is None:
        header = (
            f"Proyecto {result.project}, categoría {result.normalized_category}: "
            f"{len(result.matched_entries)} entradas de {result.total_entries} válidas."
        )
    elif result.requested_category is None and result.requested_state is not None:
        header = (
            f"Proyecto {result.project}, estado {result.normalized_state}: "
            f"{len(result.matched_entries)} entradas de {result.total_entries} válidas."
        )
    else:
        header = (
            f"Proyecto {result.project}, categoría {result.normalized_category}, estado {result.normalized_state}: "
            f"{len(result.matched_entries)} entradas de {result.total_entries} válidas."
        )

    lines = [header]
    page = paginate_items(result.matched_entries, offset, max_entries)

    if result.matched_entries and page.visible_items:
        if len(result.matched_entries) > max_entries or offset > 0:
            lines.append(f"Mostrando entradas {build_pagination_label(page, noun='entradas')}.")
        for entry in page.visible_items:
            lines.append(format_entry_summary(entry))
    else:
        lines.append("No hay entradas para mostrar.")
        if result.requested_category is not None and result.suggested_categories:
            lines.append(
                "Aviso de categoría ambigua o no encontrada. "
                f"Quizá quisiste decir: {', '.join(result.suggested_categories)}."
            )

    end_hint = build_end_of_results_hint(page, technical=True)
    if end_hint:
        lines.append(end_hint)
    next_hint = build_next_page_hint(page, technical=True)
    if next_hint:
        lines.append(next_hint)

    if result.warnings:
        lines.append(f"Avisos de lectura: {len(result.warnings)}")
        lines.extend(format_warning(warning) for warning in result.warnings)

    if overview is not None:
        lines.extend(build_overview_sections(overview))

    return "\n".join(lines)


def build_output_human(
    result: ListingResult,
    max_entries: int = 20,
    overview: Optional[ProjectOverviewResult] = None,
    offset: int = 0,
) -> str:
    project_label = humanize_project_name(result.project)
    if result.requested_category is None and result.requested_state is None:
        header = f"{project_label}: {result.total_entries} entradas." if result.total_entries != 1 else f"{project_label}: 1 entrada."
    elif result.requested_category is not None and result.requested_state is None:
        requested = humanize_category_name(result.normalized_category or normalize_name(result.requested_category))
        total = len(result.matched_entries)
        noun = "entrada" if total == 1 else "entradas"
        header = f"{project_label}, {requested}: {total} {noun} de {result.total_entries}."
    elif result.requested_category is None and result.requested_state is not None:
        requested_state = humanize_state_label(result.normalized_state or normalize_state(result.requested_state))
        total = len(result.matched_entries)
        noun = "entrada" if total == 1 else "entradas"
        header = f"{project_label}, estado {requested_state}: {total} {noun} de {result.total_entries}."
    else:
        requested = humanize_category_name(result.normalized_category or normalize_name(result.requested_category))
        requested_state = humanize_state_label(result.normalized_state or normalize_state(result.requested_state))
        total = len(result.matched_entries)
        noun = "entrada" if total == 1 else "entradas"
        header = f"{project_label}, {requested}, estado {requested_state}: {total} {noun} de {result.total_entries}."

    lines = [header]
    page = paginate_items(result.matched_entries, offset, max_entries)

    if result.matched_entries and page.visible_items:
        if len(result.matched_entries) > max_entries or offset > 0:
            lines.append(f"Te enseño las entradas {build_pagination_label(page, noun='entradas')}.")
        for entry in page.visible_items:
            lines.append(format_entry_summary_human(entry))
    else:
        lines.append("No he encontrado entradas para mostrar.")
        if result.requested_category is not None and result.suggested_categories:
            suggestions = ", ".join(humanize_category_name(item) for item in result.suggested_categories)
            lines.append(f"Quizá quisiste decir: {suggestions}.")

    end_hint = build_end_of_results_hint(page, technical=False)
    if end_hint:
        lines.append(end_hint)
    next_hint = build_next_page_hint(page, technical=False)
    if next_hint:
        lines.append(next_hint)

    if result.warnings:
        lines.append(f"Avisos de lectura: {len(result.warnings)}")
        lines.extend(format_warning(warning) for warning in result.warnings)

    if overview is not None:
        lines.extend(build_overview_sections_human(overview))

    return "\n".join(lines)


def build_search_output(result: SearchResult, max_entries: int = 20, *, technical: bool = True, offset: int = 0) -> str:
    if technical:
        return build_search_output_technical(result, max_entries=max_entries, offset=offset)
    return build_search_output_human(result, max_entries=max_entries, offset=offset)


def build_search_output_technical(result: SearchResult, max_entries: int = 20, offset: int = 0) -> str:
    lines = [
        f'Proyecto {result.project}, búsqueda "{result.query}": '
        f"{len(result.matched_hits)} coincidencias en {result.total_entries} entradas válidas."
    ]
    page = paginate_items(result.matched_hits, offset, max_entries)

    if result.matched_hits and page.visible_items:
        if len(result.matched_hits) > max_entries or offset > 0:
            lines.append(f"Mostrando coincidencias {build_pagination_label(page, noun='coincidencias')}.")
        for hit in page.visible_items:
            lines.append(format_search_hit(hit))
        lines.append("Para ver una entrada completa, usa --entry-id con el id mostrado.")
    else:
        lines.append("No se encontraron coincidencias.")

    end_hint = build_end_of_results_hint(page, technical=True)
    if end_hint:
        lines.append(end_hint)
    next_hint = build_next_page_hint(page, technical=True)
    if next_hint:
        lines.append(next_hint)

    if result.warnings:
        lines.append(f"Avisos de lectura: {len(result.warnings)}")
        lines.extend(format_warning(warning) for warning in result.warnings)

    return "\n".join(lines)


def build_search_output_human(result: SearchResult, max_entries: int = 20, offset: int = 0) -> str:
    project_label = humanize_project_name(result.project)
    total_hits = len(result.matched_hits)
    noun = "coincidencia" if total_hits == 1 else "coincidencias"
    lines = [f'{project_label}, búsqueda "{result.query}": {total_hits} {noun} en {result.total_entries} entradas.']
    page = paginate_items(result.matched_hits, offset, max_entries)

    if result.matched_hits and page.visible_items:
        if len(result.matched_hits) > max_entries or offset > 0:
            lines.append(f"Te enseño las coincidencias {build_pagination_label(page, noun='coincidencias')}.")
        for hit in page.visible_items:
            lines.append(format_search_hit_human(hit))
        lines.append("Si quieres, te muestro la entrada completa.")
    else:
        lines.append("No he encontrado coincidencias.")

    end_hint = build_end_of_results_hint(page, technical=False)
    if end_hint:
        lines.append(end_hint)
    next_hint = build_next_page_hint(page, technical=False)
    if next_hint:
        lines.append(next_hint)

    if result.warnings:
        lines.append(f"Avisos de lectura: {len(result.warnings)}")
        lines.extend(format_warning(warning) for warning in result.warnings)

    return "\n".join(lines)


def build_entry_output(result: EntryLookupResult, *, technical: bool = True) -> str:
    if technical:
        return build_entry_output_technical(result)
    return build_entry_output_human(result)


def build_entry_output_technical(result: EntryLookupResult) -> str:
    if result.entry is None:
        lines = [
            f"Proyecto {result.project}: no existe la entrada {result.requested_entry_id} "
            f"entre {result.total_entries} entradas válidas."
        ]
    else:
        lines = [format_entry_full(result.entry)]

    if result.warnings:
        lines.append(f"Avisos de lectura: {len(result.warnings)}")
        lines.extend(format_warning(warning) for warning in result.warnings)

    return "\n".join(lines)


def build_entry_output_human(result: EntryLookupResult) -> str:
    if result.entry is None:
        lines = [
            f"No he encontrado esa entrada en {humanize_project_name(result.project)}."
        ]
    else:
        lines = [format_entry_full_human(result.entry)]

    if result.warnings:
        lines.append(f"Avisos de lectura: {len(result.warnings)}")
        lines.extend(format_warning(warning) for warning in result.warnings)

    return "\n".join(lines)


def build_operational_view_output(
    result: OperationalViewResult,
    max_entries: int = 20,
    *,
    technical: bool = True,
    offset: int = 0,
) -> str:
    if technical:
        return build_operational_view_output_technical(result, max_entries=max_entries, offset=offset)
    return build_operational_view_output_human(result, max_entries=max_entries, offset=offset)


def build_operational_view_output_technical(result: OperationalViewResult, max_entries: int = 20, offset: int = 0) -> str:
    if result.view_name == "recent":
        header = (
            f"Proyecto {result.project}, últimas entradas: "
            f"{len(result.matched_entries)} de {result.total_entries} válidas."
        )
    elif result.view_name == "pending_enrichment":
        header = (
            f"Proyecto {result.project}, pendientes de enriquecer: "
            f"{len(result.matched_entries)} entradas de {result.total_entries}."
        )
    elif result.view_name.startswith("summary_quality:"):
        quality = result.view_name.split(":", 1)[1]
        header = (
            f"Proyecto {result.project}, calidad_resumen {quality}: "
            f"{len(result.matched_entries)} entradas de {result.total_entries}."
        )
    else:
        header = f"Proyecto {result.project}: {len(result.matched_entries)} entradas de {result.total_entries}."

    lines = [header]
    page = paginate_items(result.matched_entries, offset, max_entries)
    if result.matched_entries and page.visible_items:
        if len(result.matched_entries) > max_entries or offset > 0:
            lines.append(f"Mostrando entradas {build_pagination_label(page, noun='entradas')}.")
        for entry in page.visible_items:
            lines.append(format_entry_summary(entry))
    else:
        lines.append("No hay entradas para mostrar.")

    end_hint = build_end_of_results_hint(page, technical=True)
    if end_hint:
        lines.append(end_hint)
    next_hint = build_next_page_hint(page, technical=True)
    if next_hint:
        lines.append(next_hint)

    if result.warnings:
        lines.append(f"Avisos de lectura: {len(result.warnings)}")
        lines.extend(format_warning(warning) for warning in result.warnings)

    return "\n".join(lines)


def build_operational_view_output_human(result: OperationalViewResult, max_entries: int = 20, offset: int = 0) -> str:
    project_label = humanize_project_name(result.project)
    if result.view_name == "recent":
        header = f"{project_label}, últimas entradas: {len(result.matched_entries)} de {result.total_entries}."
        empty_line = "Todavía no hay entradas recientes que enseñar."
    elif result.view_name == "pending_enrichment":
        total = len(result.matched_entries)
        noun = "entrada" if total == 1 else "entradas"
        header = f"{project_label}, pendientes de enriquecer: {total} {noun}."
        empty_line = "No tienes entradas pendientes de enriquecer."
    elif result.view_name.startswith("summary_quality:"):
        quality = result.view_name.split(":", 1)[1]
        header = (
            f"{project_label}, {humanize_summary_quality_label(quality)}: "
            f"{len(result.matched_entries)} entradas."
        )
        empty_line = "No hay entradas que coincidan con esa calidad de resumen."
    else:
        header = f"{project_label}: {len(result.matched_entries)} entradas."
        empty_line = "No he encontrado entradas para mostrar."

    lines = [header]
    page = paginate_items(result.matched_entries, offset, max_entries)
    if result.matched_entries and page.visible_items:
        if len(result.matched_entries) > max_entries or offset > 0:
            lines.append(f"Te enseño las entradas {build_pagination_label(page, noun='entradas')}.")
        for entry in page.visible_items:
            lines.append(format_entry_summary_human(entry))
        if result.view_name == "pending_enrichment":
            lines.append("Si quieres, puedo ayudarte a enriquecer una de estas entradas ahora.")
    else:
        lines.append(empty_line)

    end_hint = build_end_of_results_hint(page, technical=False)
    if end_hint:
        lines.append(end_hint)
    next_hint = build_next_page_hint(page, technical=False)
    if next_hint:
        lines.append(next_hint)

    if result.warnings:
        lines.append(f"Avisos de lectura: {len(result.warnings)}")
        lines.extend(format_warning(warning) for warning in result.warnings)

    return "\n".join(lines)


def build_enrichment_reminder(project: str, data_dir: Path = DEFAULT_DATA_DIR, *, technical: bool = True, limit: int = 5) -> str:
    result = list_pending_enrichment_entries(project=project, data_dir=data_dir)
    if technical:
        if not result.matched_entries:
            return f"Recordatorio bitácora ({result.project}): no hay entradas pendientes de enriquecer."
        titles = "; ".join(entry.titulo for entry in result.matched_entries[:max(limit, 1)])
        return (
            f"Recordatorio bitácora ({result.project}): {len(result.matched_entries)} entradas con "
            f"calidad_resumen=fallback pendientes de enriquecer. {titles}"
        )

    project_label = humanize_project_name(result.project)
    if not result.matched_entries:
        return f"Hoy no tienes entradas pendientes de enriquecer en {project_label}."

    visible_entries = result.matched_entries[: max(limit, 1)]
    titles = "; ".join(entry.titulo for entry in visible_entries)
    noun = "entrada" if len(result.matched_entries) == 1 else "entradas"
    return (
        f"Tienes {len(result.matched_entries)} {noun} pendientes de enriquecer en {project_label}: "
        f"{titles}. Si quieres, retomamos una ahora."
    )


def build_daily_enrichment_reminder_job(project: str, *, session_target: str = "current") -> dict:
    normalized_project = normalize_name(project)
    return {
        "name": f"bitacora-{normalized_project}-daily-reminder",
        "schedule": {
            "kind": "cron",
            "expr": REMINDER_CRON_EXPRESSION,
            "tz": REMINDER_TIMEZONE,
        },
        "sessionTarget": session_target,
        "payload": {
            "kind": "agentTurn",
            "message": (
                f"Revisa el proyecto {normalized_project} de bitácora. Si hay entradas con calidad_resumen: "
                "fallback y estado distinto de descartado, envía un recordatorio breve y humano con las "
                "pendientes más recientes. Si no hay pendientes, responde con un breve mensaje de que hoy no hay nada pendiente."
            ),
            "timeoutSeconds": 120,
            "lightContext": True,
        },
        "delivery": {
            "mode": "announce",
        },
    }


def build_overview_sections_human(overview: ProjectOverviewResult) -> list[str]:
    lines: list[str] = []

    lines.append("Resumen por categorías:")
    if overview.category_index:
        for item in overview.category_index:
            latest = format_visible_date(item.latest_update) if item.latest_update else "sin fecha legible"
            lines.append(
                f"- {humanize_category_name(item.categoria)}: {item.total_entries} entradas, última actualización {latest}"
            )
    else:
        lines.append("- Sin entradas válidas para agrupar.")

    lines.append("Resumen por tipos:")
    if overview.type_index:
        for item in overview.type_index:
            lines.append(f"- {humanize_resource_type(item.tipo)}: {item.total_entries} entradas")
    else:
        lines.append("- Sin tipos válidos.")

    lines.append("Datos rápidos:")
    lines.append(f"- Total entradas: {overview.total_entries}")
    lines.append(f"- Categorías distintas: {len(overview.category_index)}")
    lines.append(f"- Tipos presentes: {len(overview.type_index)}")
    lines.append(
        f"- Última actualización: {format_visible_date(overview.latest_update) if overview.latest_update else 'sin fecha legible'}"
    )

    return lines


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Leer, listar y buscar entradas de bitácora")
    parser.add_argument("--project", help="Nombre del proyecto")
    parser.add_argument("--category", help="Categoría exacta o variación menor")
    parser.add_argument("--state", help="Filtrar por estado: nuevo, revisado, descartado")
    parser.add_argument("--search", help="Texto a buscar en título, resumen, tags y nota personal")
    parser.add_argument("--entry-id", help="Mostrar una entrada concreta por id")
    parser.add_argument("--recent", type=int, help="Mostrar las últimas N entradas del proyecto")
    parser.add_argument("--summary-quality", help="Filtrar por calidad_resumen: fallback, auto, usuario")
    parser.add_argument("--pending-enrichment", action="store_true", help="Mostrar entradas con calidad_resumen fallback y no descartadas")
    parser.add_argument("--reminder-preview", action="store_true", help="Mostrar el texto del recordatorio diario")
    parser.add_argument("--reminder-job", action="store_true", help="Mostrar la configuración nativa del recordatorio diario en OpenClaw")
    parser.add_argument("--overview", action="store_true", help="Mostrar índices y estadísticas derivadas del proyecto")
    parser.add_argument("--global-stats", action="store_true", help="Mostrar estadísticas agregadas de todos los proyectos")
    parser.add_argument("--technical", action="store_true", help="Mostrar salida técnica explícita")
    parser.add_argument("--data-dir", default=str(DEFAULT_DATA_DIR), help="Directorio de datos")
    parser.add_argument("--max-entries", type=int, default=20, help="Máximo de entradas a mostrar")
    parser.add_argument("--offset", type=int, default=0, help="Desplazamiento para paginar resultados")
    args = parser.parse_args(argv)
    exclusive_modes = [
        bool(args.search),
        bool(args.entry_id),
        bool(args.recent is not None),
        bool(args.summary_quality),
        bool(args.pending_enrichment),
        bool(args.reminder_preview),
        bool(args.reminder_job),
        bool(args.overview),
    ]
    if args.category and args.search:
        parser.error("--category y --search no pueden usarse a la vez")
    if args.entry_id and (args.category or args.search or args.state):
        parser.error("--entry-id no puede combinarse con --category, --search ni --state")
    if args.global_stats and args.project:
        parser.error("--global-stats no puede combinarse con --project")
    if args.global_stats and (
        args.category or args.state or args.search or args.entry_id or args.overview or args.recent is not None
        or args.summary_quality or args.pending_enrichment or args.reminder_preview or args.reminder_job
    ):
        parser.error("--global-stats no puede combinarse con filtros ni con --overview")
    if sum(1 for mode in exclusive_modes if mode) > 1:
        parser.error("Usa solo un modo principal por ejecución")
    if args.overview and (args.category or args.search or args.entry_id or args.state):
        parser.error("--overview no puede combinarse con --category, --search, --entry-id ni --state")
    if not args.global_stats and not args.project:
        parser.error("--project es obligatorio salvo con --global-stats")
    return args


def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv)
    try:
        if args.global_stats:
            result = build_global_stats(data_dir=Path(args.data_dir))
            output = build_global_stats_output_technical(result) if args.technical else build_global_stats_output_human(result)
            print(output)
            return 0

        if args.reminder_job:
            print(json.dumps(build_daily_enrichment_reminder_job(args.project), ensure_ascii=False, indent=2))
            return 0

        if args.reminder_preview:
            print(build_enrichment_reminder(args.project, Path(args.data_dir), technical=args.technical, limit=max(args.max_entries, 1)))
            return 0

        if args.entry_id:
            result = get_entry_by_id(
                project=args.project,
                entry_id=args.entry_id,
                data_dir=Path(args.data_dir),
            )
            print(build_entry_output(result, technical=args.technical))
            return 0

        if args.search:
            result = search_entries(
                project=args.project,
                query=args.search,
                data_dir=Path(args.data_dir),
            )
            print(build_search_output(result, max_entries=max(args.max_entries, 1), technical=args.technical, offset=args.offset))
            return 0

        if args.recent is not None:
            result = list_recent_entries(
                project=args.project,
                data_dir=Path(args.data_dir),
                limit=max(args.recent, 0),
            )
            print(build_operational_view_output(result, max_entries=max(args.max_entries, 1), technical=args.technical, offset=args.offset))
            return 0

        if args.summary_quality:
            result = list_entries_by_summary_quality(
                project=args.project,
                quality=args.summary_quality,
                data_dir=Path(args.data_dir),
            )
            print(build_operational_view_output(result, max_entries=max(args.max_entries, 1), technical=args.technical, offset=args.offset))
            return 0

        if args.pending_enrichment:
            result = list_pending_enrichment_entries(
                project=args.project,
                data_dir=Path(args.data_dir),
            )
            print(build_operational_view_output(result, max_entries=max(args.max_entries, 1), technical=args.technical, offset=args.offset))
            return 0

        result = list_entries(
            project=args.project,
            data_dir=Path(args.data_dir),
            category=args.category,
            state=args.state,
        )
        overview = build_project_overview(args.project, Path(args.data_dir)) if args.overview else None
    except Exception as exc:  # pragma: no cover
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(build_output(result, max_entries=max(args.max_entries, 1), overview=overview, technical=args.technical, offset=args.offset))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
