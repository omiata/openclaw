#!/usr/bin/env python3
from __future__ import annotations

import shutil
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
WORK_DIR = SKILL_DIR / ".tmp_phase10"
DATA_DIR = WORK_DIR / "data"

sys.path.insert(0, str(SCRIPT_DIR))

from read_entries import list_entries, load_entries, search_entries  # noqa: E402
from save_entry import ExternalMetadata, capture_entry, split_entry_blocks  # noqa: E402


def metadata_auto(_url: str, _timeout: float):
    return ExternalMetadata(
        title="Canaleta limpia para cableado camper",
        description="Montaje ordenado de canaletas, fusibles y paso de cables bajo mueble lateral.",
        source_kind="oembed",
    )


def no_metadata(_url: str, _timeout: float):
    return None


def main() -> int:
    if WORK_DIR.exists():
        shutil.rmtree(WORK_DIR)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    try:
        # Test 1: prioridad correcta del resumen del usuario
        user_outcome = capture_entry(
            project="camper",
            category="electricidad",
            content="https://example.com/canaleta",
            source="https://example.com/canaleta",
            summary="Resumen manual del usuario sobre la parte útil del cableado.",
            data_dir=DATA_DIR,
            metadata_fetcher=metadata_auto,
        )
        assert user_outcome.status == "saved"
        assert user_outcome.entry is not None
        assert user_outcome.entry.calidad_resumen == "usuario"
        assert user_outcome.entry.resumen == "Resumen manual del usuario sobre la parte útil del cableado."

        # Test 2: metadata útil gana frente al texto libre cuando no hay resumen del usuario
        auto_outcome = capture_entry(
            project="camper",
            category="electricidad",
            content="Texto local pobre que no debería dominar el resumen final.",
            source="https://example.com/canaleta-2",
            data_dir=DATA_DIR,
            metadata_fetcher=metadata_auto,
        )
        assert auto_outcome.status == "saved"
        assert auto_outcome.entry is not None
        assert auto_outcome.entry.calidad_resumen == "auto"
        assert "Montaje ordenado de canaletas" in auto_outcome.entry.resumen
        assert "Texto local pobre" not in auto_outcome.entry.resumen

        # Test 3: entrada pobre con fallback mínimo honesto y visibilidad de calidad
        fallback_outcome = capture_entry(
            project="camper",
            category="homologacion",
            content="https://example.com/tramite",
            source="https://example.com/tramite",
            data_dir=DATA_DIR,
            metadata_fetcher=no_metadata,
        )
        assert fallback_outcome.status == "saved"
        assert fallback_outcome.entry is not None
        assert fallback_outcome.entry.calidad_resumen == "fallback"
        assert fallback_outcome.entry.resumen == (
            "Recurso guardado desde example.com para camper/homologacion. Pendiente de revisar."
        )
        assert "calidad_resumen=fallback" in fallback_outcome.prompt

        # Regresión: render y parseo siguen siendo correctos en disco
        camper_path = DATA_DIR / "camper.md"
        blocks = split_entry_blocks(camper_path.read_text(encoding="utf-8"))
        assert len(blocks) == 3, "El archivo no contiene exactamente 3 bloques tras la Fase 10"

        entries, warnings, _ = load_entries("camper", DATA_DIR)
        assert not warnings, f"El parseo produjo avisos inesperados: {warnings}"
        qualities = {entry.entry_id: entry.calidad_resumen for entry in entries}
        assert set(qualities.values()) == {"usuario", "auto", "fallback"}

        listing = list_entries("camper", DATA_DIR)
        assert listing.total_entries == 3, "El listado dejó de funcionar tras ajustar los resúmenes"
        search = search_entries("camper", "canaletas", DATA_DIR)
        assert len(search.matched_hits) == 1, "La búsqueda dejó de encontrar el resumen enriquecido"
        assert search.matched_hits[0].entry.entry_id == auto_outcome.entry.entry_id

        print("OK: fase 10 tests pasados")
        return 0
    finally:
        if WORK_DIR.exists():
            shutil.rmtree(WORK_DIR)


if __name__ == "__main__":
    raise SystemExit(main())
