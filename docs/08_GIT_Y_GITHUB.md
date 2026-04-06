# GIT Y GITHUB

## Objetivo

Este documento define como versionar el workspace real con Git y GitHub.

## Repositorio correcto

El repo principal debe ser:

```text
C:\omi\openclaw
```

No debe ser:

```text
C:\omi\openclaw-setup
```

## Por que

Porque en tu caso:

1. solo hay un usuario
2. solo quieres un workspace principal
3. los cambios del workspace y la documentacion deben vivir juntos

## Que entra en Git

Dentro de `C:\omi\openclaw`:

- [ ] `docs\`
- [ ] `skills\` del workspace
- [ ] `prompts\`
- [ ] `templates\`
- [ ] `notes\`
- [ ] `projects\kleinanzeigen-watcher\`

## Que no entra en Git

Fuera de Git:

```text
C:\Users\Omar\.openclaw
```

Motivos:

- [ ] contiene credenciales
- [ ] contiene sesiones
- [ ] contiene estado del gateway
- [ ] contiene configuracion local de la maquina
- [ ] no es portable como repo

## Pasos correctos

### Paso 1. Trabajar en el repo real

```powershell
Set-Location C:\omi\openclaw
```

### Paso 2. Configurar identidad de Git

```powershell
git config --global user.name "omiata"
```

```powershell
git config --global user.email "TU_EMAIL_DE_GITHUB"
```

### Paso 3. Inicializar el repo

```powershell
git init -b main
```

### Paso 4. Crear el primer commit

```powershell
git add .
```

```powershell
git commit -m "chore: bootstrap openclaw workspace"
```

### Paso 5. Crear el repo en GitHub

Crear un repo vacio en GitHub con este nombre recomendado:

```text
openclaw
```

Usuario:

```text
omiata
```

### Paso 6. Conectar el remoto

```powershell
git remote add origin https://github.com/omiata/openclaw.git
```

### Paso 7. Subir el repositorio

```powershell
git push -u origin main
```

## Nota importante sobre autenticacion

GitHub ya no usa contrasena normal para `git push`.

Lo normal en Windows es:

1. login web
2. Git Credential Manager
3. o token personal si hace falta

## Regla simple

Un solo repo principal:

```text
C:\omi\openclaw
```

Un solo remoto principal:

```text
https://github.com/omiata/openclaw.git
```
