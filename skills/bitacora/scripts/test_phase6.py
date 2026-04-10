#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
WORK_DIR = SKILL_DIR / ".tmp_phase6"
DATA_DIR = WORK_DIR / "data"

sys.path.insert(0, str(SCRIPT_DIR))

from read_entries import (  # noqa: E402
    build_global_stats,
    build_global_stats_output,
    build_output,
    build_project_overview,
    list_entries,
)
from save_entry import append_entry  # noqa: E402


def main() -> int:
    if WORK_DIR.exists():
        shutil.rmtree(WORK_DIR)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    try:
        camper_1, _ = append_entry(
            project="camper",
            category="aislamiento",
            content="Panel XPS para suelo y paredes.",
            data_dir=DATA_DIR,
        )
        camper_2, _ = append_entry(
            project="camper",
            category="electricidad",
            content="https://example.com/esquema-12v",
            source="https://example.com/esquema-12v",
            data_dir=DATA_DIR,
        )
        camper_3, _ = append_entry(
            project="camper",
            category="aislamiento",
            content="Corregir puente térmico en puertas traseras.",
            data_dir=DATA_DIR,
        )
        balcon_1, _ = append_entry(
            project="balcon",
            category="riego",
            content="Programador simple por goteo.",
            data_dir=DATA_DIR,
        )
        balcon_2, _ = append_entry(
            project="balcon",
            category="suelo",
            content="https://example.com/suelo-exterior",
            source="https://example.com/suelo-exterior",
            data_dir=DATA_DIR,
            resource_type="referencia",
        )

        # Test 1: overview por proyecto calcula índice de categorías y última actualización
        overview = build_project_overview("camper", DATA_DIR)
        assert overview.total_entries == 3, "El overview del proyecto no cuenta correctamente las entradas"
        category_index = {item.categoria: item for item in overview.category_index}
        assert set(category_index) == {"aislamiento", "electricidad"}
        assert category_index["aislamiento"].total_entries == 2
        assert category_index["aislamiento"].latest_update == camper_3.fecha
        assert category_index["electricidad"].total_entries == 1
        assert overview.latest_update == camper_3.fecha

        # Test 2: overview por proyecto calcula índice de tipos y estadísticas derivadas
        type_index = {item.tipo: item.total_entries for item in overview.type_index}
        assert type_index == {"link": 1, "nota": 2}, "El índice de tipos del proyecto no es correcto"

        listing_output = build_output(list_entries("camper", DATA_DIR), overview=overview)
        assert "Índice de categorías:" in listing_output
        assert "- aislamiento: 2 entradas | última actualización:" in listing_output
        assert "Índice de tipos:" in listing_output
        assert "- link: 1 entradas" in listing_output
        assert "- nota: 2 entradas" in listing_output
        assert "Estadísticas:" in listing_output
        assert "- total entradas: 3" in listing_output
        assert "- categorías distintas: 2" in listing_output
        assert "- tipos presentes: 2" in listing_output
        assert "- categorías más usadas: aislamiento (2), electricidad (1)" in listing_output

        # Test 3: estadísticas globales agregan proyectos y categorías sin usar índices como fuente de verdad
        global_stats = build_global_stats(DATA_DIR)
        assert global_stats.total_entries == 5, "Las estadísticas globales no cuentan todas las entradas válidas"
        assert global_stats.total_projects == 2, "Las estadísticas globales no cuentan todos los proyectos"
        project_map = {item.project: item for item in global_stats.projects}
        assert project_map["camper"].total_entries == 3
        assert project_map["camper"].category_count == 2
        assert project_map["camper"].type_count == 2
        assert project_map["balcon"].total_entries == 2
        assert project_map["balcon"].category_count == 2
        assert project_map["balcon"].type_count == 2
        top_categories = {item.categoria: item.total_entries for item in global_stats.top_categories}
        assert top_categories["aislamiento"] == 2
        assert top_categories["electricidad"] == 1
        assert top_categories["riego"] == 1
        assert top_categories["suelo"] == 1

        global_output = build_global_stats_output(global_stats)
        assert "Estadísticas globales: 5 entradas válidas en 2 proyectos." in global_output
        assert "- camper: 3 entradas | 2 categorías | 2 tipos | última actualización:" in global_output
        assert "- balcon: 2 entradas | 2 categorías | 2 tipos | última actualización:" in global_output
        assert "Categorías más usadas:" in global_output
        assert "- aislamiento: 2 entradas" in global_output
        assert "Tipos presentes:" in global_output
        assert "- nota: 3 entradas" in global_output
        assert "- link: 1 entradas" in global_output
        assert "- referencia: 1 entradas" in global_output

        # Test 4: el CLI expone overview por proyecto y estadísticas globales
        overview_run = subprocess.run(
            [
                sys.executable,
                str(SCRIPT_DIR / "read_entries.py"),
                "--project",
                "camper",
                "--overview",
                "--technical",
                "--data-dir",
                str(DATA_DIR),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        assert overview_run.returncode == 0, "El CLI de overview del proyecto falló"
        assert "Índice de categorías:" in overview_run.stdout
        assert "Estadísticas:" in overview_run.stdout

        global_run = subprocess.run(
            [
                sys.executable,
                str(SCRIPT_DIR / "read_entries.py"),
                "--global-stats",
                "--technical",
                "--data-dir",
                str(DATA_DIR),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        assert global_run.returncode == 0, "El CLI de estadísticas globales falló"
        assert "Estadísticas globales: 5 entradas válidas en 2 proyectos." in global_run.stdout

        print("OK: fase 6 tests pasados")
        return 0
    finally:
        if WORK_DIR.exists():
            shutil.rmtree(WORK_DIR)


if __name__ == "__main__":
    raise SystemExit(main())
