> Documento historico de la fase inicial. La arquitectura actual vive en `docs/02_ARQUITECTURA.md`.

# GUIA REINSTALACION OPENCLAW EN WINDOWS

## Estructura simple de archivos

Usaremos esta estructura y no mezclaremos cosas:

```text
C:\omi\
├── openclaw\                  <- workspace base de OpenClaw
├── openclaw-setup\            <- este proyecto, solo documentación
└── kleinanzeigen-watcher\     <- proyecto futuro, solo instrucciones
```

## Objetivo de esta guía

Esta guía sirve para:

1. Instalar OpenClaw en Windows con la forma oficial más simple.
2. Usar PowerShell con comandos exactos.
3. Dejar OpenClaw instalado globalmente y usar `C:\omi\openclaw` como base funcional.
4. Separar OpenClaw de `C:\omi\kleinanzeigen-watcher`.
5. Comprobar que la instalación quedó bien.
6. No empezar todavía con Kleinanzeigen.

## Arquitectura elegida

Solo vamos a usar una arquitectura:

1. OpenClaw se instala globalmente con el instalador oficial.
2. `C:\omi\openclaw` será el workspace base de OpenClaw.
3. En `C:\omi\openclaw` irán skills, plugins y extras reutilizables.
4. `C:\omi\kleinanzeigen-watcher` será un proyecto separado.
5. En `C:\omi\kleinanzeigen-watcher` irán solo instrucciones y archivos del watcher.

## Importante antes de empezar

### Qué significa `C:\omi\openclaw`

OpenClaw se instala como programa global y después tú trabajas con él dentro de un workspace base.

En esta guía:

```powershell
openclaw
```

será el comando disponible en PowerShell, y:

```text
C:\omi\openclaw
```

será tu workspace base para cosas reutilizables de OpenClaw.

### Qué debería ir en `C:\omi\openclaw`

Aquí sí pueden ir cosas como:

- [ ] skills compartidas
- [ ] plugins compartidos
- [ ] configuración base
- [ ] notas técnicas de OpenClaw
- [ ] recursos reutilizables para varios proyectos

### Qué no debería ir en `C:\omi\kleinanzeigen-watcher`

Aquí no queremos meter la base funcional de OpenClaw.

Aquí solo deberían ir cosas del proyecto, por ejemplo:

- [ ] instrucciones
- [ ] prompts
- [ ] reglas del watcher
- [ ] notas del proyecto
- [ ] archivos propios de Kleinanzeigen

### Nota importante sobre Windows

La documentación oficial de OpenClaw indica que WSL2 suele ser más estable, pero aquí elegimos Windows nativo porque tú quieres simplificar y hacerlo todo en Windows.

## Fase 1. Preparar carpetas

### Paso 1. Crear la estructura base

Abre PowerShell y ejecuta:

```powershell
New-Item -ItemType Directory -Force -Path C:\omi | Out-Null
New-Item -ItemType Directory -Force -Path C:\omi\openclaw | Out-Null
New-Item -ItemType Directory -Force -Path C:\omi\openclaw-setup | Out-Null
New-Item -ItemType Directory -Force -Path C:\omi\kleinanzeigen-watcher | Out-Null
```

### Qué debería pasar

1. Las carpetas quedan creadas.
2. Si ya existían, no pasa nada grave.

### Cómo comprobarlo

```powershell
Get-ChildItem C:\omi
```

### Errores típicos

#### Error: acceso denegado

Revisa permisos de `C:\omi` o prueba desde una sesión de PowerShell normal con permisos correctos de tu usuario.

#### Error: la carpeta ya existe

No es un problema. `-Force` lo permite.

## Fase 2. Comprobar PowerShell

### Paso 2. Verificar PowerShell

```powershell
$PSVersionTable.PSVersion
```

### Qué debería pasar

Deberías ver una versión de PowerShell válida. La documentación del instalador indica PowerShell 5 o superior.

### Cómo comprobarlo

Mira el valor `Major`. Debe ser `5` o más.

### Errores típicos

#### Error: PowerShell demasiado antiguo

Si PowerShell no cumple, conviene actualizarlo antes de seguir.

## Fase 3. Instalar OpenClaw con el instalador oficial

### Paso 3. Ejecutar la instalación oficial

Ejecuta exactamente esto en PowerShell:

```powershell
& ([scriptblock]::Create((iwr -UseBasicParsing https://openclaw.ai/install.ps1))) -NoOnboard
```

### Qué debería pasar

1. El instalador oficial se descarga.
2. Comprueba Node.js.
3. Instala OpenClaw globalmente.
4. El comando `openclaw` queda disponible en PowerShell.

### Cómo comprobarlo

```powershell
openclaw --version
```

### Resultado esperado

Deberías ver una versión de OpenClaw.

### Errores típicos

#### Error: fallo al descargar el instalador

Prueba primero:

```powershell
Invoke-WebRequest -UseBasicParsing https://openclaw.ai/install.ps1
```

Si esto falla, el problema suele ser de red, proxy o antivirus.

#### Error: `openclaw` no se reconoce

Haz esto:

1. Cierra PowerShell.
2. Abre PowerShell otra vez.
3. Ejecuta:

```powershell
openclaw --version
```

## Fase 4. Hacer la configuración inicial

### Paso 4. Lanzar el onboarding

Cuando la instalación termine, ejecuta:

```powershell
openclaw onboard --install-daemon
```

### Qué debería pasar

1. Se abre el asistente de configuración.
2. Eliges proveedor y acceso.
3. Se configura el Gateway.
4. Se intenta instalar el arranque gestionado en Windows.
5. Al final deberías tener OpenClaw listo para usar.

### Cómo comprobarlo

Cuando termine:

```powershell
openclaw doctor
```

Y después:

```powershell
openclaw gateway status
```

### Errores típicos

#### Error: falla el onboarding

Vuelve a ejecutar:

```powershell
openclaw onboard --install-daemon
```

#### Error: el gateway no queda bien

Prueba:

```powershell
openclaw gateway install
```

Y después:

```powershell
openclaw gateway start
```

Y comprueba:

```powershell
openclaw gateway status
```

## Fase 5. Preparar el workspace base de OpenClaw

### Paso 5. Usar `C:\omi\openclaw` como workspace base

A partir de ahora, esta carpeta será tu workspace principal de OpenClaw en Windows.

No hace falta meter nada más todavía.

Lo importante en esta fase es:

- [ ] reservar `C:\omi\openclaw` como workspace base
- [ ] usar esta carpeta cuando trabajes con OpenClaw a nivel general
- [ ] no mezclar aquí cosas específicas de Kleinanzeigen

### Qué podría ir aquí más adelante

Si en el futuro lo necesitas, aquí podrán ir:

- [ ] `skills\` del workspace base
- [ ] configuración y notas comunes
- [ ] recursos reutilizables para varios proyectos

### Qué debería pasar

Tendrás una base limpia para OpenClaw separada de tus proyectos.

### Cómo comprobarlo

```powershell
Get-ChildItem C:\omi
```

### Error típico

#### Error: guardar skills o extras dentro de `C:\omi\kleinanzeigen-watcher`

No lo haremos.

La base reutilizable va en:

```text
C:\omi\openclaw
```

## Fase 6. Separar OpenClaw del proyecto futuro

### Paso 6. Dejar `C:\omi\kleinanzeigen-watcher` solo para instrucciones

Usaremos esto a partir de ahora:

- [ ] `C:\omi\openclaw` para OpenClaw base
- [ ] `C:\omi\openclaw-setup` para esta documentación
- [ ] `C:\omi\kleinanzeigen-watcher` solo para el proyecto y sus instrucciones

### Qué debería pasar

Tendrás OpenClaw separado del watcher.

### Cómo comprobarlo

```powershell
Get-ChildItem C:\omi
```

### Error típico

#### Error: mezclar la base funcional con el proyecto

No lo haremos.

`C:\omi\openclaw` es la base funcional.

`C:\omi\kleinanzeigen-watcher` es el proyecto.

## Fase 7. Comprobar que quedó bien instalado

### Paso 7. Verificación mínima obligatoria

Ejecuta estos comandos uno por uno:

```powershell
openclaw --version
```

```powershell
openclaw doctor
```

```powershell
openclaw gateway status
```

### Qué debería pasar

1. `openclaw --version` responde.
2. `openclaw doctor` se ejecuta.
3. `openclaw gateway status` muestra estado.

### Cómo comprobarlo

La instalación base se considera correcta si se cumple todo esto:

- [ ] `openclaw` existe en PowerShell
- [ ] `openclaw --version` responde
- [ ] `openclaw doctor` funciona
- [ ] `openclaw gateway status` funciona
- [ ] el Gateway aparece como `Scheduled Task (registered)`
- [ ] `RPC probe: ok`
- [ ] `C:\omi\openclaw` queda reservado como base funcional
- [ ] `C:\omi\kleinanzeigen-watcher` queda separado como proyecto

## Estado real de esta instalación

Estado confirmado en esta máquina el 6 de abril de 2026:

- [x] OpenClaw instalado correctamente
- [x] `openclaw --version` responde
- [x] Gateway registrado como `Scheduled Task`
- [x] `openclaw gateway status` devuelve `RPC probe: ok`
- [x] `openclaw doctor` termina correctamente
- [x] `memory search` quedó desactivado para simplificar

Comandos usados en la comprobación final:

```powershell
openclaw gateway status
```

```powershell
openclaw doctor
```

```powershell
openclaw config set agents.defaults.memorySearch.enabled false
```

## Fase 8. Cómo actualizar OpenClaw más adelante

### Paso 8. Ruta simple para actualizar

La forma simple después es:

```powershell
openclaw update
```

### Qué debería pasar

OpenClaw actualiza la instalación y reinicia lo necesario.

### Cómo comprobarlo

Después de actualizar:

```powershell
openclaw doctor
```

```powershell
openclaw gateway restart
```

```powershell
openclaw health
```

## Resumen rápido

El orden correcto es este:

1. Crear carpetas en `C:\omi`.
2. Verificar PowerShell.
3. Instalar OpenClaw con `install.ps1`.
4. Ejecutar `openclaw onboard --install-daemon`.
5. Usar `C:\omi\openclaw` como base funcional.
6. Reservar `C:\omi\kleinanzeigen-watcher` para instrucciones del proyecto.
7. Verificar con `openclaw doctor`.
8. Verificar con `openclaw gateway status`.

## Fuentes oficiales usadas para esta guía

Referencias verificadas el 6 de abril de 2026:

1. [Install - OpenClaw](https://docs.openclaw.ai/install)
2. [Installer Internals - OpenClaw](https://docs.openclaw.ai/install/installer)
3. [Windows - OpenClaw](https://docs.openclaw.ai/platforms/windows)
4. [Getting Started - OpenClaw](https://docs.openclaw.ai/start/getting-started)
5. [Updating - OpenClaw](https://docs.openclaw.ai/install/updating)
6. [Doctor - OpenClaw](https://docs.openclaw.ai/doctor)
