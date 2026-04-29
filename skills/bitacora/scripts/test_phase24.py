#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import tempfile
import uuid
from pathlib import Path

def run_script(args: list[str]) -> subprocess.CompletedProcess:
    base_dir = Path(__file__).resolve().parent.parent
    script_path = base_dir / "scripts" / "read_entries.py"
    return subprocess.run(
        ["python", str(script_path)] + args,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

def test_serve_document() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        data_dir = Path(tmpdir)
        project = "test_doc"
        file_path = data_dir / f"{project}.md"
        adjuntos_dir = data_dir / "adjuntos"
        adjuntos_dir.mkdir(parents=True, exist_ok=True)

        entry_id_1 = f"entry-{uuid.uuid4().hex[:12]}"
        entry_id_2 = f"entry-{uuid.uuid4().hex[:12]}"
        entry_id_3 = f"entry-{uuid.uuid4().hex[:12]}"

        content = f"""---entry---

---
id: {entry_id_1}
fecha: 2026-04-29T10:00:00.000Z
proyecto: {project}
categoria: manuales
tipo: documento
titulo: Manual del coche
resumen: Fallback
calidad_resumen: fallback
estado: nuevo
fuente: "PDF adjunto: manual_coche.pdf"
---

Nota personal

---entry---

---
id: {entry_id_2}
fecha: 2026-04-29T10:05:00.000Z
proyecto: {project}
categoria: manuales
tipo: video
titulo: Video del coche
resumen: Fallback
calidad_resumen: fallback
estado: nuevo
fuente: "https://youtube.com"
---

Nota personal

---entry---

---
id: {entry_id_3}
fecha: 2026-04-29T10:10:00.000Z
proyecto: {project}
categoria: manuales
tipo: documento
titulo: Documento Inexistente
resumen: Fallback
calidad_resumen: fallback
estado: nuevo
fuente: "PDF adjunto: no_existe.pdf"
---

Nota personal
"""
        file_path.write_text(content, encoding="utf-8")

        # Create valid attachment
        valid_pdf_path = adjuntos_dir / "manual_coche.pdf"
        valid_pdf_path.write_text("fake pdf content", encoding="utf-8")

        # Check general parsing
        res = run_script(["--project", project, "--data-dir", str(data_dir), "--technical"])
        print(f"DEBUG TECHNICAL: {res.stdout.encode('ascii', 'replace').decode('ascii')} {res.stderr.encode('ascii', 'replace').decode('ascii')}")

        # 1. Non-existent entry

        result = run_script(["--project", project, "--data-dir", str(data_dir), "--serve-document", "entry-nonexistent"])
        assert result.returncode == 1, f"Debió fallar con entrada inexistente. Salida: {result.stdout} {result.stderr}"
        assert "no existe" in result.stderr, f"Stderr: {result.stderr}"

        # 2. Non-document entry
        result = run_script(["--project", project, "--data-dir", str(data_dir), "--serve-document", entry_id_2])
        assert result.returncode == 1, "Debió fallar con entrada tipo no documento"
        assert "no es de tipo 'documento'" in result.stderr

        # 3. Document entry but file missing
        result = run_script(["--project", project, "--data-dir", str(data_dir), "--serve-document", entry_id_3])
        assert result.returncode == 1, f"Debió fallar con archivo inexistente. Salida: {result.stdout} {result.stderr}"
        assert "no existe en disco" in result.stderr, f"Stderr: {result.stderr}"

        # 4. Valid document entry
        result = run_script(["--project", project, "--data-dir", str(data_dir), "--serve-document", entry_id_1])
        assert result.returncode == 0, f"Debió tener éxito. Error: {result.stderr}"
        assert "MEDIA:./tmp/outbound/" in result.stdout
        
        # Verify the file was actually copied
        output_line = result.stdout.strip()
        path_str = output_line.split("MEDIA:")[1]
        
        # Resolve from the workspace root (which the script uses)
        # Because read_entries.py uses Path("tmp/outbound") which is relative to cwd.
        # When running test via pytest, cwd might be openclaw or bitacora.
        copied_file = Path(path_str).resolve()
        assert copied_file.exists(), f"El archivo copiado no existe en {copied_file}"
        assert copied_file.read_text(encoding="utf-8") == "fake pdf content"

        print("Test phase 24 (serve_document) passed!")

if __name__ == "__main__":
    test_serve_document()
