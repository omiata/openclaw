#!/usr/bin/env python3
from __future__ import annotations

import shutil
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
WORK_DIR = SKILL_DIR / ".tmp_phase22"
DATA_DIR = WORK_DIR / "data"
SKILL_MD = SKILL_DIR / "SKILL.md"

sys.path.insert(0, str(SCRIPT_DIR))

from read_entries import get_entry_by_id, list_entries, search_entries  # noqa: E402
from save_entry import capture_entry, split_entry_blocks, update_existing_entry  # noqa: E402


def no_metadata(_url: str, _timeout: float):
    return None


def main() -> int:
    if WORK_DIR.exists():
        shutil.rmtree(WORK_DIR)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    try:
        source_url = "https://example.com/placa-solar"

        # Test 1: no guardar nota redundante si es la misma URL de la fuente
        saved = capture_entry(
            project="camper",
            category="electricidad",
            content=source_url,
            source=source_url,
            additional_content=source_url,
            data_dir=DATA_DIR,
            metadata_fetcher=no_metadata,
            human_output=True,
        )
        assert saved.status == "saved"
        assert saved.entry is not None and saved.file_path is not None
        assert saved.entry.contenido_adicional is None, "La URL repetida no debe persistirse como nota personal"
        lookup = get_entry_by_id("camper", saved.entry.entry_id, DATA_DIR)
        assert lookup.entry is not None
        assert lookup.entry.contenido_adicional is None
        assert len(split_entry_blocks(saved.file_path.read_text(encoding="utf-8"))) == 1

        # Test 2: una limpieza posterior no debe borrar información útil ya existente
        enriched = capture_entry(
            project="camper",
            category="electricidad",
            content="https://example.com/regulador-mppt",
            source="https://example.com/regulador-mppt",
            title="Comparativa de reguladores MPPT",
            summary="Recurso para revisar opciones MPPT antes de cerrar el sistema solar.",
            additional_content="Medir hueco bajo asiento antes de comprar y revisar ventilación.",
            data_dir=DATA_DIR,
            metadata_fetcher=no_metadata,
            human_output=True,
        )
        assert enriched.status == "saved"
        assert enriched.entry is not None
        updated, _ = update_existing_entry(
            project="camper",
            entry_id=enriched.entry.entry_id,
            additional_content="https://example.com/regulador-mppt",
            data_dir=DATA_DIR,
        )
        assert updated.contenido_adicional == "Medir hueco bajo asiento antes de comprar y revisar ventilación.", "La limpieza no debe borrar una nota útil previa"
        lookup_enriched = get_entry_by_id("camper", enriched.entry.entry_id, DATA_DIR)
        assert lookup_enriched.entry is not None
        assert lookup_enriched.entry.contenido_adicional == updated.contenido_adicional

        # Test 3: la fusión sobre duplicado no debe introducir una URL vacía de valor como nota
        merged = capture_entry(
            project="camper",
            category="electricidad",
            content=source_url,
            source=source_url,
            data_dir=DATA_DIR,
            metadata_fetcher=no_metadata,
            human_output=True,
            duplicate_strategy="merge",
        )
        assert merged.status == "merged"
        merged_lookup = get_entry_by_id("camper", saved.entry.entry_id, DATA_DIR)
        assert merged_lookup.entry is not None
        assert merged_lookup.entry.contenido_adicional is None, "La fusión no debe añadir una nota redundante con la misma URL"
        assert len(split_entry_blocks(saved.file_path.read_text(encoding="utf-8"))) == 2, "No debe crearse una entrada nueva al fusionar un duplicado"

        # Test 4: documentación final revisada, sin estado draft ni implementación pendiente
        skill_text = SKILL_MD.read_text(encoding="utf-8").lower()
        assert "pendiente de implementacion" not in skill_text
        assert "draft documental" not in skill_text
        assert "scripts/test_phase1.py` a `scripts/test_phase22.py" in skill_text

        # Regresión mínima: lectura, búsqueda y listado siguen funcionando tras la limpieza
        listing = list_entries("camper", DATA_DIR)
        assert listing.total_entries == 2
        search = search_entries("camper", "ventilación", DATA_DIR)
        assert len(search.matched_hits) == 1
        assert search.matched_hits[0].entry.entry_id == enriched.entry.entry_id

        print("OK: fase 22 tests pasados")
        return 0
    finally:
        if WORK_DIR.exists():
            shutil.rmtree(WORK_DIR)


if __name__ == "__main__":
    raise SystemExit(main())
