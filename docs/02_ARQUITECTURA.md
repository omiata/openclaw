# ARQUITECTURA

## Objetivo

Esta arquitectura esta pensada para:

1. Windows nativo
2. un solo usuario
3. maxima claridad
4. documentacion local en Markdown
5. separar OpenClaw del proyecto futuro

## Arquitectura elegida

```text
C:\Users\Omar\.openclaw\                          <- configuracion global real de OpenClaw
C:\omi\openclaw\                                  <- repo Git principal y workspace unico
C:\omi\openclaw\docs\                             <- documentacion y bitacora
C:\omi\openclaw\projects\kleinanzeigen-watcher\   <- proyecto futuro
```

## Que va en cada sitio

### `C:\Users\Omar\.openclaw`

Aqui vive el estado global real de OpenClaw.

Ejemplos:

- [ ] config global
- [ ] auth
- [ ] gateway
- [ ] sesiones
- [ ] skills compartidas globales si algun dia hacen falta

### `C:\omi\openclaw`

Este sera el repo Git principal y el workspace principal.

Aqui ira lo reutilizable a nivel de trabajo diario.

Ejemplos:

- [ ] `skills\` del workspace
- [ ] `prompts\`
- [ ] `templates\`
- [ ] `notes\`
- [ ] `projects\`

### `C:\omi\openclaw\docs`

Aqui va toda la documentacion.

Ejemplos:

- [ ] guias
- [ ] protocolo
- [ ] decisiones
- [ ] bitacora

### `C:\omi\openclaw\projects\kleinanzeigen-watcher`

Aqui ira solo el proyecto futuro.

Ejemplos:

- [ ] objetivo del proyecto
- [ ] reglas
- [ ] prompts del watcher
- [ ] archivos propios del watcher

## Regla de decision

### Si algo es global de OpenClaw

Va en:

```text
C:\Users\Omar\.openclaw
```

### Si algo es reusable en tu trabajo diario con OpenClaw

Va en:

```text
C:\omi\openclaw
```

### Si algo es documentacion

Va en:

```text
C:\omi\openclaw\docs
```

### Si algo es solo del watcher

Va en:

```text
C:\omi\openclaw\projects\kleinanzeigen-watcher
```

## Lo que no vamos a hacer

- [ ] no mover la instalacion de `npm`
- [ ] no mover a mano el contenido interno de `C:\Users\Omar\.openclaw`
- [ ] no meter la documentacion fuera del repo principal
- [ ] no dejar el watcher fuera del repo si depende del mismo workspace
- [ ] no usar `C:\WINDOWS\System32` como carpeta de trabajo

## Regla practica

Cuando trabajes con OpenClaw como base general, usa:

```powershell
Set-Location C:\omi\openclaw
```

Cuando llegue el proyecto de Kleinanzeigen, usa:

```powershell
Set-Location C:\omi\openclaw\projects\kleinanzeigen-watcher
```

## Nota importante sobre Git

El repo principal sera:

```text
C:\omi\openclaw
```

No versionaremos:

```text
C:\Users\Omar\.openclaw
```

porque ahi hay estado real de la maquina, credenciales, sesiones, gateway y otros datos locales.
