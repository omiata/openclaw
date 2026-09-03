# AGENTS.md

## Telegram audio replies

- For incoming Telegram voice notes or audio messages, transcribe them and use that transcription as input context.
- Default to text replies.
- Only include the exact tag `[[tts]]` when the user explicitly asks for audio, voice, or a voice note reply.
- When the user explicitly asks for audio, include `[[tts]]` in the final reply and also keep the same reply in visible text.
- Do not use `[[tts]]` for normal text replies.

## Telegram behavior summary

- In Telegram, always reply in text by default, unless the user explicitly asks for audio.

## Debug discipline

When debugging:
- Isolate the failing path and compare it to the working path.
- Before changing config, confirm:
 1. exact key name
 2. exact allowed value
 3. exact file controlling runtime
 4. effective runtime value
- Report findings before applying changes.
- Do not speculate before a direct test.
- If 5 useful actions do not reveal a concrete cause, stop and report the blockage.
- Do not repeat the same action more than 2 times without progress.

## Autonomy and Git Limits

- Automatically commit changes when a **full implementation block** is finished and successfully passes all its tests.
- Committing per-phase is ONLY allowed if the implementation plan is not grouped into blocks.
- **Never push** to the remote repository unless explicitly requested by the user.

## Autonomous Code Modification & Documentation (Sync Inbox Policy)

- When operating autonomously (e.g., via Telegram or TUI) to improve functionality or fix bugs, you are **STRICTLY PROHIBITED** from updating, modifying, or creating any structural documentation files (e.g., `_fases.md`, `_reglas.md`, `_changelog.md`, `AGENTIC_PROMPTING.md`, or any proposal/reference `.md` file).
- Your **ONLY** allowed method of logging your changes is to **APPEND** (never overwrite) a brief technical summary to an inbox file.
- **Inbox Routing Rules:**
  - If the change involves a specific skill (e.g., `bitacora`), append the detailed summary to `skills/<skill_name>/ref/sync_inbox.md`. THEN, append a short reference in the root `sync_inbox.md` indicating where the details are (e.g., "- 2026-04-12 | bitacora | Se actualizó la lógica, detalles en skills/bitacora/...").
  - If the change is general OpenClaw core code, append the summary ONLY to the root `sync_inbox.md`.
- **Format:** `- FECHA [YYYY-MM-DD HH:MM] | ARCHIVOS TOCADOS | RESUMEN DEL CAMBIO LOGICO`.
- You must not attempt to consolidate documentation yourself. The user will perform a formal code review and promote the notes from the inboxes to the master documentation manually.
- **Consolidation Rules (When User Requests It):**
  - Read BOTH the root `sync_inbox.md` and any referenced skill `sync_inbox` files.
  - Core/Framework changes go to the root `CHANGELOG.md`.
  - Skill-specific changes MUST ONLY go directly to the specific skill's changelog (`skills/<skill_name>/ref/<skill_name>_changelog.md`). Never mix skill details into the root `CHANGELOG.md`.
  - Clear both the root and skill-specific inboxes once their contents are fully promoted.
