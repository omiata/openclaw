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
