#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
WORK_DIR = SKILL_DIR / ".tmp_phase8"
DATA_DIR = WORK_DIR / "data"

sys.path.insert(0, str(SCRIPT_DIR))

from read_entries import list_entries, search_entries  # noqa: E402
from save_entry import CaptureOutcome, DuplicateEntryError, capture_entry, append_entry  # noqa: E402


def count_blocks(file_path: Path) -> int:
    if not file_path.exists():
        return 0
    content = file_path.read_text(encoding="utf-8")
    return sum(1 for part in content.split("---entry---") if part.strip())


def no_metadata(_url: str, _timeout: float):
    return None


def main() -> int:
    if WORK_DIR.exists():
        shutil.rmtree(WORK_DIR)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    try:
        seed_1, camper_path = append_entry(
            project="camper",
            category="electricidad",
            content="Esquema de instalación 12V con fusibles accesibles.",
            data_dir=DATA_DIR,
            metadata_fetcher=no_metadata,
        )
        seed_2, _ = append_entry(
            project="camper",
            category="aislamiento",
            content="Usar XPS de alta densidad en suelo y laterales.",
            data_dir=DATA_DIR,
            metadata_fetcher=no_metadata,
        )
        initial_blocks = count_blocks(camper_path)

        # Test 1: faltante de proyecto con pregunta obligatoria y sin guardado parcial
        missing_project = capture_entry(
            project=None,
            category="aislamiento",
            content="https://example.com/guia-xps",
            source="https://example.com/guia-xps",
            data_dir=DATA_DIR,
            metadata_fetcher=no_metadata,
        )
        assert missing_project.status == "needs_project"
        assert missing_project.entry is None and missing_project.file_path is None
        assert missing_project.prompt == "¿En qué proyecto guardo esto?"
        assert count_blocks(camper_path) == initial_blocks, "Se guardó algo pese a faltar el proyecto"

        # Test 2: faltante de categoría con propuesta y sin guardado parcial
        missing_category = capture_entry(
            project="camper",
            category=None,
            content="https://example.com/guia-electrica",
            source="https://example.com/guia-electrica",
            data_dir=DATA_DIR,
            metadata_fetcher=no_metadata,
        )
        assert missing_category.status == "needs_category"
        assert missing_category.entry is None and missing_category.file_path is None
        assert "¿Qué categoría le pongo en camper?" in missing_category.prompt
        assert "electricidad" in missing_category.suggested_categories
        assert "aislamiento" in missing_category.suggested_categories
        assert count_blocks(camper_path) == initial_blocks, "Se guardó algo pese a faltar la categoría"

        # Test 3: guardado normal con proyecto y categoría solo se completa al final del flujo
        completed = capture_entry(
            project="camper",
            category="ventilacion",
            content="Ventana abatible con mosquitera para techo elevable.",
            data_dir=DATA_DIR,
            metadata_fetcher=no_metadata,
        )
        assert completed.status == "saved"
        assert completed.entry is not None and completed.file_path == camper_path
        assert completed.entry.proyecto == "camper"
        assert completed.entry.categoria == "ventilacion"
        assert count_blocks(camper_path) == initial_blocks + 1, "El guardado final no añadió exactamente una entrada"

        # Test 4: el CLI pide proyecto o categoría en vez de guardar parcialmente
        missing_project_run = subprocess.run(
            [
                sys.executable,
                str(SCRIPT_DIR / "save_entry.py"),
                "--content",
                "Idea rápida para módulo auxiliar",
                "--data-dir",
                str(DATA_DIR),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        assert missing_project_run.returncode == 2
        assert "¿En qué proyecto guardo esto?" in missing_project_run.stdout

        missing_category_run = subprocess.run(
            [
                sys.executable,
                str(SCRIPT_DIR / "save_entry.py"),
                "--project",
                "camper",
                "--content",
                "Idea rápida para módulo auxiliar",
                "--data-dir",
                str(DATA_DIR),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        assert missing_category_run.returncode == 2
        assert "¿Qué categoría le pongo en camper?" in missing_category_run.stdout
        assert count_blocks(camper_path) == initial_blocks + 1, "El CLI dejó guardado parcial al pedir categoría"

        # Regresión mínima: guardado normal, lectura, búsqueda y deduplicación básica siguen funcionando
        listing = list_entries("camper", DATA_DIR)
        assert listing.total_entries == 3, "El listado global dejó de contar correctamente tras la Fase 8"
        search = search_entries("camper", "mosquitera", DATA_DIR)
        assert len(search.matched_hits) == 1, "La búsqueda dejó de encontrar la entrada recién guardada"
        assert search.matched_hits[0].entry.entry_id == completed.entry.entry_id

        duplicate_seen = False
        try:
            capture_entry(
                project="camper",
                category="ventilacion",
                content="https://example.com/guia-ventana",
                source="https://example.com/guia-ventana",
                data_dir=DATA_DIR,
                metadata_fetcher=no_metadata,
            )
            capture_entry(
                project="camper",
                category="ventilacion",
                content="https://example.com/guia-ventana",
                source="https://example.com/guia-ventana",
                data_dir=DATA_DIR,
                metadata_fetcher=no_metadata,
            )
        except DuplicateEntryError:
            duplicate_seen = True
        assert duplicate_seen, "La deduplicación básica dejó de bloquear la URL exacta duplicada"

        print("OK: fase 8 tests pasados")
        return 0
    finally:
        if WORK_DIR.exists():
            shutil.rmtree(WORK_DIR)


if __name__ == "__main__":
    raise SystemExit(main())
