#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import yaml

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
WORK_DIR = SKILL_DIR / ".tmp_phase21"
DATA_DIR = WORK_DIR / "data"
SKILL_MD = SKILL_DIR / "SKILL.md"

sys.path.insert(0, str(SCRIPT_DIR))

from read_entries import build_output, get_entry_by_id, list_entries  # noqa: E402
from save_entry import build_confirmation, capture_entry, split_entry_blocks  # noqa: E402


def no_metadata(_url: str, _timeout: float):
    return None


def parse_skill_file(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    parts = text.split("---", 2)
    assert len(parts) >= 3, "SKILL.md debe incluir frontmatter YAML"
    frontmatter = yaml.safe_load(parts[1])
    assert isinstance(frontmatter, dict), "El frontmatter debe parsearse como mapa YAML"
    return frontmatter, parts[2]


def main() -> int:
    if WORK_DIR.exists():
        shutil.rmtree(WORK_DIR)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    try:
        # Test 1: SKILL.md actualizado con reglas conversacionales y modo técnico explícito
        frontmatter, body = parse_skill_file(SKILL_MD)
        assert frontmatter.get("name") == "bitacora"
        description = str(frontmatter.get("description") or "")
        assert "modo técnico explícito" in description or "modo tecnico explicito" in description.lower()
        assert "duplic" in description.lower()
        lowered_body = body.lower()
        for expected in (
            "preguntar siempre primero por el proyecto si falta",
            "no guardar nada si falta la categoría",
            "no crear un duplicado",
            "entrada queda pobre",
            "modo técnico",
        ):
            assert expected.lower() in lowered_body, f"Falta en SKILL.md: {expected}"

        # Test 2: faltante de proyecto con pregunta obligatoria
        missing_project = capture_entry(
            project=None,
            category="electricidad",
            content="https://example.com/inversor",
            source="https://example.com/inversor",
            data_dir=DATA_DIR,
            metadata_fetcher=no_metadata,
            human_output=True,
        )
        assert missing_project.status == "needs_project"
        assert missing_project.prompt == "¿En qué proyecto guardo esto?"
        assert not (DATA_DIR / "camper.md").exists(), "No debe guardarse nada si falta el proyecto"

        # Preparar una entrada válida para sugerencias y duplicados
        saved = capture_entry(
            project="camper",
            category="electricidad",
            content="https://example.com/inversor-12v",
            source="https://example.com/inversor-12v",
            data_dir=DATA_DIR,
            metadata_fetcher=no_metadata,
            human_output=True,
        )
        assert saved.status == "saved"
        assert saved.entry is not None and saved.file_path is not None
        assert len(split_entry_blocks(saved.file_path.read_text(encoding="utf-8"))) == 1

        # Test 3: faltante de categoría con pregunta o propuesta
        missing_category = capture_entry(
            project="camper",
            category=None,
            content="Guía sobre cableado limpio.",
            data_dir=DATA_DIR,
            metadata_fetcher=no_metadata,
            human_output=True,
        )
        assert missing_category.status == "needs_category"
        assert "¿Qué categoría le pongo en camper?" in missing_category.prompt
        assert "electricidad" in missing_category.prompt
        assert "electricidad" in missing_category.suggested_categories
        assert len(split_entry_blocks(saved.file_path.read_text(encoding="utf-8"))) == 1, "No debe guardarse nada si falta categoría"

        # Test 4: duplicado con respuesta conversacional correcta
        duplicate = capture_entry(
            project="camper",
            category="electricidad",
            content="Nueva observación sobre el inversor.",
            source="https://example.com/inversor-12v",
            data_dir=DATA_DIR,
            metadata_fetcher=no_metadata,
            human_output=True,
            duplicate_strategy="offer",
        )
        assert duplicate.status == "duplicate"
        assert "no he creado un duplicado" in duplicate.prompt.lower()
        assert "fusionar" in duplicate.prompt.lower()
        assert len(split_entry_blocks(saved.file_path.read_text(encoding="utf-8"))) == 1

        # Test 5: modo técnico explícito y regresión mínima de guardado/lectura
        technical_confirmation = build_confirmation(saved.entry, saved.file_path, technical=True)
        human_confirmation = build_confirmation(saved.entry, saved.file_path, technical=False)
        assert "id=" in technical_confirmation and "archivo=" in technical_confirmation
        assert "id=" not in human_confirmation and "archivo=" not in human_confirmation

        lookup = get_entry_by_id("camper", saved.entry.entry_id, DATA_DIR)
        assert lookup.entry is not None
        listing = list_entries("camper", DATA_DIR)
        assert listing.total_entries == 1
        human_listing = build_output(listing, technical=False)
        assert saved.entry.entry_id not in human_listing

        technical_cli = subprocess.run(
            [
                sys.executable,
                str(SCRIPT_DIR / "read_entries.py"),
                "--project",
                "camper",
                "--technical",
                "--data-dir",
                str(DATA_DIR),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        assert technical_cli.returncode == 0
        assert saved.entry.entry_id in technical_cli.stdout
        assert saved.entry.fecha in technical_cli.stdout

        print("OK: fase 21 tests pasados")
        return 0
    finally:
        if WORK_DIR.exists():
            shutil.rmtree(WORK_DIR)


if __name__ == "__main__":
    raise SystemExit(main())
