#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
WORK_DIR = SKILL_DIR / ".tmp_phase23"
DATA_DIR = WORK_DIR / "data"

sys.path.insert(0, str(SCRIPT_DIR))

from read_entries import (  # noqa: E402
    build_telegram_carousel_callback_data,
    build_telegram_carousel_output,
    list_entries,
)
from save_entry import (  # noqa: E402
    capture_entry,
    derive_reference_thumbnail_url,
)


def no_metadata(_url: str, _timeout: float):
    return None


def main() -> int:
    if WORK_DIR.exists():
        shutil.rmtree(WORK_DIR)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    try:
        youtube_url = "https://youtu.be/dQw4w9WgXcQ?si=abc123"
        plain_url = "https://example.com/guia-cama-plegable"

        first = capture_entry(
            project="camper",
            category="cama",
            content=youtube_url,
            source=youtube_url,
            data_dir=DATA_DIR,
            metadata_fetcher=no_metadata,
            human_output=True,
        )
        assert first.status == "saved"
        assert first.entry is not None

        second = capture_entry(
            project="camper",
            category="cama",
            content=plain_url,
            source=plain_url,
            title="Guía de cama plegable",
            data_dir=DATA_DIR,
            metadata_fetcher=no_metadata,
            human_output=True,
        )
        assert second.status == "saved"
        assert second.entry is not None

        third = capture_entry(
            project="camper",
            category="cama",
            content="Nota interna sin enlace",
            data_dir=DATA_DIR,
            metadata_fetcher=no_metadata,
            human_output=True,
        )
        assert third.status == "saved"

        assert derive_reference_thumbnail_url(youtube_url) == "https://i.ytimg.com/vi/dQw4w9WgXcQ/hqdefault.jpg"
        assert derive_reference_thumbnail_url(plain_url) is None

        listing = list_entries("camper", DATA_DIR, category="cama")
        payload = json.loads(
            build_telegram_carousel_output(
                listing.matched_entries,
                project=listing.project,
                source_view="list",
                total_entries=listing.total_entries,
                warnings=listing.warnings,
                requested_category=listing.requested_category,
                cache_key="abc123",
            )
        )

        assert payload["kind"] == "telegram_inline_carousel"
        assert payload["total_items"] == 2, "La nota sin enlace no debe entrar en el carrusel"
        assert len(payload["items"]) == 2
        assert payload["initial"]["media_url"] == "https://i.ytimg.com/vi/dQw4w9WgXcQ/hqdefault.jpg"
        assert payload["items"][0]["caption"].startswith(first.entry.titulo)
        assert payload["items"][0]["source_url"] == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        assert payload["items"][0]["buttons"][0][0]["callback_data"] == "btc:abc123:0:s"
        assert payload["items"][0]["buttons"][0][1]["callback_data"] == "btc:abc123:0:n"
        assert payload["items"][1]["message"]["edit_mode"] == "caption-only"

        try:
            build_telegram_carousel_callback_data("x" * 80, 0)
            raise AssertionError("Se esperaba error por callback_data demasiado largo")
        except ValueError as exc:
            assert "64 bytes" in str(exc)

        cli = subprocess.run(
            [
                sys.executable,
                str(SCRIPT_DIR / "read_entries.py"),
                "--project",
                "camper",
                "--category",
                "cama",
                "--telegram-carousel",
                "--carousel-cache-key",
                "abc123",
                "--data-dir",
                str(DATA_DIR),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        assert cli.returncode == 0
        cli_payload = json.loads(cli.stdout)
        assert cli_payload["total_items"] == 2
        assert cli_payload["items"][0]["message"]["buttons"][0][2]["callback_data"] == "btc:abc123:1:s"

        print("OK: fase 23 tests pasados")
        return 0
    finally:
        if WORK_DIR.exists():
            shutil.rmtree(WORK_DIR)


if __name__ == "__main__":
    raise SystemExit(main())
