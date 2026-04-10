#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
WORK_DIR = SKILL_DIR / ".tmp_phase11"
DATA_DIR = WORK_DIR / "data"

sys.path.insert(0, str(SCRIPT_DIR))

from read_entries import build_entry_output, build_output, build_search_output, get_entry_by_id, list_entries, search_entries  # noqa: E402
from save_entry import capture_entry, format_visible_date, split_entry_blocks  # noqa: E402


def no_metadata(_url: str, _timeout: float):
    return None


def main() -> int:
    if WORK_DIR.exists():
        shutil.rmtree(WORK_DIR)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    try:
        # Test 1: confirmación de guardado limpia, sin rutas ni id por defecto
        saved = capture_entry(
            project="camper",
            category="electricidad",
            content="https://example.com/cableado-limpio",
            source="https://example.com/cableado-limpio",
            data_dir=DATA_DIR,
            metadata_fetcher=no_metadata,
            human_output=True,
        )
        assert saved.status == "saved"
        assert saved.entry is not None and saved.file_path is not None
        file_text = saved.file_path.read_text(encoding="utf-8")
        assert len(split_entry_blocks(file_text)) == 1, "La entrada no quedó guardada en disco"
        assert "Guardado en Camper, Electricidad:" in saved.prompt
        assert "id=" not in saved.prompt
        assert "archivo=" not in saved.prompt
        assert str(saved.file_path) not in saved.prompt

        # Añadir una segunda entrada para probar listado y búsqueda humana
        second = capture_entry(
            project="camper",
            category="fijaciones-estructura",
            content="Usar remaches roscados M6 con arandela ancha para guías laterales.",
            data_dir=DATA_DIR,
            metadata_fetcher=no_metadata,
            human_output=True,
        )
        assert second.status == "saved"
        assert second.entry is not None
        file_text = (DATA_DIR / "camper.md").read_text(encoding="utf-8")
        assert len(split_entry_blocks(file_text)) == 2, "El archivo no contiene exactamente 2 entradas tras el setup"

        # Test 2: fecha humanizada en la salida visible
        listing = list_entries("camper", DATA_DIR)
        assert listing.total_entries == 2
        human_listing = build_output(listing, technical=False)
        assert format_visible_date(saved.entry.fecha) in human_listing
        assert saved.entry.fecha not in human_listing

        # Test 3: ausencia de ID en listado resumido visible
        assert "id:" not in human_listing
        assert saved.entry.entry_id not in human_listing
        assert second.entry.entry_id not in human_listing

        # Test 4: lenguaje natural en mensajes de búsqueda
        search = search_entries("camper", "remaches", DATA_DIR)
        assert len(search.matched_hits) == 1, "La búsqueda dejó de encontrar la entrada esperada"
        human_search = build_search_output(search, technical=False)
        assert "Aparece en el resumen" in human_search or "Aparece en la nota personal" in human_search or "Aparece en el título" in human_search
        assert "--entry-id" not in human_search
        assert "contenido_adicional" not in human_search
        assert "field_name" not in human_search
        assert "Si quieres, te muestro la entrada completa." in human_search

        # Test 5: regresión mínima, lectura/búsqueda siguen funcionando y la vista técnica sigue disponible
        lookup = get_entry_by_id("camper", second.entry.entry_id, DATA_DIR)
        assert lookup.entry is not None
        technical_entry = build_entry_output(lookup, technical=True)
        assert f"ID: {second.entry.entry_id}" in technical_entry
        assert f"Categoría: {second.entry.categoria}" in technical_entry

        cli_listing = subprocess.run(
            [
                sys.executable,
                str(SCRIPT_DIR / "read_entries.py"),
                "--project",
                "camper",
                "--data-dir",
                str(DATA_DIR),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        assert cli_listing.returncode == 0
        assert "id:" not in cli_listing.stdout
        assert saved.entry.fecha not in cli_listing.stdout
        assert "Camper:" in cli_listing.stdout

        print("OK: fase 11 tests pasados")
        return 0
    finally:
        if WORK_DIR.exists():
            shutil.rmtree(WORK_DIR)


if __name__ == "__main__":
    raise SystemExit(main())
