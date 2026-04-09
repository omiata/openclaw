#!/usr/bin/env python3
from __future__ import annotations

import argparse
import difflib
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import yaml

from save_entry import DEFAULT_DATA_DIR, ENTRY_DELIMITER, ascii_fold, normalize_name

REQUIRED_FIELDS = ("id", "fecha", "proyecto", "categoria", "tipo", "titulo", "resumen")
SEARCHABLE_FIELDS = ("titulo", "resumen", "tags", "contenido_adicional")


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


@dataclass
class ListingResult:
    project: str
    file_path: Path
    total_entries: int
    matched_entries: list[StoredEntry]
    warnings: list[ParseWarning]
    requested_category: Optional[str] = None
    normalized_category: Optional[str] = None
    suggested_categories: list[str] = field(default_factory=list)


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
class EntryLookupResult:
    project: str
    file_path: Path
    total_entries: int
    requested_entry_id: str
    entry: Optional[StoredEntry]
    warnings: list[ParseWarning]


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


def extract_frontmatter(block: str) -> tuple[str, str]:
    lines = block.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("El bloque no empieza con frontmatter YAML")

    end_index = None
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            end_index = index
            break

    if end_index is None:
        raise ValueError("No se encontró cierre del frontmatter YAML")

    yaml_text = "\n".join(lines[1:end_index])
    body = "\n".join(lines[end_index + 1 :]).strip()
    return yaml_text, body


def parse_tags(raw_tags: object) -> list[str]:
    if raw_tags is None:
        return []
    if isinstance(raw_tags, str):
        candidate = raw_tags.strip()
        return [candidate] if candidate else []
    if isinstance(raw_tags, list):
        normalized: list[str] = []
        for item in raw_tags:
            if item is None:
                continue
            candidate = str(item).strip()
            if candidate:
                normalized.append(candidate)
        return normalized
    raise ValueError("El campo tags debe ser una lista o string")


def parse_entry_block(block: str, position: int, source_path: Path) -> StoredEntry:
    yaml_text, body = extract_frontmatter(block)
    parsed = yaml.safe_load(yaml_text)
    if not isinstance(parsed, dict):
        raise ValueError("El YAML no se parseó como mapa")

    missing_fields = [field for field in REQUIRED_FIELDS if field not in parsed or parsed[field] in (None, "")]
    if missing_fields:
        raise ValueError(f"Faltan campos obligatorios: {', '.join(missing_fields)}")

    return StoredEntry(
        entry_id=str(parsed["id"]),
        fecha=str(parsed["fecha"]),
        proyecto=str(parsed["proyecto"]),
        categoria=str(parsed["categoria"]),
        tipo=str(parsed["tipo"]),
        titulo=str(parsed["titulo"]),
        resumen=str(parsed["resumen"]),
        contenido=body,
        source_path=source_path,
        position=position,
        fuente=str(parsed["fuente"]).strip() if parsed.get("fuente") not in (None, "") else None,
        tags=parse_tags(parsed.get("tags")),
        contenido_adicional=(
            str(parsed["contenido_adicional"]).strip()
            if parsed.get("contenido_adicional") not in (None, "")
            else None
        ),
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


def sort_entries(entries: list[StoredEntry]) -> list[StoredEntry]:
    def key(entry: StoredEntry) -> datetime:
        try:
            return datetime.fromisoformat(entry.fecha.replace("Z", "+00:00"))
        except ValueError:
            return datetime.min.replace(tzinfo=timezone.utc)

    return sorted(entries, key=key, reverse=True)


def filter_entries_by_category(entries: list[StoredEntry], category: str) -> tuple[str, list[StoredEntry]]:
    normalized_category = normalize_name(category)
    matched = [entry for entry in entries if normalize_name(entry.categoria) == normalized_category]
    return normalized_category, matched


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
) -> ListingResult:
    entries, warnings, file_path = load_entries(project=project, data_dir=data_dir)
    if category is None:
        return ListingResult(
            project=normalize_name(project),
            file_path=file_path,
            total_entries=len(entries),
            matched_entries=entries,
            warnings=warnings,
        )

    normalized_category, matched_entries = filter_entries_by_category(entries, category)
    suggestions = suggest_categories(entries, category) if not matched_entries else []
    return ListingResult(
        project=normalize_name(project),
        file_path=file_path,
        total_entries=len(entries),
        matched_entries=matched_entries,
        warnings=warnings,
        requested_category=category,
        normalized_category=normalized_category,
        suggested_categories=suggestions,
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
        f"  resumen: {entry.resumen}",
    ]
    if entry.fuente:
        lines.append(f"  fuente: {entry.fuente}")
    if entry.tags:
        lines.append(f"  tags: {', '.join(entry.tags)}")
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


def format_entry_full(entry: StoredEntry) -> str:
    lines = [
        f"ID: {entry.entry_id}",
        f"Proyecto: {entry.proyecto}",
        f"Categoría: {entry.categoria}",
        f"Tipo: {entry.tipo}",
        f"Fecha: {entry.fecha}",
        f"Título: {entry.titulo}",
        f"Resumen: {entry.resumen}",
    ]
    if entry.fuente:
        lines.append(f"Fuente: {entry.fuente}")
    if entry.tags:
        lines.append(f"Tags: {', '.join(entry.tags)}")
    if entry.contenido_adicional:
        lines.append(f"Nota adicional: {entry.contenido_adicional}")
    lines.append("Contenido:")
    lines.append(entry.contenido or "(sin contenido)")
    return "\n".join(lines)


def format_warning(warning: ParseWarning) -> str:
    location = f"id {warning.entry_id}" if warning.entry_id else f"posición {warning.position}"
    return f"- {location}: {warning.message}"


def build_output(result: ListingResult, max_entries: int = 20) -> str:
    if result.requested_category is None:
        header = f"Proyecto {result.project}: {result.total_entries} entradas válidas."
    else:
        header = (
            f"Proyecto {result.project}, categoría {result.normalized_category}: "
            f"{len(result.matched_entries)} entradas de {result.total_entries} válidas."
        )

    lines = [header]

    if result.matched_entries:
        visible_entries = result.matched_entries[:max_entries]
        if len(result.matched_entries) > max_entries:
            lines.append(f"Mostrando {len(visible_entries)} de {len(result.matched_entries)} entradas.")
        for entry in visible_entries:
            lines.append(format_entry_summary(entry))
    else:
        lines.append("No hay entradas para mostrar.")
        if result.requested_category is not None and result.suggested_categories:
            lines.append(
                "Aviso de categoría ambigua o no encontrada. "
                f"Quizá quisiste decir: {', '.join(result.suggested_categories)}."
            )

    if result.warnings:
        lines.append(f"Avisos de lectura: {len(result.warnings)}")
        lines.extend(format_warning(warning) for warning in result.warnings)

    return "\n".join(lines)


def build_search_output(result: SearchResult, max_entries: int = 20) -> str:
    lines = [
        f'Proyecto {result.project}, búsqueda "{result.query}": '
        f"{len(result.matched_hits)} coincidencias en {result.total_entries} entradas válidas."
    ]

    if result.matched_hits:
        visible_hits = result.matched_hits[:max_entries]
        if len(result.matched_hits) > max_entries:
            lines.append(f"Mostrando {len(visible_hits)} de {len(result.matched_hits)} coincidencias.")
        for hit in visible_hits:
            lines.append(format_search_hit(hit))
        lines.append("Para ver una entrada completa, usa --entry-id con el id mostrado.")
    else:
        lines.append("No se encontraron coincidencias.")

    if result.warnings:
        lines.append(f"Avisos de lectura: {len(result.warnings)}")
        lines.extend(format_warning(warning) for warning in result.warnings)

    return "\n".join(lines)


def build_entry_output(result: EntryLookupResult) -> str:
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


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Leer, listar y buscar entradas de bitácora")
    parser.add_argument("--project", required=True, help="Nombre del proyecto")
    parser.add_argument("--category", help="Categoría exacta o variación menor")
    parser.add_argument("--search", help="Texto a buscar en título, resumen, tags y contenido adicional")
    parser.add_argument("--entry-id", help="Mostrar una entrada concreta por id")
    parser.add_argument("--data-dir", default=str(DEFAULT_DATA_DIR), help="Directorio de datos")
    parser.add_argument("--max-entries", type=int, default=20, help="Máximo de entradas a mostrar")
    args = parser.parse_args(argv)
    if args.category and args.search:
        parser.error("--category y --search no pueden usarse a la vez")
    if args.entry_id and (args.category or args.search):
        parser.error("--entry-id no puede combinarse con --category ni --search")
    return args


def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv)
    try:
        if args.entry_id:
            result = get_entry_by_id(
                project=args.project,
                entry_id=args.entry_id,
                data_dir=Path(args.data_dir),
            )
            print(build_entry_output(result))
            return 0

        if args.search:
            result = search_entries(
                project=args.project,
                query=args.search,
                data_dir=Path(args.data_dir),
            )
            print(build_search_output(result, max_entries=max(args.max_entries, 1)))
            return 0

        result = list_entries(
            project=args.project,
            data_dir=Path(args.data_dir),
            category=args.category,
        )
    except Exception as exc:  # pragma: no cover
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(build_output(result, max_entries=max(args.max_entries, 1)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
