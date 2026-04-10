#!/usr/bin/env python3
from __future__ import annotations

import shutil
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
WORK_DIR = SKILL_DIR / ".tmp_phase9"
DATA_DIR = WORK_DIR / "data"

sys.path.insert(0, str(SCRIPT_DIR))

from read_entries import list_entries, search_entries  # noqa: E402
from save_entry import ExternalMetadata, append_entry, extract_external_metadata  # noqa: E402


def count_blocks(file_path: Path) -> int:
    content = file_path.read_text(encoding="utf-8")
    return sum(1 for part in content.split("---entry---") if part.strip())


def timeout_metadata(_url: str, _timeout: float):
    raise TimeoutError("timeout inducido")


def broken_metadata(_url: str, _timeout: float):
    raise RuntimeError("fallo de red inducido")


def main() -> int:
    if WORK_DIR.exists():
        shutil.rmtree(WORK_DIR)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    try:
        # Test 1: extracción exitosa en YouTube/Vimeo mediante oEmbed
        youtube_metadata = extract_external_metadata(
            "https://www.youtube.com/watch?v=abc123",
            fetch_json=lambda _url, _timeout: {
                "title": "DIY Camper Wiring Basics",
                "description": "Recorrido corto por fusibles, batería y distribución 12V.",
            },
            fetch_text=lambda _url, _timeout: "",
        )
        assert youtube_metadata is not None
        assert youtube_metadata.title == "DIY Camper Wiring Basics"
        assert youtube_metadata.description == "Recorrido corto por fusibles, batería y distribución 12V."
        assert youtube_metadata.source_kind == "oembed"

        youtube_entry, youtube_path = append_entry(
            project="camper",
            category="electricidad",
            content="https://www.youtube.com/watch?v=abc123",
            source="https://www.youtube.com/watch?v=abc123",
            data_dir=DATA_DIR,
            metadata_fetcher=lambda _url, _timeout: youtube_metadata,
        )
        assert youtube_entry.titulo == "DIY Camper Wiring Basics"
        assert youtube_entry.calidad_resumen == "auto"
        assert "Recorrido corto por fusibles" in youtube_entry.resumen
        assert count_blocks(youtube_path) == 1

        # Test 2: extracción exitosa en web normal con og:title y meta description
        html_page = """
        <html>
          <head>
            <meta property=\"og:title\" content=\"Aislamiento térmico en furgoneta\" />
            <meta name=\"description\" content=\"Comparativa breve entre XPS, Kaiflex y corcho proyectado.\" />
            <title>Título de respaldo</title>
          </head>
        </html>
        """
        web_metadata = extract_external_metadata(
            "https://example.com/aislamiento",
            fetch_json=lambda _url, _timeout: {},
            fetch_text=lambda _url, _timeout: html_page,
        )
        assert web_metadata is not None
        assert web_metadata.title == "Aislamiento térmico en furgoneta"
        assert web_metadata.description == "Comparativa breve entre XPS, Kaiflex y corcho proyectado."
        assert web_metadata.source_kind == "html"

        web_entry, _ = append_entry(
            project="camper",
            category="aislamiento",
            content="https://example.com/aislamiento",
            source="https://example.com/aislamiento",
            data_dir=DATA_DIR,
            metadata_fetcher=lambda _url, _timeout: web_metadata,
        )
        assert web_entry.titulo == "Aislamiento térmico en furgoneta"
        assert web_entry.calidad_resumen == "auto"
        assert "Kaiflex" in web_entry.resumen

        # Test 3: timeout duro con fallback seguro y sin bloquear el guardado
        timeout_entry, timeout_path = append_entry(
            project="camper",
            category="ventilacion",
            content="https://example.com/ventilacion",
            source="https://example.com/ventilacion",
            data_dir=DATA_DIR,
            metadata_fetcher=timeout_metadata,
        )
        assert timeout_entry.calidad_resumen == "fallback"
        assert "Pendiente de revisar" in timeout_entry.resumen
        assert count_blocks(timeout_path) == 3

        # Test 4: fallo de red seguro, sin bloqueo ni estado inconsistente
        broken_entry, broken_path = append_entry(
            project="camper",
            category="cama",
            content="https://example.com/cama-plegable",
            source="https://example.com/cama-plegable",
            data_dir=DATA_DIR,
            metadata_fetcher=broken_metadata,
        )
        assert broken_entry.calidad_resumen == "fallback"
        assert broken_path.exists()
        assert count_blocks(broken_path) == 4

        # Regresión mínima: entradas sin URL y texto puro siguen funcionando
        plain_entry, plain_path = append_entry(
            project="camper",
            category="ideas-generales",
            content="Mover la batería auxiliar al lateral izquierdo para liberar el paso.",
            data_dir=DATA_DIR,
            metadata_fetcher=timeout_metadata,
        )
        assert plain_entry.calidad_resumen == "auto"
        assert plain_entry.tipo == "nota"
        assert count_blocks(plain_path) == 5

        listing = list_entries("camper", DATA_DIR)
        assert listing.total_entries == 5, "La lectura dejó de contar entradas válidas tras la Fase 9"
        search = search_entries("camper", "batería auxiliar", DATA_DIR)
        assert len(search.matched_hits) == 1, "La búsqueda dejó de funcionar con entradas sin URL"
        assert search.matched_hits[0].entry.entry_id == plain_entry.entry_id

        print("OK: fase 9 tests pasados")
        return 0
    finally:
        if WORK_DIR.exists():
            shutil.rmtree(WORK_DIR)


if __name__ == "__main__":
    raise SystemExit(main())
