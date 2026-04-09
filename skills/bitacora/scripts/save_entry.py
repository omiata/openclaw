#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import re
import sys
import time
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Optional, Sequence
from urllib.parse import unquote, urlparse

ROOT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DATA_DIR = ROOT_DIR / "data"
ENTRY_DELIMITER = "---entry---"
VALID_TYPES = ("link", "video", "documento", "nota", "idea", "referencia")
VIDEO_HOSTS = ("youtube.com", "youtu.be", "vimeo.com")
DOCUMENT_EXTENSIONS = (
    ".pdf",
    ".doc",
    ".docx",
    ".ppt",
    ".pptx",
    ".xls",
    ".xlsx",
    ".odt",
    ".ods",
    ".txt",
    ".rtf",
)
URL_PATTERN = re.compile(r"https?://\S+", re.IGNORECASE)


@dataclass
class Entry:
    entry_id: str
    fecha: str
    proyecto: str
    categoria: str
    tipo: str
    titulo: str
    resumen: str
    contenido: str
    fuente: Optional[str] = None
    tags: tuple[str, ...] = ()
    contenido_adicional: Optional[str] = None


def normalize_text(value: str) -> str:
    value = value.replace("\r\n", "\n").replace("\r", "\n")
    return value.strip()


def squeeze_whitespace(value: str) -> str:
    return " ".join(normalize_text(value).split())


def ascii_fold(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    return normalized.encode("ascii", "ignore").decode("ascii")


def normalize_name(value: str) -> str:
    value = ascii_fold(normalize_text(value)).lower()
    value = re.sub(r"\s+", "-", value)
    value = re.sub(r"[^a-z0-9_-]", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    if not value:
        raise ValueError("El nombre no puede quedar vacío")
    return value


def normalize_optional_text(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    normalized = normalize_text(value)
    return normalized or None


def ensure_no_entry_delimiter(field_name: str, value: Optional[str]) -> None:
    if value and ENTRY_DELIMITER in value:
        raise ValueError(f"El campo {field_name} no puede contener el delimitador {ENTRY_DELIMITER}")


def normalize_tag(value: str) -> str:
    return normalize_name(value)


def normalize_tags(values: Optional[Sequence[str]]) -> tuple[str, ...]:
    if not values:
        return ()

    normalized_tags: list[str] = []
    seen: set[str] = set()
    for raw_tag in values:
        if raw_tag is None:
            continue
        for piece in re.split(r"[,\n]", raw_tag):
            candidate = piece.strip()
            if not candidate:
                continue
            tag = normalize_tag(candidate)
            ensure_no_entry_delimiter("tags", tag)
            if tag not in seen:
                seen.add(tag)
                normalized_tags.append(tag)
    return tuple(normalized_tags)


def extract_first_url(*values: Optional[str]) -> Optional[str]:
    for value in values:
        if not value:
            continue
        match = URL_PATTERN.search(value)
        if match:
            return match.group(0)
    return None


def is_plain_url(value: Optional[str]) -> bool:
    if not value:
        return False
    stripped = normalize_text(value)
    return bool(URL_PATTERN.fullmatch(stripped))


def normalize_resource_type(resource_type: str) -> str:
    normalized = normalize_name(resource_type)
    if normalized not in VALID_TYPES:
        allowed = ", ".join(VALID_TYPES)
        raise ValueError(f"Tipo no soportado: {resource_type}. Tipos válidos: {allowed}")
    return normalized


def infer_type(content: str, source: Optional[str], explicit_type: Optional[str] = None) -> str:
    if explicit_type:
        return normalize_resource_type(explicit_type)

    url = extract_first_url(source, content)
    if url:
        parsed = urlparse(url)
        host = (parsed.netloc or "").lower()
        path = parsed.path.lower()
        if any(video_host in host for video_host in VIDEO_HOSTS):
            return "video"
        if path.endswith(DOCUMENT_EXTENSIONS):
            return "documento"
        return "link"

    return "nota"


def shorten_line(value: str, max_length: int) -> str:
    clean = squeeze_whitespace(value)
    if not clean:
        return ""
    if len(clean) <= max_length:
        return clean
    return clean[: max_length - 3].rstrip() + "..."


def derive_title_from_url(url: str) -> str:
    parsed = urlparse(url)
    last_segment = unquote(parsed.path.rstrip("/").split("/")[-1]) if parsed.path else ""
    candidate = re.sub(r"[-_]+", " ", last_segment)
    candidate = re.sub(r"\.[a-z0-9]{1,5}$", "", candidate, flags=re.IGNORECASE)
    candidate = shorten_line(candidate, 90)
    if candidate:
        return candidate[0].upper() + candidate[1:] if len(candidate) > 1 else candidate.upper()
    domain = parsed.netloc or url
    return shorten_line(domain, 90)


def make_title(
    content: str,
    source: Optional[str],
    additional_content: Optional[str],
    explicit_title: Optional[str],
    resource_type: str,
    category: str,
) -> str:
    if explicit_title:
        title = shorten_line(explicit_title, 90)
        if title:
            return title

    for candidate in (content, source, additional_content):
        if candidate and not is_plain_url(candidate):
            title = shorten_line(candidate.splitlines()[0], 90)
            if title:
                return title

    url = extract_first_url(source, content)
    if url:
        return derive_title_from_url(url)

    return f"{resource_type.capitalize()} de {category}"


def make_summary(
    project: str,
    category: str,
    title: str,
    content: str,
    source: Optional[str],
    additional_content: Optional[str],
    explicit_summary: Optional[str],
) -> str:
    if explicit_summary:
        summary_lines = [shorten_line(line, 160) for line in normalize_text(explicit_summary).splitlines() if line.strip()]
        summary_lines = [line for line in summary_lines if line]
        if summary_lines:
            return "\n".join(summary_lines[:3])

    lines: list[str] = []

    for candidate in (content, additional_content, source):
        if candidate and not is_plain_url(candidate):
            snippet = shorten_line(candidate, 160)
            if snippet and snippet.lower() != title.lower():
                lines.append(snippet)
                break

    url = extract_first_url(source, content)
    if url:
        host = urlparse(url).netloc or url
        lines.append(f"Fuente: {host}.")

    lines.append(f"Relevante para {project}/{category}.")

    cleaned_lines: list[str] = []
    seen: set[str] = set()
    for line in lines:
        clean = shorten_line(line, 160)
        key = clean.lower()
        if clean and key not in seen:
            seen.add(key)
            cleaned_lines.append(clean)
        if len(cleaned_lines) == 3:
            break

    if cleaned_lines:
        return "\n".join(cleaned_lines)
    return f"Relevante para {project}/{category}."


def ensure_entry_has_material(
    content: str,
    source: Optional[str],
    additional_content: Optional[str],
    title: Optional[str],
) -> None:
    if any(normalize_optional_text(value) for value in (content, source, additional_content, title)):
        return
    raise ValueError("Debe proporcionarse contenido, fuente, contenido adicional o título")


def generate_entry(
    project: str,
    category: str,
    content: str = "",
    *,
    resource_type: Optional[str] = None,
    title: Optional[str] = None,
    summary: Optional[str] = None,
    source: Optional[str] = None,
    tags: Optional[Sequence[str]] = None,
    additional_content: Optional[str] = None,
) -> Entry:
    ensure_entry_has_material(content, source, additional_content, title)

    now = datetime.now(timezone.utc)
    normalized_project = normalize_name(project)
    normalized_category = normalize_name(category)
    normalized_content = normalize_text(content) if content else ""
    normalized_source = normalize_optional_text(source)
    normalized_additional = normalize_optional_text(additional_content)
    normalized_tags = normalize_tags(tags)
    normalized_type = infer_type(normalized_content, normalized_source, resource_type)
    normalized_title = make_title(
        content=normalized_content,
        source=normalized_source,
        additional_content=normalized_additional,
        explicit_title=normalize_optional_text(title),
        resource_type=normalized_type,
        category=normalized_category,
    )
    normalized_summary = make_summary(
        project=normalized_project,
        category=normalized_category,
        title=normalized_title,
        content=normalized_content,
        source=normalized_source,
        additional_content=normalized_additional,
        explicit_summary=normalize_optional_text(summary),
    )

    for field_name, value in (
        ("contenido", normalized_content),
        ("fuente", normalized_source),
        ("contenido_adicional", normalized_additional),
        ("titulo", normalized_title),
        ("resumen", normalized_summary),
    ):
        ensure_no_entry_delimiter(field_name, value)
    for tag in normalized_tags:
        ensure_no_entry_delimiter("tags", tag)

    entry_id = f"entry-{time.time_ns() // 1_000_000}"
    return Entry(
        entry_id=entry_id,
        fecha=now.isoformat(timespec="milliseconds").replace("+00:00", "Z"),
        proyecto=normalized_project,
        categoria=normalized_category,
        tipo=normalized_type,
        titulo=normalized_title,
        resumen=normalized_summary,
        contenido=normalized_content,
        fuente=normalized_source,
        tags=normalized_tags,
        contenido_adicional=normalized_additional,
    )


def yaml_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def render_yaml_string(key: str, value: str) -> list[str]:
    if "\n" in value:
        lines = [f"{key}: |-"]
        for line in value.splitlines():
            lines.append(f"  {line}")
        if value.endswith("\n"):
            lines.append("  ")
        return lines
    return [f'{key}: "{yaml_escape(value)}"']


def render_frontmatter(entry: Entry) -> str:
    lines: list[str] = []
    for key, value in (
        ("id", entry.entry_id),
        ("fecha", entry.fecha),
        ("proyecto", entry.proyecto),
        ("categoria", entry.categoria),
        ("tipo", entry.tipo),
        ("titulo", entry.titulo),
        ("resumen", entry.resumen),
    ):
        lines.extend(render_yaml_string(key, value))

    if entry.fuente:
        lines.extend(render_yaml_string("fuente", entry.fuente))
    if entry.tags:
        lines.append("tags:")
        for tag in entry.tags:
            lines.append(f'  - "{yaml_escape(tag)}"')
    if entry.contenido_adicional:
        lines.extend(render_yaml_string("contenido_adicional", entry.contenido_adicional))
    return "\n".join(lines)


def render_entry(entry: Entry) -> str:
    body_lines = [
        ENTRY_DELIMITER,
        "",
        "---",
        render_frontmatter(entry),
        "---",
        "",
        "**Título**",
        entry.titulo,
        "",
        "**Resumen**",
        entry.resumen,
        "",
    ]

    if entry.fuente:
        body_lines.extend(["**Fuente**", entry.fuente, ""])
    if entry.tags:
        body_lines.extend(["**Tags**", ", ".join(entry.tags), ""])
    if entry.contenido_adicional:
        body_lines.extend(["**Nota adicional**", entry.contenido_adicional, ""])

    body_lines.extend(["**Contenido**", entry.contenido or "(sin contenido)", ""])
    return "\n".join(body_lines)


def append_entry(
    project: str,
    category: str,
    content: str = "",
    data_dir: Path = DEFAULT_DATA_DIR,
    *,
    resource_type: Optional[str] = None,
    title: Optional[str] = None,
    summary: Optional[str] = None,
    source: Optional[str] = None,
    tags: Optional[Sequence[str]] = None,
    additional_content: Optional[str] = None,
) -> tuple[Entry, Path]:
    entry = generate_entry(
        project=project,
        category=category,
        content=content,
        resource_type=resource_type,
        title=title,
        summary=summary,
        source=source,
        tags=tags,
        additional_content=additional_content,
    )
    data_dir.mkdir(parents=True, exist_ok=True)
    file_path = data_dir / f"{entry.proyecto}.md"
    rendered = render_entry(entry)

    prefix = ""
    if file_path.exists() and file_path.stat().st_size > 0:
        with file_path.open("rb") as existing:
            existing.seek(-1, os.SEEK_END)
            last_byte = existing.read(1)
        if last_byte != b"\n":
            prefix = "\n"

    with file_path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(prefix)
        handle.write(rendered)

    return entry, file_path


def build_confirmation(entry: Entry, file_path: Path) -> str:
    extras: list[str] = []
    if entry.fuente:
        extras.append("con fuente")
    if entry.tags:
        extras.append(f"{len(entry.tags)} tags")
    if entry.contenido_adicional:
        extras.append("con nota adicional")
    suffix = f" [{', '.join(extras)}]" if extras else ""
    return (
        f"Guardado en {entry.proyecto}/{entry.categoria}: {entry.titulo} "
        f"({entry.tipo}){suffix} -> {file_path}"
    )


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Guardar una entrada de bitácora")
    parser.add_argument("--project", required=True, help="Nombre del proyecto")
    parser.add_argument("--category", required=True, help="Categoría de la entrada")
    parser.add_argument("--content", default="", help="Contenido o recurso del usuario")
    parser.add_argument("--type", dest="resource_type", help="Tipo explícito: link, video, documento, nota, idea, referencia")
    parser.add_argument("--title", help="Título explícito de la entrada")
    parser.add_argument("--summary", help="Resumen explícito de la entrada")
    parser.add_argument("--source", help="URL o descripción del origen")
    parser.add_argument("--tag", dest="tags", action="append", default=[], help="Tag opcional, repetir para varios")
    parser.add_argument("--additional-content", help="Nota libre adicional del usuario")
    parser.add_argument("--data-dir", default=str(DEFAULT_DATA_DIR), help="Directorio de datos")
    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv)
    try:
        entry, file_path = append_entry(
            project=args.project,
            category=args.category,
            content=args.content,
            data_dir=Path(args.data_dir),
            resource_type=args.resource_type,
            title=args.title,
            summary=args.summary,
            source=args.source,
            tags=args.tags,
            additional_content=args.additional_content,
        )
    except Exception as exc:  # pragma: no cover
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(build_confirmation(entry, file_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
