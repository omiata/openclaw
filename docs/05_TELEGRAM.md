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

## Objetivos futuros para Telegram

Mas adelante, este documento debera cubrir:

- [ ] enviar mensajes de texto
- [ ] recibir mensajes de texto
- [ ] enviar audios
- [ ] recibir audios
- [ ] transcripcion
- [ ] reglas de uso
- [ ] pruebas reales

## Nota

Cuando anadamos funciones nuevas de Telegram, se registraran tambien en:

- [07_BITACORA.md](/C:/omi/openclaw/docs/07_BITACORA.md)
