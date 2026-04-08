# MIGRACION A WSL

## Objetivo

Volver a usar OpenClaw desde WSL2 porque es la ruta mas estable en Windows.

Esta guia esta pensada para:

1. no romper lo que ya existe en Windows
2. instalar OpenClaw de nuevo dentro de WSL
3. usar el mismo repo de trabajo
4. probar Telegram y audio en un entorno Linux
5. decidir despues si limpiar la instalacion nativa de Windows

## Decision

Vamos a usar WSL2 como runtime real de OpenClaw.

Windows nativo queda como instalacion anterior, pero no como entorno principal.

## Arquitectura

```text
Windows
C:\omi\openclaw\                         <- repo y documentacion
C:\Users\Omar\.openclaw\                 <- config anterior de Windows, no copiar a WSL

WSL
/mnt/c/omi/openclaw/                     <- mismo repo visto desde WSL
~/.openclaw/                             <- config real de OpenClaw en WSL
```

## Regla importante

No copiar:

```text
C:\Users\Omar\.openclaw
```

a:

```text
~/.openclaw
```

Son configuraciones distintas.

## Fase 1. Parar OpenClaw en Windows

### Paso 1. Parar el Gateway de Windows

En PowerShell de Windows:

```powershell
schtasks /End /TN "OpenClaw Gateway"
```

### Paso 2. Desactivar el autoarranque temporalmente

```powershell
schtasks /Change /TN "OpenClaw Gateway" /DISABLE
```

### Que deberia pasar

- [ ] el Gateway nativo de Windows deja de competir con WSL
- [ ] no desinstalamos nada todavia

### Como comprobarlo

```powershell
schtasks /Query /TN "OpenClaw Gateway" /FO LIST
```

### Error tipico

#### Error: acceso denegado

Abrir PowerShell como administrador y repetir los comandos.

## Fase 2. Abrir WSL en el workspace correcto

### Paso 3. Abrir WSL

Desde Windows:

```powershell
wsl
```

### Paso 4. Ir al repo de OpenClaw

Dentro de WSL:

```bash
cd /mnt/c/omi/openclaw
```

### Que deberia pasar

Estas dentro del mismo repo que usamos en Windows.

### Como comprobarlo

```bash
pwd
```

```bash
ls
```

Deberias ver:

```text
docs
projects
README.md
```

## Fase 3. Comprobar WSL

### Paso 5. Comprobar version de WSL

En PowerShell de Windows:

```powershell
wsl -l -v
```

### Que deberia pasar

Tu distribucion, normalmente Ubuntu, deberia aparecer como WSL2.

### Error tipico

#### Error: aparece WSL1

Primero habria que convertir o reinstalar como WSL2 antes de seguir.

## Fase 4. Instalar OpenClaw dentro de WSL

### Paso 6. Ejecutar el instalador oficial de Linux/WSL

Dentro de WSL:

```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-onboard
```

### Que deberia pasar

1. el instalador detecta Linux/WSL
2. instala Node si hace falta
3. instala OpenClaw
4. deja disponible el comando `openclaw`

### Como comprobarlo

Cierra y abre WSL si hace falta.

Despues:

```bash
openclaw --version
```

```bash
openclaw doctor
```

## Fase 5. Onboarding en WSL

### Paso 7. Ejecutar onboarding

Dentro de WSL:

```bash
cd /mnt/c/omi/openclaw
openclaw onboard --install-daemon
```

### Que deberia pasar

1. OpenClaw configura el entorno de WSL
2. se configura el Gateway dentro de Linux
3. se configura el proveedor de modelo
4. se instala el servicio de usuario si systemd esta disponible

### Como comprobarlo

```bash
openclaw gateway status
```

```bash
openclaw doctor
```

## Fase 6. Probar Telegram

### Paso 8. Probar texto

En Telegram:

```text
test
```

### Que deberia pasar

El bot responde desde el OpenClaw de WSL.

### Paso 9. Probar audio

Enviar una nota de voz corta:

```text
Prueba de audio. Responde solo: audio recibido.
```

### Que deberia pasar

OpenClaw deberia recibir y transcribir el audio.

Si falla, en WSL revisaremos:

```bash
which ffmpeg
```

```bash
ffmpeg -version
```

```bash
which whisper
```

```bash
whisper --help
```

## Fase 7. Acceso directo desde Windows

### Objetivo

Crear un acceso directo para abrir WSL directamente en el workspace correcto.

### Comando base

En el acceso directo de Windows:

```text
wsl.exe -d Ubuntu --cd /mnt/c/omi/openclaw
```

### Si la distro no se llama Ubuntu

Comprobar nombre:

```powershell
wsl -l -v
```

Y cambiar `Ubuntu` por el nombre real.

### Regla

Recordar esto para mas tarde:

```text
OpenClaw WSL = wsl.exe -d Ubuntu --cd /mnt/c/omi/openclaw
```

## Fase 8. No desinstalar Windows todavia

### Decision

No desinstalar OpenClaw de Windows hasta que WSL este validado.

### Criterio para limpiar Windows

Solo limpiar Windows cuando:

- [ ] OpenClaw funciona en WSL
- [ ] Telegram funciona en WSL
- [ ] audio funciona en WSL o queda una ruta clara
- [ ] el Gateway de WSL arranca correctamente
- [ ] la documentacion esta actualizada

## Fuentes oficiales

Referencias verificadas el 8 de abril de 2026:

1. [Windows - OpenClaw](https://docs.openclaw.ai/platforms/windows)
2. [Install - OpenClaw](https://docs.openclaw.ai/install)
3. [Installer Internals - OpenClaw](https://docs.openclaw.ai/install/installer)
4. [Getting Started - OpenClaw](https://docs.openclaw.ai/start/getting-started)
