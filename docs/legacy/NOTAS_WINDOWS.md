> Documento historico de la fase inicial. La arquitectura actual vive en `docs/02_ARQUITECTURA.md`.

# NOTAS WINDOWS

## Qué estamos haciendo

Estamos dejando OpenClaw instalado en Windows de la forma más simple posible:

1. Windows nativo.
2. PowerShell.
3. Instalador oficial normal.
4. Sin `git`.
5. Con una separación clara entre base funcional y proyecto.

## Arquitectura correcta

### `C:\omi\openclaw`

Esta carpeta será el workspace base de OpenClaw.

Aquí pueden ir más adelante:

- [ ] `skills\` del workspace
- [ ] extras reutilizables
- [ ] configuración base
- [ ] notas comunes

### `C:\omi\openclaw-setup`

Esta carpeta es solo para documentación.

Aquí guardamos:

- [ ] guía
- [ ] checklist
- [ ] notas

### `C:\omi\kleinanzeigen-watcher`

Esta carpeta será el proyecto futuro.

Aquí deberían ir solo:

- [ ] instrucciones
- [ ] prompts
- [ ] reglas
- [ ] archivos del watcher

## Regla simple

Si algo es reutilizable o forma parte de la base de OpenClaw, va en:

```text
C:\omi\openclaw
```

Si algo es específico del proyecto de Kleinanzeigen, va en:

```text
C:\omi\kleinanzeigen-watcher
```

## Comandos principales

### Instalar OpenClaw

```powershell
& ([scriptblock]::Create((iwr -UseBasicParsing https://openclaw.ai/install.ps1))) -NoOnboard
```

### Hacer onboarding

```powershell
openclaw onboard --install-daemon
```

### Comprobar OpenClaw

```powershell
openclaw --version
```

```powershell
openclaw doctor
```

```powershell
openclaw gateway status
```

## Qué debería pasar al final

- [ ] `openclaw` funciona en PowerShell
- [ ] `openclaw --version` responde
- [ ] `openclaw doctor` se ejecuta
- [ ] `openclaw gateway status` devuelve estado
- [ ] el Gateway aparece como `Scheduled Task (registered)`
- [ ] `RPC probe: ok`
- [ ] `C:\omi\openclaw` queda como base funcional
- [ ] `C:\omi\kleinanzeigen-watcher` queda como proyecto separado

## Cómo saber si algo va bien

### Señal 1

```powershell
openclaw --version
```

Si responde, OpenClaw quedó disponible como comando.

### Señal 2

```powershell
openclaw doctor
```

Si arranca y muestra comprobaciones, la instalación base existe.

### Señal 3

```powershell
openclaw gateway status
```

Si devuelve estado, OpenClaw está más cerca de quedar bien montado.

## Errores típicos

### Error: `openclaw` no se reconoce

Haz esto:

1. Cierra PowerShell.
2. Abre PowerShell otra vez.
3. Ejecuta:

```powershell
openclaw --version
```

### Error: fallo al descargar el instalador

Prueba primero:

```powershell
Invoke-WebRequest -UseBasicParsing https://openclaw.ai/install.ps1
```

Si eso falla, el problema suele ser de red, proxy o antivirus.

### Error: falla el onboarding

Vuelve a lanzar:

```powershell
openclaw onboard --install-daemon
```

Después comprueba:

```powershell
openclaw doctor
```

```powershell
openclaw gateway status
```

### Error: el Gateway no instala el servicio por permisos

Si Windows bloquea la tarea programada, abre PowerShell como administrador y ejecuta:

```powershell
openclaw gateway install
```

```powershell
openclaw gateway start
```

Luego comprueba:

```powershell
openclaw gateway status
```

### Error: meter capacidades compartidas dentro del watcher

No lo haremos.

Las capacidades compartidas van en:

```text
C:\omi\openclaw
```

## Actualización más adelante

La forma simple de actualizar después es:

```powershell
openclaw update
```

Después conviene comprobar:

```powershell
openclaw doctor
```

```powershell
openclaw gateway restart
```

```powershell
openclaw health
```

## Recordatorio importante

- [ ] No mezclar OpenClaw con el watcher futuro
- [ ] No usar `C:\omi\openclaw-setup` como instalación real
- [ ] No meter skills compartidas en `C:\omi\kleinanzeigen-watcher`
- [ ] No empezar todavía Kleinanzeigen

## Estado real actual

- [x] OpenClaw instalado con `npm`
- [x] Gateway funcionando como `Scheduled Task`
- [x] `memory search` desactivado para simplificar
- [x] Workspace base: `C:\omi\openclaw`
