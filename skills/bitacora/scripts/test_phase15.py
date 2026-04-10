#!/usr/bin/env python3
from __future__ import annotations

import shutil
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
WORK_DIR = SKILL_DIR / ".tmp_phase15"
DATA_DIR = WORK_DIR / "data"

sys.path.insert(0, str(SCRIPT_DIR))

from read_entries import (  # noqa: E402
    REMINDER_CRON_EXPRESSION,
    REMINDER_TIMEZONE,
    build_daily_enrichment_reminder_job,
    build_enrichment_reminder,
    list_entries,
    list_pending_enrichment_entries,
)
from save_entry import capture_entry, update_entry_state, update_existing_entry  # noqa: E402


def no_metadata(_url: str, _timeout: float):
    return None


def main() -> int:
    if WORK_DIR.exists():
        shutil.rmtree(WORK_DIR)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    try:
        fallback_pending = capture_entry(
            project="camper",
            category="electricidad",
            content="https://example.com/inversor",
            source="https://example.com/inversor",
            data_dir=DATA_DIR,
            metadata_fetcher=no_metadata,
            human_output=True,
        )
        fallback_discarded = capture_entry(
            project="camper",
            category="agua",
            content="https://example.com/bomba",
            source="https://example.com/bomba",
            data_dir=DATA_DIR,
            metadata_fetcher=no_metadata,
            human_output=True,
        )
        enriched = capture_entry(
            project="camper",
            category="cama",
            content="Diseño plegable con bastidor de aluminio y cierre lateral.",
            data_dir=DATA_DIR,
            human_output=True,
        )
        assert fallback_pending.entry and fallback_discarded.entry and enriched.entry

        update_entry_state(
            project="camper",
            entry_id=fallback_discarded.entry.entry_id,
            state="descartado",
            data_dir=DATA_DIR,
        )
        update_existing_entry(
            project="camper",
            entry_id=enriched.entry.entry_id,
            additional_content="Añadir colchoneta plegable y medir hueco de paso.",
            data_dir=DATA_DIR,
        )

        # Test 1: selección correcta de entradas fallback pendientes
        pending = list_pending_enrichment_entries("camper", DATA_DIR)
        pending_ids = [entry.entry_id for entry in pending.matched_entries]
        assert pending_ids == [fallback_pending.entry.entry_id], "El recordatorio debe usar solo fallback no descartadas"

        # Test 2: formato del recordatorio
        reminder = build_enrichment_reminder("camper", DATA_DIR, technical=False)
        assert "pendientes de enriquecer" in reminder
        assert fallback_pending.entry.titulo in reminder
        assert fallback_discarded.entry.titulo not in reminder
        assert "retomamos una ahora" in reminder

        # Test 3: periodicidad a las 20:00 y uso del mecanismo nativo validado
        job = build_daily_enrichment_reminder_job("camper")
        assert job["schedule"]["kind"] == "cron", "La programación debe usar el mecanismo nativo cron de OpenClaw"
        assert job["schedule"]["expr"] == REMINDER_CRON_EXPRESSION, "La expresión cron debe quedar fijada a las 20:00"
        assert job["schedule"]["tz"] == REMINDER_TIMEZONE, "La zona horaria del recordatorio debe quedar fijada"
        assert job["sessionTarget"] == "current"
        assert job["payload"]["kind"] == "agentTurn"
        assert job["delivery"]["mode"] == "announce"
        assert "calidad_resumen" in job["payload"]["message"]

        # Regresión mínima: estados y vistas siguen funcionando
        discarded = list_entries("camper", DATA_DIR, state="descartado")
        assert len(discarded.matched_entries) == 1, "La vista por estado descartado dejó de funcionar tras preparar el recordatorio"
        assert discarded.matched_entries[0].entry_id == fallback_discarded.entry.entry_id

        listing = list_entries("camper", DATA_DIR)
        assert listing.total_entries == 3, "El listado global dejó de funcionar tras la Fase 15"

        print("OK: fase 15 tests pasados")
        return 0
    finally:
        if WORK_DIR.exists():
            shutil.rmtree(WORK_DIR)


if __name__ == "__main__":
    raise SystemExit(main())
