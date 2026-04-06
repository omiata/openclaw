> Documento historico de la fase inicial. La arquitectura actual vive en `docs/02_ARQUITECTURA.md`.

# CHECKLIST WINDOWS OPENCLAW

## Objetivo

Usa esta checklist como versión corta de la guía principal.

Marca cada paso cuando esté hecho.

## Estructura final esperada

```text
C:\omi\
├── openclaw\
├── openclaw-setup\
└── kleinanzeigen-watcher\
```

## Regla de arquitectura

- [ ] `C:\omi\openclaw` será la base funcional de OpenClaw
- [ ] `C:\omi\kleinanzeigen-watcher` será solo el proyecto y sus instrucciones

## Fase 1. Preparación

- [ ] Abrir PowerShell
- [ ] Crear carpetas base

```powershell
New-Item -ItemType Directory -Force -Path C:\omi | Out-Null
New-Item -ItemType Directory -Force -Path C:\omi\openclaw | Out-Null
New-Item -ItemType Directory -Force -Path C:\omi\openclaw-setup | Out-Null
New-Item -ItemType Directory -Force -Path C:\omi\kleinanzeigen-watcher | Out-Null
```

### Qué debería pasar

- [ ] Las carpetas existen en `C:\omi`

### Cómo comprobarlo

```powershell
Get-ChildItem C:\omi
```

## Fase 2. Comprobaciones previas

- [ ] Comprobar PowerShell

```powershell
$PSVersionTable.PSVersion
```

### Qué debería pasar

- [ ] PowerShell es versión 5 o superior

## Fase 3. Instalar OpenClaw

- [ ] Ejecutar el instalador oficial

```powershell
& ([scriptblock]::Create((iwr -UseBasicParsing https://openclaw.ai/install.ps1))) -NoOnboard
```

- [ ] Comprobar el comando `openclaw`

```powershell
openclaw --version
```

### Qué debería pasar

- [ ] `openclaw --version` responde

### Errores típicos

#### Error: `openclaw` no se reconoce

- [ ] Cerrar PowerShell
- [ ] Abrir PowerShell otra vez
- [ ] Repetir `openclaw --version`

#### Error: problema al descargar el instalador

```powershell
Invoke-WebRequest -UseBasicParsing https://openclaw.ai/install.ps1
```

## Fase 4. Onboarding

- [ ] Ejecutar el onboarding

```powershell
openclaw onboard --install-daemon
```

### Qué debería pasar

- [ ] Se abre el asistente
- [ ] Termina la configuración inicial
- [ ] Se intenta instalar el arranque de OpenClaw

### Cómo comprobarlo

```powershell
openclaw doctor
```

```powershell
openclaw gateway status
```

## Fase 5. Workspace base

- [ ] Reservar `C:\omi\openclaw` como workspace base
- [ ] Usar esa carpeta para OpenClaw a nivel general
- [ ] Dejar skills y extras para más adelante si hacen falta
- [ ] No usar `C:\omi\kleinanzeigen-watcher` para eso

## Fase 6. Verificación final

- [ ] `openclaw --version`

```powershell
openclaw --version
```

- [ ] `openclaw doctor`

```powershell
openclaw doctor
```

- [ ] `openclaw gateway status`

```powershell
openclaw gateway status
```

### Instalación correcta si todo esto se cumple

- [ ] `openclaw` existe en PowerShell
- [ ] `openclaw --version` responde
- [ ] `openclaw doctor` funciona
- [ ] `openclaw gateway status` funciona
- [ ] el Gateway aparece como `Scheduled Task (registered)`
- [ ] `RPC probe: ok`
- [ ] `C:\omi\openclaw` queda como base funcional
- [ ] `C:\omi\kleinanzeigen-watcher` queda como proyecto aparte

## Estado final de este primer paso

- [x] OpenClaw instalado
- [x] Onboarding completado
- [x] Gateway arreglado con permisos de PowerShell
- [x] Gateway registrado como `Scheduled Task`
- [x] `memory search` desactivado

## No hacer todavía

- [ ] No empezar aún el proyecto de Kleinanzeigen
- [ ] No meter skills compartidas en `C:\omi\kleinanzeigen-watcher`
- [ ] No usar `C:\omi\openclaw-setup` como instalación real

## Orden corto

1. Crear carpetas.
2. Verificar PowerShell.
3. Instalar OpenClaw.
4. Ejecutar onboarding.
5. Reservar `C:\omi\openclaw` como base funcional.
6. Ejecutar comprobaciones finales.
