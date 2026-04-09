#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
WORK_DIR = SKILL_DIR / ".tmp_phase5"
DATA_DIR = WORK_DIR / "data"

sys.path.insert(0, str(SCRIPT_DIR))

from read_entries import build_output, build_search_output, get_entry_by_id, list_entries, search_entries  # noqa: E402
from save_entry import DuplicateEntryError, append_entry, update_existing_entry  # noqa: E402


def count_blocks(file_path: Path) -> int:
    content = file_path.read_text(encoding="utf-8")
    return sum(1 for part in content.split("---entry---") if part.strip())


def main() -> int:
    if WORK_DIR.exists():
        shutil.rmtree(WORK_DIR)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    try:
        project = "phase5-test"
        url = "https://example.com/aislamiento-xps"

        # Test 1: guardar URL nueva añade una entrada válida
        first_entry, file_path = append_entry(
            project=project,
            category="aislamiento",
            content=url,
            source=url,
            data_dir=DATA_DIR,
            summary="Guía base para aislamiento térmico en furgoneta.",
        )
        assert file_path.exists(), "El archivo del proyecto no se creó"
        assert count_blocks(file_path) == 1, "La URL nueva no creó exactamente una entrada"

        # Test 2: guardar la misma URL de nuevo no crea una nueva entrada
        duplicate_error = None
        try:
            append_entry(
                project=project,
                category="aislamiento",
                content=url,
                source=url,
                data_dir=DATA_DIR,
                additional_content="No debería guardarse como duplicada.",
            )
        except DuplicateEntryError as exc:
            duplicate_error = exc

        assert duplicate_error is not None, "No se detectó el duplicado por URL exacta"
        assert duplicate_error.match.entry.entry_id == first_entry.entry_id
        assert count_blocks(file_path) == 1, "El archivo ganó una entrada pese al duplicado"

        # Test 3: el CLI informa claramente el duplicado y no guarda nada nuevo
        duplicate_run = subprocess.run(
            [
                sys.executable,
                str(SCRIPT_DIR / "save_entry.py"),
                "--project",
                project,
                "--category",
                "aislamiento",
                "--content",
                url,
                "--source",
                url,
                "--data-dir",
                str(DATA_DIR),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        assert duplicate_run.returncode == 1, "El CLI debería fallar al detectar URL duplicada"
        assert "URL duplicada detectada" in duplicate_run.stderr
        assert "No se ha creado una entrada nueva" in duplicate_run.stderr
        assert count_blocks(file_path) == 1, "El CLI duplicó la entrada cuando debía bloquearla"

        # Test 4: actualización explícita por URL reescribe la entrada sin duplicarla
        updated_entry, updated_path = update_existing_entry(
            project=project,
            source_url=url,
            data_dir=DATA_DIR,
            tags=["xps", "suelo"],
            summary="Resumen actualizado para revisar espesores y puentes térmicos.",
            additional_content="Añadir comparativa con corcho proyectado.",
        )
        assert updated_path == file_path
        assert updated_entry.entry_id == first_entry.entry_id, "Se modificó el id inmutable"
        assert updated_entry.fecha == first_entry.fecha, "Se modificó la fecha inmutable"
        assert count_blocks(file_path) == 1, "La actualización creó un bloque extra"

        lookup = get_entry_by_id(project, first_entry.entry_id, DATA_DIR)
        assert lookup.entry is not None, "La entrada actualizada no se puede recuperar"
        assert lookup.entry.tags == ["xps", "suelo"], "Los tags no se actualizaron correctamente"
        assert lookup.entry.resumen == "Resumen actualizado para revisar espesores y puentes térmicos."
        assert lookup.entry.contenido_adicional == "Añadir comparativa con corcho proyectado."

        # Test 5: aviso ante categoría ambigua
        category_output = build_output(list_entries(project, DATA_DIR, category="aislamient"))
        assert "Aviso de categoría ambigua o no encontrada" in category_output
        assert "aislamiento" in category_output

        # Regresión Fase 2: listado sigue funcionando
        listing = list_entries(project, DATA_DIR)
        assert listing.total_entries == 1, "El listado global dejó de contar correctamente"
        listing_output = build_output(listing)
        assert "Proyecto phase5-test: 1 entradas válidas." in listing_output

        # Regresión Fase 2: filtrado por categoría existente sigue funcionando
        category_listing = list_entries(project, DATA_DIR, category="Aislamiento")
        assert len(category_listing.matched_entries) == 1, "El filtrado por categoría dejó de funcionar"
        assert category_listing.matched_entries[0].entry_id == first_entry.entry_id

        # Regresión Fase 4: búsqueda sigue funcionando sobre contenido actualizado
        search_result = search_entries(project, "corcho proyectado", DATA_DIR)
        assert len(search_result.matched_hits) == 1, "La búsqueda dejó de encontrar contenido adicional actualizado"
        search_output = build_search_output(search_result)
        assert "coincidencia en contenido_adicional" in search_output

        print("OK: fase 5 tests pasados")
        return 0
    finally:
        if WORK_DIR.exists():
            shutil.rmtree(WORK_DIR)


if __name__ == "__main__":
    raise SystemExit(main())
