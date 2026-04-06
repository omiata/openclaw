# INSTALACION WINDOWS

## Estado actual

La instalacion base de OpenClaw en Windows ya esta completada y validada.

## Resultado confirmado

- [x] OpenClaw instalado en Windows
- [x] Onboarding completado
- [x] OpenAI configurado con OAuth
- [x] Telegram emparejado y aprobado
- [x] Gateway instalado como `Scheduled Task`
- [x] `openclaw gateway status` devuelve `RPC probe: ok`
- [x] `openclaw doctor` termina correctamente
- [x] `memory search` desactivado para simplificar

## Comandos de comprobacion

```powershell
openclaw --version
```

```powershell
openclaw gateway status
```

```powershell
openclaw doctor
```

```powershell
openclaw security audit
```

## Resultado esperado

- [ ] El Gateway aparece como `Scheduled Task (registered)`
- [ ] `RPC probe: ok`
- [ ] `Listening: 127.0.0.1:18789`
- [ ] No hay errores graves de instalacion

## Comandos usados para cerrar la instalacion

```powershell
openclaw gateway install
```

```powershell
openclaw gateway start
```

```powershell
openclaw config set agents.defaults.memorySearch.enabled false
```

## Notas importantes

### Servicio del Gateway

El Gateway ya no depende de arranque manual.

Quedo registrado como tarea programada de Windows.

### Memory search

Se ha desactivado por simplicidad.

No hace falta para usar OpenClaw en esta fase.

### Ubicacion de trabajo

De ahora en adelante, el workspace principal y repo Git seran:

```text
C:\omi\openclaw
```

## Documentos relacionados

- [GUIA_REINSTALACION_WINDOWS.md](/C:/omi/openclaw/docs/legacy/GUIA_REINSTALACION_WINDOWS.md)
- [CHECKLIST_WINDOWS.md](/C:/omi/openclaw/docs/legacy/CHECKLIST_WINDOWS.md)
- [NOTAS_WINDOWS.md](/C:/omi/openclaw/docs/legacy/NOTAS_WINDOWS.md)
