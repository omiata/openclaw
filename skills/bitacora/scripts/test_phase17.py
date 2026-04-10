#!/usr/bin/env python3
from __future__ import annotations

import shutil
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
WORK_DIR = SKILL_DIR / ".tmp_phase17"
DATA_DIR = WORK_DIR / "data"

sys.path.insert(0, str(SCRIPT_DIR))

from read_entries import get_entry_by_id, list_pending_enrichment_entries, search_entries  # noqa: E402
from save_entry import capture_entry, update_existing_entry  # noqa: E402


def no_metadata(_url: str, _timeout: float):
    return None


def main() -> int:
    if WORK_DIR.exists():
        shutil.rmtree(WORK_DIR)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    try:
        saved = capture_entry(
            project="camper",
            category="electricidad",
            content="https://example.com/instalacion-12v",
            source="https://example.com/instalacion-12v",
            data_dir=DATA_DIR,
            metadata_fetcher=no_metadata,
            human_output=True,
        )
        assert saved.status == "saved"
        assert saved.entry is not None
        assert saved.entry.calidad_resumen == "fallback", "El setup de la fase 17 necesita una entrada fallback"

        # Test 1: añadir nota personal a entrada existente
        updated_first, _ = update_existing_entry(
            project="camper",
            entry_id=saved.entry.entry_id,
            additional_content="Montarlo cerca del arcón derecho para acortar cableado.",
            data_dir=DATA_DIR,
        )
        assert updated_first.contenido_adicional == "Montarlo cerca del arcón derecho para acortar cableado."
        assert updated_first.calidad_resumen == "usuario", "Una entrada fallback enriquecida con nota debe pasar a usuario"
        assert updated_first.entry_id == saved.entry.entry_id
        assert updated_first.fecha == saved.entry.fecha

        # Test 2: ampliar tags y acumular nota sin sobrescribir la previa
        updated_second, _ = update_existing_entry(
            project="camper",
            entry_id=saved.entry.entry_id,
            additional_content="Revisar sección de fusibles ANL y paso por mamparo.",
            tags=["12v", "fusibles-anl", "12v"],
            data_dir=DATA_DIR,
        )
        assert updated_second.tags == ("12v", "fusibles-anl"), "Los tags deben ampliarse y deduplicarse"
        assert "Montarlo cerca del arcón derecho" in (updated_second.contenido_adicional or "")
        assert "Revisar sección de fusibles ANL" in (updated_second.contenido_adicional or "")
        assert "\n\n" in (updated_second.contenido_adicional or ""), "La nota nueva debe añadirse con separación clara"

        # Test 3: YAML/note resultante legibles y coherentes
        lookup = get_entry_by_id("camper", saved.entry.entry_id, DATA_DIR)
        assert lookup.entry is not None
        assert lookup.entry.contenido_adicional == updated_second.contenido_adicional
        assert lookup.entry.tags == ["12v", "fusibles-anl"]
        assert lookup.entry.calidad_resumen == "usuario"

        # Regresión mínima: búsqueda y pendientes siguen funcionando
        search = search_entries("camper", "mamparo", DATA_DIR)
        assert len(search.matched_hits) == 1, "La búsqueda debe encontrar la nota personal añadida"
        assert search.matched_hits[0].entry.entry_id == saved.entry.entry_id

        pending = list_pending_enrichment_entries("camper", DATA_DIR)
        assert not pending.matched_entries, "Una entrada ya enriquecida no debe seguir apareciendo como pendiente"

        print("OK: fase 17 tests pasados")
        return 0
    finally:
        if WORK_DIR.exists():
            shutil.rmtree(WORK_DIR)


if __name__ == "__main__":
    raise SystemExit(main())
