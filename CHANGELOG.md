# OpenClaw Changelog

Todas las actualizaciones clave de la plataforma OpenClaw a nivel general, ordenadas cronológicamente. 

---

### [2026-04-20] - Fix de TTS Simple en Telegram 
- **Bug Fix:** Se solucionó el bug donde la etiqueta `[[tts]]` sin parámetros no generaba audio y se mostraba como texto en Telegram. `parseTtsDirectives` en el backend `provider-error-utils-DZcqh6Wf.js` solo reconocía `[[tts:text]]` y equivalentes. Se añadió el regex localmente (`/\[\[tts\]\]/gi`) y se reinició el servicio gateway.

### [2026-04-14] - Reporte de Error en TTS
- **Issue Tracked:** Identificado que el TTS en Telegram estaba inoperativo con respuestas mostrando el literal `[[tts]]`. 

### [2026-04-13] - Sistema de Carrusel de Telegram Integrado
- **Bug Fix / Streaming:** Arreglado un bug crítico de visualización donde Telegram filtraba "restos de JSON" (ej: `telegram_inline_carousel` crudo) por culpa del Streaming Mode `partial`. La solución permanente fue fijar en la instalación de OpenClaw (WSL) `channels.telegram.streaming.mode = "off"`, para garantizar entrega bloqueada del componente visual final y limpiar bundles en caliente a versiones estables.
- **Backend Refactor:** Reutilizamos el parser nativo de carrusel en el `delivery runtime` del bot, inyectando `sendPhoto` y `sendMessage` dinámicamente preservando the callback_data de interfaces interactivas. 

### [2026-04-12] - Formato Visual de Datos
- **UX Mejora:** Preferencia globalizada para retornar categorías y agrupaciones en formato explícito de 'Lista Visual' en el canal general.
