#!/usr/bin/env python3
from __future__ import annotations

import shutil
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
WORK_DIR = SKILL_DIR / ".tmp_phase2"
DATA_DIR = WORK_DIR / "data"

sys.path.insert(0, str(SCRIPT_DIR))

from read_entries import build_output, list_entries, load_entries  # noqa: E402
from save_entry import ENTRY_DELIMITER, append_entry  # noqa: E402


def count_real_blocks(file_path: Path) -> int:
    content = file_path.read_text(encoding="utf-8")
    return len([part for part in content.split(ENTRY_DELIMITER) if part.strip()])


def main() -> int:
    if WORK_DIR.exists():
        shutil.rmtree(WORK_DIR)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    try:
        project = "phase2-test"

        entry1, _ = append_entry(project, "aislamiento", "Panel XPS para suelo y paredes", DATA_DIR)
        entry2, _ = append_entry(project, "electricidad", "https://example.com/esquema-12v", DATA_DIR)
        entry3, _ = append_entry(project, "Aislamiento", "Puente térmico en puertas traseras", DATA_DIR)

        file_path = DATA_DIR / f"{project}.md"
        assert file_path.exists(), "No existe el archivo del proyecto para la fase 2"

        # Test 1: listar todo coincide con el número real de bloques válidos
        listing_all = list_entries(project, DATA_DIR)
        real_blocks = count_real_blocks(file_path)
        assert listing_all.total_entries == real_blocks, (
            f"El listado devuelve {listing_all.total_entries} entradas y el archivo tiene {real_blocks} bloques"
        )
        assert len(listing_all.matched_entries) == real_blocks, "El listado global no devuelve todas las entradas"
        assert listing_all.matched_entries[0].entry_id == entry3.entry_id, "El listado no muestra primero la entrada más reciente"
        assert listing_all.matched_entries[1].entry_id == entry2.entry_id, "El listado no mantiene el orden esperado por fecha"
        assert listing_all.matched_entries[2].entry_id == entry1.entry_id, "El listado no mantiene el orden esperado por fecha"
        output_all = build_output(listing_all)
        assert "Proyecto phase2-test: 3 entradas válidas." in output_all

        # Test 2: filtrar por categoría existente con variación menor
        listing_category = list_entries(project, DATA_DIR, category="Aislamiento")
        assert listing_category.normalized_category == "aislamiento"
        assert len(listing_category.matched_entries) == 2, "El filtro por categoría no devolvió 2 entradas"
        assert all(entry.categoria == "aislamiento" for entry in listing_category.matched_entries)
        output_category = build_output(listing_category)
        assert "categoría aislamiento: 2 entradas de 3 válidas" in output_category

        # Test 3: filtrar por categoría inexistente devuelve cero resultados sin error
        listing_empty = list_entries(project, DATA_DIR, category="ventilacion")
        assert len(listing_empty.matched_entries) == 0, "La categoría inexistente no devolvió cero resultados"
        output_empty = build_output(listing_empty)
        assert "No hay entradas para mostrar." in output_empty

        # Regresión Fase 1: guardar después de leer sigue funcionando
        before_append = count_real_blocks(file_path)
        _ = load_entries(project, DATA_DIR)
        append_entry(project, "cama", "Idea de cama plegable con tres módulos", DATA_DIR)
        after_append = count_real_blocks(file_path)
        assert after_append == before_append + 1, "Guardar después de leer rompió el append de Fase 1"

        print("OK: fase 2 tests pasados")
        return 0
    finally:
        if WORK_DIR.exists():
            shutil.rmtree(WORK_DIR)


if __name__ == "__main__":
    raise SystemExit(main())
