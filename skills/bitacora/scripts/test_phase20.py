#!/usr/bin/env python3
from __future__ import annotations

import shutil
import sys
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
WORK_DIR = SKILL_DIR / ".tmp_phase20"
DATA_DIR = WORK_DIR / "data"

sys.path.insert(0, str(SCRIPT_DIR))

from read_entries import get_entry_by_id, list_entries, search_entries  # noqa: E402
from save_entry import capture_entry, edit_existing_entry  # noqa: E402


def no_metadata(_url: str, _timeout: float):
    return None


def main() -> int:
    if WORK_DIR.exists():
        shutil.rmtree(WORK_DIR)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    try:
        original = capture_entry(
            project="camper",
            category="electricidad",
            content="https://example.com/esquema-12v",
            source="https://example.com/esquema-12v",
            tags=["12v", "fusibles"],
            additional_content="Revisar ubicación del fusible principal antes de cerrar mueble.",
            data_dir=DATA_DIR,
            metadata_fetcher=no_metadata,
            human_output=True,
        )
        assert original.status == "saved"
        assert original.entry is not None
        time.sleep(0.02)

        # Tests 1, 2 y 3: actualización de categoría, título, tipo y fuente sin tocar campos inmutables
        edited, edited_path = edit_existing_entry(
            project="camper",
            entry_id=original.entry.entry_id,
            data_dir=DATA_DIR,
            category="fijaciones-estructura",
            resource_type="documento",
            title="Esquema 12V con fijaciones del panel lateral",
            source="https://example.com/manuales/esquema-12v.pdf",
        )
        assert edited_path.exists()
        assert edited.categoria == "fijaciones-estructura"
        assert edited.tipo == "documento"
        assert edited.titulo == "Esquema 12V con fijaciones del panel lateral"
        assert edited.fuente == "https://example.com/manuales/esquema-12v.pdf"
        assert edited.entry_id == original.entry.entry_id, "El id es inmutable"
        assert edited.fecha == original.entry.fecha, "La fecha original es inmutable"

        # Test 4: fecha_actualizacion cuando procede y preservación de campos opcionales
        assert edited.fecha_actualizacion is not None, "La edición completa debe registrar fecha_actualizacion"
        lookup = get_entry_by_id("camper", original.entry.entry_id, DATA_DIR)
        assert lookup.entry is not None
        assert lookup.entry.fecha_actualizacion == edited.fecha_actualizacion
        assert lookup.entry.tags == ["12v", "fusibles"], "Los tags opcionales no deben perderse"
        assert lookup.entry.contenido_adicional == "Revisar ubicación del fusible principal antes de cerrar mueble."

        # Test 5: el archivo sigue siendo mantenible y la entrada editada se recupera por su nueva forma
        by_category = list_entries("camper", DATA_DIR, category="fijaciones-estructura")
        assert len(by_category.matched_entries) == 1
        assert by_category.matched_entries[0].entry_id == original.entry.entry_id

        title_search = search_entries("camper", "panel lateral", DATA_DIR)
        assert len(title_search.matched_hits) == 1
        assert title_search.matched_hits[0].entry.entry_id == original.entry.entry_id

        # Regresión mínima: lectura, búsqueda y deduplicación siguen funcionando con la nueva fuente
        duplicate = capture_entry(
            project="camper",
            category="fijaciones-estructura",
            content="https://example.com/manuales/esquema-12v.pdf",
            source="https://example.com/manuales/esquema-12v.pdf",
            data_dir=DATA_DIR,
            metadata_fetcher=no_metadata,
            human_output=True,
            duplicate_strategy="offer",
        )
        assert duplicate.status == "duplicate"
        assert duplicate.duplicate_match is not None
        assert duplicate.duplicate_match.entry.entry_id == original.entry.entry_id

        print("OK: fase 20 tests pasados")
        return 0
    finally:
        if WORK_DIR.exists():
            shutil.rmtree(WORK_DIR)


if __name__ == "__main__":
    raise SystemExit(main())
