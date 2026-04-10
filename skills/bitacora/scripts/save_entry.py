#!/usr/bin/env python3
from __future__ import annotations

import argparse
from html import unescape
import os
import re
import shutil
import sys
import tempfile
import time
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Optional, Sequence
from urllib.error import HTTPError, URLError
from urllib.parse import quote_plus, unquote, urlparse
from urllib.request import Request, urlopen

import yaml

ROOT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DATA_DIR = ROOT_DIR / "data"
ENTRY_DELIMITER = "---entry---"
VALID_TYPES = ("link", "video", "documento", "nota", "idea", "referencia")
VALID_SUMMARY_QUALITY = ("fallback", "auto", "usuario")
VALID_STATES = ("nuevo", "revisado", "descartado")
VIDEO_HOSTS = ("youtube.com", "youtu.be", "vimeo.com")
YOUTUBE_HOSTS = ("youtube.com", "www.youtube.com", "m.youtube.com", "youtu.be")
VIMEO_HOSTS = ("vimeo.com", "www.vimeo.com", "player.vimeo.com")
EXTERNAL_METADATA_TIMEOUT_SECONDS = 3.0
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
LEGACY_SECTION_MARKERS = {
    "**Título**": "titulo_markdown",
    "**Resumen**": "resumen_markdown",
    "**Fuente**": "fuente_markdown",
    "**Tags**": "tags_markdown",
    "**Nota adicional**": "contenido_adicional_markdown",
    "**Contenido**": "contenido_markdown",
}
V2_SECTION_MARKERS = {
    "**Nota personal**": "nota_personal",
}
DEFAULT_PROJECT_CATEGORIES = {
    "camper": (
        "aislamiento",
        "cama",
        "distribucion",
        "almacenamiento",
        "electricidad",
        "iluminacion",
        "ventilacion",
        "cocina",
        "agua",
        "moto",
        "fijaciones-estructura",
        "homologacion",
        "herramientas-materiales",
        "ideas-generales",
    ),
}


@dataclass
class Entry:
    entry_id: str
    fecha: str
    proyecto: str
    categoria: str
    tipo: str
    titulo: str
    resumen: str
    contenido: str = ""
    fuente: Optional[str] = None
    tags: tuple[str, ...] = ()
    contenido_adicional: Optional[str] = None
    calidad_resumen: str = "fallback"
    estado: str = "nuevo"


@dataclass
class ExternalMetadata:
    title: Optional[str] = None
    description: Optional[str] = None
    source_kind: Optional[str] = None
    resolved_url: Optional[str] = None


@dataclass
class CaptureOutcome:
    status: str
    prompt: str
    entry: Optional[Entry] = None
    file_path: Optional[Path] = None
    suggested_categories: tuple[str, ...] = ()


@dataclass
class DuplicateMatch:
    duplicate_url: str
    entry: Entry
    file_path: Path


@dataclass
class MigrationResult:
    project: str
    file_path: Path
    backup_path: Optional[Path]
    migrated_entries: list[Entry]


class DuplicateEntryError(ValueError):
    def __init__(self, match: DuplicateMatch):
        self.match = match
        super().__init__(
            f'La URL {match.duplicate_url} ya existe en la entrada {match.entry.entry_id} de '
            f'{match.entry.proyecto}/{match.entry.categoria}'
        )


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


def is_useful_free_text(value: Optional[str]) -> bool:
    normalized = normalize_optional_text(value)
    return bool(normalized and not is_plain_url(normalized))


def clean_summary_text(value: str, *, max_lines: int = 3, max_length: int = 160) -> Optional[str]:
    normalized = normalize_optional_text(value)
    if not normalized:
        return None

    cleaned_lines: list[str] = []
    seen: set[str] = set()
    for line in normalized.splitlines():
        compact = shorten_line(line, max_length)
        if not compact:
            continue
        key = compact.lower()
        if key in seen:
            continue
        seen.add(key)
        cleaned_lines.append(compact)
        if len(cleaned_lines) >= max_lines:
            break

    if not cleaned_lines:
        compact = shorten_line(normalized, max_length)
        return compact or None
    return "\n".join(cleaned_lines)


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


def extract_urls(*values: Optional[str]) -> tuple[str, ...]:
    urls: list[str] = []
    seen: set[str] = set()
    for value in values:
        if not value:
            continue
        for match in URL_PATTERN.findall(value):
            candidate = match.strip()
            if candidate and candidate not in seen:
                seen.add(candidate)
                urls.append(candidate)
    return tuple(urls)


def extract_first_url(*values: Optional[str]) -> Optional[str]:
    urls = extract_urls(*values)
    return urls[0] if urls else None


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


def normalize_summary_quality(value: Optional[str]) -> str:
    candidate = normalize_name(value) if value else "fallback"
    if candidate not in VALID_SUMMARY_QUALITY:
        raise ValueError(
            f"calidad_resumen no soportada: {value}. Valores válidos: {', '.join(VALID_SUMMARY_QUALITY)}"
        )
    return candidate


def normalize_state(value: Optional[str]) -> str:
    candidate = normalize_name(value) if value else "nuevo"
    if candidate not in VALID_STATES:
        raise ValueError(f"estado no soportado: {value}. Valores válidos: {', '.join(VALID_STATES)}")
    return candidate


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


def normalize_metadata_title(value: Optional[str]) -> Optional[str]:
    normalized = normalize_optional_text(value)
    if not normalized or is_plain_url(normalized):
        return None
    return shorten_line(normalized, 90) or None


def normalize_metadata_description(value: Optional[str]) -> Optional[str]:
    normalized = normalize_optional_text(value)
    if not normalized or is_plain_url(normalized):
        return None
    return clean_summary_text(normalized, max_lines=2, max_length=160)


def merge_metadata(*items: Optional[ExternalMetadata]) -> Optional[ExternalMetadata]:
    merged_title: Optional[str] = None
    merged_description: Optional[str] = None
    merged_source: Optional[str] = None
    merged_url: Optional[str] = None

    for item in items:
        if item is None:
            continue
        if merged_title is None and item.title:
            merged_title = normalize_metadata_title(item.title)
        if merged_description is None and item.description:
            merged_description = normalize_metadata_description(item.description)
        if merged_source is None and item.source_kind:
            merged_source = item.source_kind
        if merged_url is None and item.resolved_url:
            merged_url = item.resolved_url

    if not any((merged_title, merged_description, merged_source, merged_url)):
        return None
    return ExternalMetadata(
        title=merged_title,
        description=merged_description,
        source_kind=merged_source,
        resolved_url=merged_url,
    )


def parse_html_metadata(html_text: str, url: str) -> Optional[ExternalMetadata]:
    def find_meta(*patterns: str) -> Optional[str]:
        for pattern in patterns:
            match = re.search(pattern, html_text, re.IGNORECASE | re.DOTALL)
            if match:
                return normalize_optional_text(unescape(match.group(1)))
        return None

    title = find_meta(
        r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']+)["\']',
        r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:title["\']',
    )
    description = find_meta(
        r'<meta[^>]+property=["\']og:description["\'][^>]+content=["\']([^"\']+)["\']',
        r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:description["\']',
        r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']+)["\']',
        r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+name=["\']description["\']',
    )

    if title is None:
        title_match = re.search(r"<title[^>]*>(.*?)</title>", html_text, re.IGNORECASE | re.DOTALL)
        if title_match:
            title = normalize_optional_text(unescape(title_match.group(1)))

    metadata = merge_metadata(
        ExternalMetadata(
            title=title,
            description=description,
            source_kind="html",
            resolved_url=url,
        )
    )
    return metadata


def fetch_url_text(url: str, timeout_seconds: float = EXTERNAL_METADATA_TIMEOUT_SECONDS) -> str:
    request = Request(url, headers={"User-Agent": "bitacora/0.2"})
    with urlopen(request, timeout=timeout_seconds) as response:
        payload = response.read(512_000)
        charset = response.headers.get_content_charset() or "utf-8"
    return payload.decode(charset, errors="replace")


def fetch_json_metadata(url: str, timeout_seconds: float = EXTERNAL_METADATA_TIMEOUT_SECONDS) -> dict:
    request = Request(url, headers={"User-Agent": "bitacora/0.2", "Accept": "application/json"})
    with urlopen(request, timeout=timeout_seconds) as response:
        payload = response.read(256_000)
        charset = response.headers.get_content_charset() or "utf-8"
    loaded = yaml.safe_load(payload.decode(charset, errors="replace"))
    if not isinstance(loaded, dict):
        raise ValueError("La respuesta de metadata externa no es un objeto JSON válido")
    return loaded


def build_oembed_url(url: str) -> Optional[str]:
    parsed = urlparse(url)
    host = (parsed.netloc or "").lower()
    if host in YOUTUBE_HOSTS:
        return f"https://www.youtube.com/oembed?format=json&url={quote_plus(url)}"
    if host in VIMEO_HOSTS:
        return f"https://vimeo.com/api/oembed.json?url={quote_plus(url)}"
    return None


def extract_external_metadata(
    url: str,
    timeout_seconds: float = EXTERNAL_METADATA_TIMEOUT_SECONDS,
    *,
    fetch_text: Optional[Callable[[str, float], str]] = None,
    fetch_json: Optional[Callable[[str, float], dict]] = None,
) -> Optional[ExternalMetadata]:
    if not normalize_optional_text(url):
        return None

    fetch_text = fetch_text or fetch_url_text
    fetch_json = fetch_json or fetch_json_metadata
    oembed_metadata: Optional[ExternalMetadata] = None

    try:
        oembed_url = build_oembed_url(url)
        if oembed_url:
            raw = fetch_json(oembed_url, timeout_seconds)
            oembed_metadata = merge_metadata(
                ExternalMetadata(
                    title=raw.get("title"),
                    description=raw.get("description") or raw.get("summary"),
                    source_kind="oembed",
                    resolved_url=url,
                )
            )
    except (TimeoutError, HTTPError, URLError, ValueError):
        oembed_metadata = None
    except Exception:
        oembed_metadata = None

    try:
        html_text = fetch_text(url, timeout_seconds)
        html_metadata = parse_html_metadata(html_text, url)
    except (TimeoutError, HTTPError, URLError, ValueError):
        html_metadata = None
    except Exception:
        html_metadata = None

    return merge_metadata(oembed_metadata, html_metadata)


def resolve_external_metadata(
    url: Optional[str],
    metadata_fetcher: Optional[Callable[[str, float], Optional[ExternalMetadata]]],
    timeout_seconds: float,
) -> Optional[ExternalMetadata]:
    normalized_url = normalize_optional_text(url)
    if not normalized_url:
        return None
    try:
        if metadata_fetcher is not None:
            return merge_metadata(metadata_fetcher(normalized_url, timeout_seconds))
        return extract_external_metadata(normalized_url, timeout_seconds)
    except Exception:
        return None


def build_metadata_summary(
    metadata: ExternalMetadata,
    *,
    project: str,
    category: str,
    source_url: Optional[str],
) -> Optional[str]:
    host = urlparse(source_url).netloc if source_url else ""
    if metadata.description:
        suffix = f"Guardado desde {host} para {project}/{category}." if host else f"Guardado para {project}/{category}."
        return clean_summary_text(f"{metadata.description}\n{suffix}")
    if metadata.title:
        if host:
            return clean_summary_text(
                f'Recurso titulado "{metadata.title}" guardado desde {host} para {project}/{category}. Pendiente de revisar.'
            )
        return clean_summary_text(
            f'Recurso titulado "{metadata.title}" guardado para {project}/{category}. Pendiente de revisar.'
        )
    return None


def build_free_text_summary(
    text: str,
    *,
    project: str,
    category: str,
    title: str,
) -> Optional[str]:
    summary = clean_summary_text(text)
    if not summary:
        return None
    summary_lines = summary.splitlines()
    if len(summary_lines) < 3:
        relevance = f"Guardado para {project}/{category}."
        if all(line.lower() != relevance.lower() for line in summary_lines):
            summary_lines.append(relevance)
    compact = "\n".join(summary_lines[:3])
    if normalize_text(compact).lower() == normalize_text(title).lower():
        return None
    return compact


def build_fallback_summary(project: str, category: str, source_url: Optional[str]) -> str:
    host = urlparse(source_url).netloc if source_url else ""
    if host:
        return f"Recurso guardado desde {host} para {project}/{category}. Pendiente de revisar."
    return f"Entrada guardada para {project}/{category}. Pendiente de enriquecer."


def make_title(
    content: str,
    source: Optional[str],
    additional_content: Optional[str],
    explicit_title: Optional[str],
    resource_type: str,
    category: str,
    external_metadata: Optional[ExternalMetadata] = None,
) -> str:
    if explicit_title:
        title = shorten_line(explicit_title, 90)
        if title:
            return title

    if external_metadata and external_metadata.title:
        title = shorten_line(external_metadata.title, 90)
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
    external_metadata: Optional[ExternalMetadata],
) -> tuple[str, str]:
    user_summary = clean_summary_text(explicit_summary or "") if explicit_summary else None
    if user_summary:
        return user_summary, "usuario"

    metadata_summary = build_metadata_summary(
        external_metadata,
        project=project,
        category=category,
        source_url=extract_first_url(source, content),
    ) if external_metadata else None
    if metadata_summary:
        return metadata_summary, "auto"

    for candidate in (additional_content, content, source):
        if is_useful_free_text(candidate):
            free_text_summary = build_free_text_summary(candidate or "", project=project, category=category, title=title)
            if free_text_summary:
                return free_text_summary, "auto"

    source_url = extract_first_url(source, content)
    return build_fallback_summary(project, category, source_url), "fallback"


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
    quality_override: Optional[str] = None,
    state: Optional[str] = None,
    metadata_fetcher: Optional[Callable[[str, float], Optional[ExternalMetadata]]] = None,
    metadata_timeout_seconds: float = EXTERNAL_METADATA_TIMEOUT_SECONDS,
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
    source_url = extract_first_url(normalized_source, normalized_content)
    external_metadata = resolve_external_metadata(
        source_url,
        metadata_fetcher=metadata_fetcher,
        timeout_seconds=metadata_timeout_seconds,
    )
    normalized_title = make_title(
        content=normalized_content,
        source=normalized_source,
        additional_content=normalized_additional,
        explicit_title=normalize_optional_text(title),
        resource_type=normalized_type,
        category=normalized_category,
        external_metadata=external_metadata,
    )
    normalized_summary, inferred_quality = make_summary(
        project=normalized_project,
        category=normalized_category,
        title=normalized_title,
        content=normalized_content,
        source=normalized_source,
        additional_content=normalized_additional,
        explicit_summary=normalize_optional_text(summary),
        external_metadata=external_metadata,
    )
    normalized_quality = normalize_summary_quality(quality_override or inferred_quality)
    normalized_state = normalize_state(state)

    for field_name, value in (
        ("contenido", normalized_content),
        ("fuente", normalized_source),
        ("nota_personal", normalized_additional),
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
        calidad_resumen=normalized_quality,
        estado=normalized_state,
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
    lines.extend(render_yaml_string("calidad_resumen", entry.calidad_resumen))
    lines.extend(render_yaml_string("estado", entry.estado))
    return "\n".join(lines)


def render_entry(entry: Entry) -> str:
    note = normalize_optional_text(entry.contenido_adicional)
    ensure_no_entry_delimiter("nota_personal", note)

    body_lines = [
        ENTRY_DELIMITER,
        "",
        "---",
        render_frontmatter(entry),
        "---",
        "",
        "**Nota personal**",
    ]
    if note:
        body_lines.append(note)
    body_lines.append("")
    return "\n".join(body_lines)


def split_entry_blocks(content: str) -> list[str]:
    return [part.strip() for part in content.split(ENTRY_DELIMITER) if part.strip()]


def extract_frontmatter(block: str) -> tuple[dict, str]:
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
    parsed = yaml.safe_load(yaml_text)
    if not isinstance(parsed, dict):
        raise ValueError("El YAML no se parseó como mapa")
    body = "\n".join(lines[end_index + 1 :]).strip()
    return parsed, body


def parse_rendered_body(body: str) -> dict[str, str]:
    values: dict[str, list[str]] = {}
    current_key: Optional[str] = None
    markers = {**LEGACY_SECTION_MARKERS, **V2_SECTION_MARKERS}
    for line in body.splitlines():
        marker = markers.get(line.strip())
        if marker:
            current_key = marker
            values.setdefault(current_key, [])
            continue
        if current_key is None:
            continue
        values[current_key].append(line)

    return {key: normalize_text("\n".join(lines)) for key, lines in values.items()}


def is_meaningful_note(candidate: Optional[str], *, source: Optional[str], title: str, summary: str) -> bool:
    normalized = normalize_optional_text(candidate)
    if not normalized:
        return False
    if source and normalized == normalize_text(source):
        return False
    if normalized == normalize_text(title):
        return False
    if normalized == normalize_text(summary):
        return False
    return True


def entry_from_block(block: str) -> Entry:
    parsed, body = extract_frontmatter(block)
    sections = parse_rendered_body(body)

    legacy_content = sections.get("contenido_markdown")
    legacy_additional = sections.get("contenido_adicional_markdown")
    note_personal = normalize_optional_text(
        sections.get("nota_personal")
        or legacy_additional
        or parsed.get("contenido_adicional")
    )

    contenido = normalize_optional_text(legacy_content) or ""
    if not note_personal and is_meaningful_note(
        contenido,
        source=str(parsed.get("fuente") or "").strip() or None,
        title=str(parsed["titulo"]),
        summary=str(parsed["resumen"]),
    ):
        note_personal = contenido

    calidad_resumen = normalize_summary_quality(parsed.get("calidad_resumen") or "fallback")
    estado = normalize_state(parsed.get("estado") or "nuevo")

    return Entry(
        entry_id=str(parsed["id"]),
        fecha=str(parsed["fecha"]),
        proyecto=str(parsed["proyecto"]),
        categoria=str(parsed["categoria"]),
        tipo=str(parsed["tipo"]),
        titulo=str(parsed["titulo"]),
        resumen=str(parsed["resumen"]),
        contenido=contenido,
        fuente=str(parsed["fuente"]).strip() if parsed.get("fuente") not in (None, "") else None,
        tags=tuple(normalize_tags(parsed.get("tags"))),
        contenido_adicional=note_personal,
        calidad_resumen=calidad_resumen,
        estado=estado,
    )


def load_project_entries_for_capture(project: str, data_dir: Path = DEFAULT_DATA_DIR) -> list[Entry]:
    file_path = data_dir / f"{normalize_name(project)}.md"
    if not file_path.exists():
        return []

    entries: list[Entry] = []
    content = file_path.read_text(encoding="utf-8")
    for block in split_entry_blocks(content):
        try:
            entries.append(entry_from_block(block))
        except Exception:
            continue
    return entries


def suggest_categories_for_project(project: str, data_dir: Path = DEFAULT_DATA_DIR, limit: int = 5) -> tuple[str, ...]:
    normalized_project = normalize_name(project)
    entries = load_project_entries_for_capture(normalized_project, data_dir=data_dir)

    counters: dict[str, int] = {}
    for entry in entries:
        counters[entry.categoria] = counters.get(entry.categoria, 0) + 1

    ordered = [
        category
        for category, _count in sorted(counters.items(), key=lambda item: (-item[1], item[0]))
    ]

    for default_category in DEFAULT_PROJECT_CATEGORIES.get(normalized_project, ()):
        if default_category not in ordered:
            ordered.append(default_category)

    return tuple(ordered[:limit])


def build_missing_project_prompt() -> str:
    return "¿En qué proyecto guardo esto?"


def build_missing_category_prompt(project: str, suggestions: Sequence[str]) -> str:
    normalized_project = normalize_name(project)
    if suggestions:
        return (
            f"¿Qué categoría le pongo en {normalized_project}? "
            f"Puedes usar una de estas: {', '.join(suggestions)}."
        )
    return f"¿Qué categoría le pongo en {normalized_project}?"


def capture_entry(
    *,
    project: Optional[str],
    category: Optional[str],
    content: str = "",
    data_dir: Path = DEFAULT_DATA_DIR,
    resource_type: Optional[str] = None,
    title: Optional[str] = None,
    summary: Optional[str] = None,
    source: Optional[str] = None,
    tags: Optional[Sequence[str]] = None,
    additional_content: Optional[str] = None,
    metadata_fetcher: Optional[Callable[[str, float], Optional[ExternalMetadata]]] = None,
    metadata_timeout_seconds: float = EXTERNAL_METADATA_TIMEOUT_SECONDS,
) -> CaptureOutcome:
    normalized_project = normalize_optional_text(project)
    if not normalized_project:
        return CaptureOutcome(status="needs_project", prompt=build_missing_project_prompt())

    normalized_category = normalize_optional_text(category)
    if not normalized_category:
        suggestions = suggest_categories_for_project(normalized_project, data_dir=data_dir)
        return CaptureOutcome(
            status="needs_category",
            prompt=build_missing_category_prompt(normalized_project, suggestions),
            suggested_categories=suggestions,
        )

    entry, file_path = append_entry(
        project=normalized_project,
        category=normalized_category,
        content=content,
        data_dir=data_dir,
        resource_type=resource_type,
        title=title,
        summary=summary,
        source=source,
        tags=tags,
        additional_content=additional_content,
        metadata_fetcher=metadata_fetcher,
        metadata_timeout_seconds=metadata_timeout_seconds,
    )
    return CaptureOutcome(status="saved", prompt=build_confirmation(entry, file_path), entry=entry, file_path=file_path)


def find_duplicate_url(file_path: Path, candidate_urls: Sequence[str]) -> Optional[DuplicateMatch]:
    if not candidate_urls or not file_path.exists():
        return None

    content = file_path.read_text(encoding="utf-8")
    for block in split_entry_blocks(content):
        try:
            entry = entry_from_block(block)
        except Exception:
            continue
        existing_urls = set(extract_urls(entry.fuente, entry.contenido, entry.contenido_adicional))
        for candidate_url in candidate_urls:
            if candidate_url in existing_urls:
                return DuplicateMatch(duplicate_url=candidate_url, entry=entry, file_path=file_path)
    return None


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
    metadata_fetcher: Optional[Callable[[str, float], Optional[ExternalMetadata]]] = None,
    metadata_timeout_seconds: float = EXTERNAL_METADATA_TIMEOUT_SECONDS,
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
        metadata_fetcher=metadata_fetcher,
        metadata_timeout_seconds=metadata_timeout_seconds,
    )
    data_dir.mkdir(parents=True, exist_ok=True)
    file_path = data_dir / f"{entry.proyecto}.md"

    duplicate_match = find_duplicate_url(file_path, extract_urls(entry.fuente, entry.contenido, entry.contenido_adicional))
    if duplicate_match:
        raise DuplicateEntryError(duplicate_match)

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
    extras: list[str] = [f"calidad_resumen={entry.calidad_resumen}", f"estado={entry.estado}"]
    if entry.fuente:
        extras.append("con fuente")
    if entry.tags:
        extras.append(f"{len(entry.tags)} tags")
    if entry.contenido_adicional:
        extras.append("con nota personal")
    suffix = f" [{', '.join(extras)}]" if extras else ""
    return (
        f"Guardado correctamente en {entry.proyecto}/{entry.categoria}: {entry.titulo} ({entry.tipo})"
        f"{suffix}. id={entry.entry_id}. archivo={file_path}"
    )


def atomic_write(
    file_path: Path,
    content: str,
    *,
    before_replace: Optional[Callable[[Path], None]] = None,
) -> None:
    file_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path: Optional[Path] = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="\n", dir=file_path.parent, delete=False) as handle:
            handle.write(content)
            temp_path = Path(handle.name)
        if before_replace is not None:
            before_replace(temp_path)
        temp_path.replace(file_path)
        temp_path = None
    finally:
        if temp_path is not None and temp_path.exists():
            temp_path.unlink()


def backup_project_file(file_path: Path) -> Path:
    backup_path = file_path.with_name(f"{file_path.name}.bak")
    backup_path.write_text(file_path.read_text(encoding="utf-8"), encoding="utf-8", newline="\n")
    return backup_path


def migrate_entry_to_v0_2(entry: Entry) -> Entry:
    return Entry(
        entry_id=entry.entry_id,
        fecha=entry.fecha,
        proyecto=entry.proyecto,
        categoria=entry.categoria,
        tipo=entry.tipo,
        titulo=entry.titulo,
        resumen=entry.resumen,
        contenido=entry.contenido,
        fuente=entry.fuente,
        tags=entry.tags,
        contenido_adicional=entry.contenido_adicional,
        calidad_resumen=normalize_summary_quality(entry.calidad_resumen or "fallback"),
        estado=normalize_state(entry.estado or "nuevo"),
    )


def build_project_content(entries: Sequence[Entry]) -> str:
    rendered_entries = [render_entry(entry) for entry in entries]
    final_content = "\n".join(rendered_entries)
    if final_content and not final_content.endswith("\n"):
        final_content += "\n"
    return final_content


def migrate_project_file(
    project: str,
    data_dir: Path = DEFAULT_DATA_DIR,
    *,
    create_backup: bool = True,
    before_replace: Optional[Callable[[Path], None]] = None,
) -> MigrationResult:
    normalized_project = normalize_name(project)
    file_path = data_dir / f"{normalized_project}.md"
    if not file_path.exists():
        raise ValueError(f"No existe el archivo del proyecto {normalized_project}: {file_path}")

    original_content = file_path.read_text(encoding="utf-8")
    raw_blocks = split_entry_blocks(original_content)
    if not raw_blocks:
        raise ValueError(f"El archivo del proyecto {normalized_project} está vacío; no hay entradas que migrar")

    migrated_entries = [migrate_entry_to_v0_2(entry_from_block(block)) for block in raw_blocks]
    backup_path = backup_project_file(file_path) if create_backup else None
    final_content = build_project_content(migrated_entries)
    atomic_write(file_path, final_content, before_replace=before_replace)
    return MigrationResult(
        project=normalized_project,
        file_path=file_path,
        backup_path=backup_path,
        migrated_entries=migrated_entries,
    )


def update_existing_entry(
    project: str,
    *,
    entry_id: Optional[str] = None,
    source_url: Optional[str] = None,
    data_dir: Path = DEFAULT_DATA_DIR,
    tags: Optional[Sequence[str]] = None,
    summary: Optional[str] = None,
    additional_content: Optional[str] = None,
) -> tuple[Entry, Path]:
    normalized_project = normalize_name(project)
    file_path = data_dir / f"{normalized_project}.md"
    if not file_path.exists():
        raise ValueError(f"No existe el archivo del proyecto {normalized_project}: {file_path}")
    if not entry_id and not source_url:
        raise ValueError("Debe indicarse --update-entry-id o --update-source-url")

    original_content = file_path.read_text(encoding="utf-8")
    raw_blocks = split_entry_blocks(original_content)
    updated_blocks: list[str] = []
    updated_entry: Optional[Entry] = None

    normalized_summary = normalize_optional_text(summary)
    normalized_additional = normalize_optional_text(additional_content)
    normalized_new_tags = normalize_tags(tags)

    for block in raw_blocks:
        entry = entry_from_block(block)
        existing_urls = set(extract_urls(entry.fuente, entry.contenido, entry.contenido_adicional))
        is_target = (entry_id and entry.entry_id == entry_id.strip()) or (source_url and source_url.strip() in existing_urls)
        if not is_target:
            updated_blocks.append(render_entry(entry))
            continue

        merged_tags = entry.tags
        if normalized_new_tags:
            merged_tags = normalize_tags([*entry.tags, *normalized_new_tags])

        new_summary = normalized_summary or entry.resumen
        new_note = normalized_additional if normalized_additional is not None else entry.contenido_adicional
        updated_quality = entry.calidad_resumen
        if normalized_summary is not None:
            updated_quality = "usuario"

        updated_entry = Entry(
            entry_id=entry.entry_id,
            fecha=entry.fecha,
            proyecto=entry.proyecto,
            categoria=entry.categoria,
            tipo=entry.tipo,
            titulo=entry.titulo,
            resumen=new_summary,
            contenido=entry.contenido,
            fuente=entry.fuente,
            tags=merged_tags,
            contenido_adicional=new_note,
            calidad_resumen=updated_quality,
            estado=entry.estado,
        )
        updated_blocks.append(render_entry(updated_entry))

    if updated_entry is None:
        target = entry_id.strip() if entry_id else source_url.strip()
        raise ValueError(f"No se encontró ninguna entrada para actualizar con {target}")

    final_content = "\n".join(updated_blocks)
    if final_content and not final_content.endswith("\n"):
        final_content += "\n"
    atomic_write(file_path, final_content)
    return updated_entry, file_path


def build_update_confirmation(entry: Entry, file_path: Path) -> str:
    changes: list[str] = []
    if entry.tags:
        changes.append(f"tags={', '.join(entry.tags)}")
    if entry.contenido_adicional:
        changes.append("nota personal actualizada")
    if entry.resumen:
        changes.append(f"calidad_resumen={entry.calidad_resumen}")
    details = f" ({'; '.join(changes)})" if changes else ""
    return f"Entrada actualizada sin duplicar: id={entry.entry_id} en {file_path}{details}"


def build_migration_confirmation(result: MigrationResult) -> str:
    backup_text = f" backup={result.backup_path}" if result.backup_path else ""
    return (
        f"Migración v0.2 completada para {result.project}: {len(result.migrated_entries)} entradas."
        f" archivo={result.file_path}{backup_text}"
    )


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Guardar, actualizar o migrar entradas de bitácora")
    parser.add_argument("--project", help="Nombre del proyecto")
    parser.add_argument("--category", help="Categoría de la entrada al guardar")
    parser.add_argument("--content", default="", help="Contenido o recurso del usuario")
    parser.add_argument("--type", dest="resource_type", help="Tipo explícito: link, video, documento, nota, idea, referencia")
    parser.add_argument("--title", help="Título explícito de la entrada")
    parser.add_argument("--summary", help="Resumen explícito o nuevo resumen")
    parser.add_argument("--source", help="URL o descripción del origen")
    parser.add_argument("--tag", dest="tags", action="append", default=[], help="Tag opcional, repetir para varios")
    parser.add_argument("--additional-content", help="Nota libre adicional del usuario")
    parser.add_argument("--update-entry-id", help="Actualizar una entrada existente por id")
    parser.add_argument("--update-source-url", help="Actualizar una entrada existente localizándola por URL exacta")
    parser.add_argument("--migrate-project", action="store_true", help="Migrar el archivo del proyecto al formato v0.2")
    parser.add_argument("--data-dir", default=str(DEFAULT_DATA_DIR), help="Directorio de datos")
    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv)
    data_dir = Path(args.data_dir)
    update_mode = bool(args.update_entry_id or args.update_source_url)

    try:
        if args.migrate_project:
            if not args.project:
                raise ValueError("--project es obligatorio al migrar un proyecto")
            result = migrate_project_file(project=args.project, data_dir=data_dir, create_backup=True)
            print(build_migration_confirmation(result))
            return 0

        if update_mode:
            if not args.project:
                raise ValueError("--project es obligatorio al actualizar una entrada")
            entry, file_path = update_existing_entry(
                project=args.project,
                entry_id=args.update_entry_id,
                source_url=args.update_source_url,
                data_dir=data_dir,
                tags=args.tags,
                summary=args.summary,
                additional_content=args.additional_content,
            )
            print(build_update_confirmation(entry, file_path))
            return 0

        outcome = capture_entry(
            project=args.project,
            category=args.category,
            content=args.content,
            data_dir=data_dir,
            resource_type=args.resource_type,
            title=args.title,
            summary=args.summary,
            source=args.source,
            tags=args.tags,
            additional_content=args.additional_content,
        )
        if outcome.status != "saved":
            print(outcome.prompt)
            return 2

        entry = outcome.entry
        file_path = outcome.file_path
    except DuplicateEntryError as exc:  # pragma: no cover
        match = exc.match
        print(
            "ERROR: URL duplicada detectada. "
            f"La URL {match.duplicate_url} ya existe en la entrada {match.entry.entry_id} "
            f"de {match.entry.proyecto}/{match.entry.categoria}. "
            "No se ha creado una entrada nueva. "
            "Si quieres actualizarla de forma explícita, usa --update-entry-id o --update-source-url.",
            file=sys.stderr,
        )
        return 1
    except Exception as exc:  # pragma: no cover
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(build_confirmation(entry, file_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
