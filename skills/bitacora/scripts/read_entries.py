#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import yaml

from save_entry import DEFAULT_DATA_DIR, ENTRY_DELIMITER, normalize_name

REQUIRED_FIELDS = ("id", "fecha", "proyecto", "categoria", "tipo", "titulo", "resumen")


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


@dataclass
class ListingResult:
    project: str
    file_path: Path
    total_entries: int
    matched_entries: list[StoredEntry]
    warnings: list[ParseWarning]
    requested_category: Optional[str] = None
    normalized_category: Optional[str] = None


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
    return ListingResult(
        project=normalize_name(project),
        file_path=file_path,
        total_entries=len(entries),
        matched_entries=matched_entries,
        warnings=warnings,
        requested_category=category,
        normalized_category=normalized_category,
    )


def format_entry_summary(entry: StoredEntry) -> str:
    return (
        f"- {entry.titulo}\n"
        f"  categoría: {entry.categoria} | tipo: {entry.tipo} | fecha: {entry.fecha}\n"
        f"  resumen: {entry.resumen}"
    )


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

    if result.warnings:
        lines.append(f"Avisos de lectura: {len(result.warnings)}")
        lines.extend(format_warning(warning) for warning in result.warnings)

    return "\n".join(lines)


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Leer y listar entradas de bitácora")
    parser.add_argument("--project", required=True, help="Nombre del proyecto")
    parser.add_argument("--category", help="Categoría exacta o variación menor")
    parser.add_argument("--data-dir", default=str(DEFAULT_DATA_DIR), help="Directorio de datos")
    parser.add_argument("--max-entries", type=int, default=20, help="Máximo de entradas a mostrar")
    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv)
    try:
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
