#!/usr/bin/env python3
from __future__ import annotations

import shutil
import sys
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
WORK_DIR = SKILL_DIR / ".tmp_phase14"
DATA_DIR = WORK_DIR / "data"

sys.path.insert(0, str(SCRIPT_DIR))

from read_entries import (  # noqa: E402
    build_operational_view_output,
    list_entries,
    list_entries_by_summary_quality,
    list_pending_enrichment_entries,
    list_recent_entries,
)
from save_entry import capture_entry, update_entry_state  # noqa: E402


def no_metadata(_url: str, _timeout: float):
    return None


def pause() -> None:
    time.sleep(0.02)


def main() -> int:
    if WORK_DIR.exists():
        shutil.rmtree(WORK_DIR)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    try:
        first = capture_entry(
            project="camper",
            category="electricidad",
            content="https://example.com/bateria",
            source="https://example.com/bateria",
            data_dir=DATA_DIR,
            metadata_fetcher=no_metadata,
            human_output=True,
        )
        pause()
        second = capture_entry(
            project="camper",
            category="cama",
            content="Diseño plegable con patas de aluminio y tablones ligeros.",
            data_dir=DATA_DIR,
            human_output=True,
        )
        pause()
        third = capture_entry(
            project="camper",
            category="agua",
            content="https://example.com/deposito",
            source="https://example.com/deposito",
            data_dir=DATA_DIR,
            metadata_fetcher=no_metadata,
            human_output=True,
        )
        pause()
        fourth = capture_entry(
            project="camper",
            category="ventilacion",
            content="Idea para extractor con relé térmico y rejilla discreta.",
            data_dir=DATA_DIR,
            human_output=True,
        )
        assert all(outcome.status == "saved" for outcome in (first, second, third, fourth))
        assert first.entry and second.entry and third.entry and fourth.entry

        # Marcar una fallback como descartada para comprobar que no salga en pendientes
        discarded, _ = update_entry_state(
            project="camper",
            entry_id=third.entry.entry_id,
            state="descartado",
            data_dir=DATA_DIR,
        )
        assert discarded.estado == "descartado"

        # Test 1: vista de últimas entradas en orden temporal
        recent = list_recent_entries("camper", DATA_DIR, limit=2)
        recent_ids = [entry.entry_id for entry in recent.matched_entries]
        assert recent_ids == [fourth.entry.entry_id, third.entry.entry_id], "Las últimas entradas no respetan el orden temporal"

        recent_human = build_operational_view_output(recent, technical=False)
        assert "últimas entradas" in recent_human.lower()
        assert fourth.entry.titulo in recent_human and third.entry.titulo in recent_human

        # Test 2: vista de calidad_resumen fallback
        fallback_view = list_entries_by_summary_quality("camper", "fallback", DATA_DIR)
        fallback_ids = {entry.entry_id for entry in fallback_view.matched_entries}
        assert fallback_ids == {first.entry.entry_id, third.entry.entry_id}, "El filtro por calidad_resumen fallback no coincide"

        # Test 3: pendientes de enriquecer excluyen descartadas y reenganchan al usuario
        pending = list_pending_enrichment_entries("camper", DATA_DIR)
        pending_ids = [entry.entry_id for entry in pending.matched_entries]
        assert pending_ids == [first.entry.entry_id], "Las pendientes de enriquecer deben excluir descartadas y mantener orden temporal"

        pending_human = build_operational_view_output(pending, technical=False)
        assert "pendientes de enriquecer" in pending_human.lower()
        assert "Si quieres, puedo ayudarte a enriquecer" in pending_human
        assert first.entry.titulo in pending_human
        assert third.entry.titulo not in pending_human

        # Regresión mínima: estados, búsqueda/listado general siguen funcionando
        reviewed = list_entries("camper", DATA_DIR, state="descartado")
        assert len(reviewed.matched_entries) == 1, "El filtro por estado descartado dejó de funcionar"
        assert reviewed.matched_entries[0].entry_id == third.entry.entry_id

        listing = list_entries("camper", DATA_DIR)
        assert listing.total_entries == 4, "El listado global dejó de devolver todas las entradas"

        print("OK: fase 14 tests pasados")
        return 0
    finally:
        if WORK_DIR.exists():
            shutil.rmtree(WORK_DIR)


if __name__ == "__main__":
    raise SystemExit(main())
