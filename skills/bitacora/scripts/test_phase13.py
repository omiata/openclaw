#!/usr/bin/env python3
from __future__ import annotations

import shutil
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
WORK_DIR = SKILL_DIR / ".tmp_phase13"
DATA_DIR = WORK_DIR / "data"

sys.path.insert(0, str(SCRIPT_DIR))

from read_entries import build_output, list_entries, search_entries  # noqa: E402
from save_entry import capture_entry, split_entry_blocks, update_entry_state  # noqa: E402


def no_metadata(_url: str, _timeout: float):
    return None


def main() -> int:
    if WORK_DIR.exists():
        shutil.rmtree(WORK_DIR)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    try:
        first = capture_entry(
            project="camper",
            category="electricidad",
            content="https://example.com/fusibles",
            source="https://example.com/fusibles",
            data_dir=DATA_DIR,
            metadata_fetcher=no_metadata,
            human_output=True,
        )
        second = capture_entry(
            project="camper",
            category="agua",
            content="Apunte sobre depósito auxiliar con salida de limpieza.",
            data_dir=DATA_DIR,
            human_output=True,
        )
        assert first.status == "saved" and second.status == "saved"
        assert first.entry is not None and second.entry is not None

        # Test 1: estado por defecto
        assert first.entry.estado == "nuevo", "Las entradas nuevas deben salir con estado nuevo"
        assert second.entry.estado == "nuevo", "Todas las entradas nuevas deben salir con estado nuevo"

        camper_path = DATA_DIR / "camper.md"
        raw_text = camper_path.read_text(encoding="utf-8")
        assert len(split_entry_blocks(raw_text)) == 2, "El archivo debe contener exactamente dos entradas"

        # Test 2: actualización de estado sin tocar id ni fecha
        updated_entry, _file_path = update_entry_state(
            project="camper",
            entry_id=first.entry.entry_id,
            state="revisado",
            data_dir=DATA_DIR,
        )
        assert updated_entry.estado == "revisado", "La entrada no quedó marcada como revisada"
        assert updated_entry.entry_id == first.entry.entry_id, "El id es inmutable y no debe cambiar"
        assert updated_entry.fecha == first.entry.fecha, "La fecha original es inmutable y no debe cambiar"

        # Test 3: filtro por estado
        reviewed = list_entries("camper", DATA_DIR, state="revisado")
        assert len(reviewed.matched_entries) == 1, "El filtro por revisado debe devolver exactamente una entrada"
        assert reviewed.matched_entries[0].entry_id == first.entry.entry_id

        new_entries = list_entries("camper", DATA_DIR, state="nuevo")
        assert len(new_entries.matched_entries) == 1, "El filtro por nuevo debe dejar la otra entrada"
        assert new_entries.matched_entries[0].entry_id == second.entry.entry_id

        human_reviewed = build_output(reviewed, technical=False)
        assert "estado revisada" in human_reviewed, "La salida humana debe reflejar el filtro por estado"
        assert first.entry.entry_id not in human_reviewed, "La salida humana no debe exponer ids"

        # Regresión mínima: lectura, búsqueda y listado global siguen funcionando
        listing = list_entries("camper", DATA_DIR)
        assert listing.total_entries == 2, "El listado global dejó de contar bien las entradas"
        search = search_entries("camper", "depósito", DATA_DIR)
        assert len(search.matched_hits) == 1, "La búsqueda dejó de encontrar entradas tras añadir estados"
        assert search.matched_hits[0].entry.entry_id == second.entry.entry_id

        print("OK: fase 13 tests pasados")
        return 0
    finally:
        if WORK_DIR.exists():
            shutil.rmtree(WORK_DIR)


if __name__ == "__main__":
    raise SystemExit(main())
