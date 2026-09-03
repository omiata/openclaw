# TELEGRAM

## Estado actual

Telegram ya esta conectado y funcionando.

## Resultado confirmado

- [x] bot accesible
- [x] pairing aprobado
- [x] mensajes de prueba funcionando

## Comando importante de aprobacion

Cuando OpenClaw muestre un codigo de pairing, la aprobacion se hace en PowerShell, no en BotFather.

Ejemplo:

```powershell
openclaw pairing approve telegram 5VS7QDTR
```

## Regla importante

`BotFather` no sirve para aprobar el pairing de OpenClaw.

La aprobacion se hace con el comando de PowerShell en tu propio PC.

## Comprobaciones utiles

```powershell
openclaw doctor
```

```powershell
openclaw gateway status
```

## Comportamiento actual de Telegram

Configuracion operativa confirmada:

- los mensajes normales se responden en texto
- los audios entrantes se transcriben y esa transcripcion se usa como contexto
- solo se envia audio cuando el usuario lo pide de forma explicita

## Objetivos futuros para Telegram

Mas adelante, este documento debera cubrir:

- [ ] reglas de uso mas detalladas
- [ ] pruebas reales

## Nota

Cuando anadamos funciones nuevas de Telegram, se registraran tambien en:

- [07_BITACORA.md](/C:/omi/openclaw/docs/07_BITACORA.md)

## Guía de Implementación y Troubleshooting (Gotchas)

A lo largo del desarrollo, hemos identificado patrones importantes sobre cómo se integra OpenClaw de vuelta con el bot de Telegram. Si algo falla en la salida (texto mal formateado, audios no generados), revisa estas reglas:

### 1. Sistema TTS y Notas de Voz
El bot solo genera audio automáticamente bajo ciertas condiciones. Para obligar a la salida, el prompt interno inyecta la etiqueta.
- **Modo soportado por defecto:** El config usa `messages.tts.auto = "tagged"`.
- **Parsing de la Etiqueta:** Para que OpenClaw realmente intercepte la etiqueta, esta no puede ir vacía si el motor base no está parcheado (históricamente requería `[[tts:text]]` o `[[tts:voz]]`). Para usar el `[[tts]]` estándar, el archivo `provider-error-utils-DZcqh6Wf.js` de la distribución debe tener el regex parcheado (`/\[\[tts\]\]/gi`) para disparar la directiva.
- Nunca envíes contenido multimedia y la etiqueta `[[tts]]` en el mismo reply si el provider bloquea combinaciones pesadas.

### 2. Previews y Streaming de UI (JSON visible)
Si ves literales como `telegram_inline_carousel` o json en la interfaz de Telegram en crudo mientras OpenClaw "escribe":
- El problema es el **Streaming Parcial**. OpenClaw empieza a volcar los datos antes de completar la estructura final del carrusel.
- **Solución Obligatoria:** Fijar `channels.telegram.streaming.mode = "off"` en la instalación de OpenClaw. Esto obliga al bot a retener todo el texto hasta que el pipeline completo procese el componente (como fotos o inline buttons) en vez de filtrar texto como update normal en el frontend.

### 3. Listados (List format)
Si la UI de Telegram presenta el contenido junto en bloques densos incomprensibles, se debe a que tu componente intentó renderizar en línea:
- Separa categóricamente secciones de array usando bullet points puros o el componente nativo de inline-carousel que implementamos recientemente en el `delivery runtime`.
