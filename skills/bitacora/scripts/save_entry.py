#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import re
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

ROOT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DATA_DIR = ROOT_DIR / "data"
ENTRY_DELIMITER = "---entry---"


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


def normalize_text(value: str) -> str:
    value = value.replace("\r\n", "\n").replace("\r", "\n")
    return value.strip()


def normalize_name(value: str) -> str:
    value = normalize_text(value).lower()
    value = re.sub(r"\s+", "-", value)
    value = re.sub(r"[^a-z0-9_-]", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    if not value:
        raise ValueError("El nombre no puede quedar vacío")
    return value


def infer_type(content: str) -> str:
    lowered = content.lower()
    if "youtube.com" in lowered or "youtu.be" in lowered or "vimeo.com" in lowered:
        return "video"
    if re.search(r"https?://", lowered):
        return "link"
    return "nota"


def make_title(content: str) -> str:
    single_line = " ".join(normalize_text(content).splitlines()).strip()
    if not single_line:
        return "Entrada sin título"
    if len(single_line) <= 72:
        return single_line
    return single_line[:69].rstrip() + "..."


def make_summary(content: str) -> str:
    single_line = " ".join(normalize_text(content).splitlines()).strip()
    if not single_line:
        return "Entrada guardada en bitácora."
    if len(single_line) <= 160:
        return single_line
    return single_line[:157].rstrip() + "..."


def generate_entry(project: str, category: str, content: str) -> Entry:
    now = datetime.now(timezone.utc)
    entry_id = f"entry-{time.time_ns() // 1_000_000}"
    normalized_content = normalize_text(content)
    return Entry(
        entry_id=entry_id,
        fecha=now.isoformat(timespec="milliseconds").replace("+00:00", "Z"),
        proyecto=normalize_name(project),
        categoria=normalize_name(category),
        tipo=infer_type(normalized_content),
        titulo=make_title(normalized_content),
        resumen=make_summary(normalized_content),
        contenido=normalized_content,
    )


def yaml_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def render_entry(entry: Entry) -> str:
    body_lines = [
        ENTRY_DELIMITER,
        "",
        "---",
        f'id: "{yaml_escape(entry.entry_id)}"',
        f'fecha: "{yaml_escape(entry.fecha)}"',
        f'proyecto: "{yaml_escape(entry.proyecto)}"',
        f'categoria: "{yaml_escape(entry.categoria)}"',
        f'tipo: "{yaml_escape(entry.tipo)}"',
        f'titulo: "{yaml_escape(entry.titulo)}"',
        f'resumen: "{yaml_escape(entry.resumen)}"',
        "---",
        "",
        "**Título**",
        entry.titulo,
        "",
        "**Resumen**",
        entry.resumen,
        "",
        "**Contenido**",
        entry.contenido or "(sin contenido)",
        "",
    ]
    return "\n".join(body_lines)


def append_entry(project: str, category: str, content: str, data_dir: Path = DEFAULT_DATA_DIR) -> tuple[Entry, Path]:
    entry = generate_entry(project, category, content)
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
    return (
        f"Guardado en {entry.proyecto}/{entry.categoria}: {entry.titulo} "
        f"({entry.tipo}) -> {file_path}"
    )


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Guardar una entrada mínima de bitácora")
    parser.add_argument("--project", required=True, help="Nombre del proyecto")
    parser.add_argument("--category", required=True, help="Categoría de la entrada")
    parser.add_argument("--content", required=True, help="Contenido o recurso del usuario")
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
        )
    except Exception as exc:  # pragma: no cover
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(build_confirmation(entry, file_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
