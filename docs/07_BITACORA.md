# BITACORA

## 2026-04-06

### Bloque 1. Instalacion base de OpenClaw en Windows

- [x] OpenClaw instalado con el instalador oficial
- [x] OpenAI configurado con OAuth
- [x] Gateway instalado y validado
- [x] `memory search` desactivado para simplificar

### Bloque 2. Telegram

- [x] Telegram emparejado
- [x] pairing aprobado desde PowerShell
- [x] prueba basica funcionando

### Bloque 3. Arquitectura

Arquitectura elegida:

```text
C:\Users\Omar\.openclaw\
C:\omi\openclaw\
C:\omi\openclaw\docs\
C:\omi\openclaw\projects\kleinanzeigen-watcher\
```

### Bloque 4. Siguiente paso pendiente

- [ ] definir identidad del asistente
- [ ] documentar mejor Telegram
- [ ] decidir futuras capacidades de audio
- [ ] dejar preparado el proyecto de Kleinanzeigen cuando toque

## 2026-04-08

### Bloque 5. Decision de migracion a WSL

- [x] Se decide volver a WSL2 como runtime principal de OpenClaw
- [x] Windows nativo queda como instalacion anterior, no como entorno principal
- [x] Se crea guia de migracion: `docs/09_MIGRACION_A_WSL.md`
- [x] Se recuerda crear acceso directo: `wsl.exe -d Ubuntu --cd /mnt/c/omi/openclaw`
