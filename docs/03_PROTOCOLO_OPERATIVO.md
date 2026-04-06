# PROTOCOLO OPERATIVO

## Objetivo

Este protocolo sirve para no perder orden a medida que anadamos mas funciones.

## Regla principal

Cada cambio importante debe quedar documentado en Markdown.

## Como nos organizamos

### Cambios de instalacion o sistema

Se documentan en:

- [01_INSTALACION_WINDOWS.md](/C:/omi/openclaw/docs/01_INSTALACION_WINDOWS.md)
- [07_BITACORA.md](/C:/omi/openclaw/docs/07_BITACORA.md)

### Cambios de arquitectura

Se documentan en:

- [02_ARQUITECTURA.md](/C:/omi/openclaw/docs/02_ARQUITECTURA.md)
- [07_BITACORA.md](/C:/omi/openclaw/docs/07_BITACORA.md)

### Cambios de comportamiento del asistente

Se documentan en:

- [04_IDENTIDAD_ASISTENTE.md](/C:/omi/openclaw/docs/04_IDENTIDAD_ASISTENTE.md)
- [07_BITACORA.md](/C:/omi/openclaw/docs/07_BITACORA.md)

### Cambios de Telegram

Se documentan en:

- [05_TELEGRAM.md](/C:/omi/openclaw/docs/05_TELEGRAM.md)
- [07_BITACORA.md](/C:/omi/openclaw/docs/07_BITACORA.md)

### Cambios de skills o capacidades

Se documentan en:

- [06_CAPACIDADES_Y_SKILLS.md](/C:/omi/openclaw/docs/06_CAPACIDADES_Y_SKILLS.md)
- [07_BITACORA.md](/C:/omi/openclaw/docs/07_BITACORA.md)

## Protocolo para cada cambio

1. Decidir si el cambio es global, de workspace, de documentacion o de proyecto.
2. Hacer el cambio tecnico.
3. Comprobar que funciona.
4. Escribir el cambio en el `.md` correcto.
5. Anadir una entrada corta en la bitacora.

## Regla de comprobacion

Despues de un cambio importante, comprobar siempre lo minimo:

```powershell
openclaw gateway status
```

```powershell
openclaw doctor
```

## Regla de simplicidad

- [ ] una sola ruta recomendada
- [ ] no abrir caminos alternativos si no hacen falta
- [ ] no instalar extras sin una necesidad clara
- [ ] no mezclar sistema con proyecto

## Cierre de bloque

Un bloque se da por terminado cuando:

- [ ] el cambio funciona
- [ ] esta documentado
- [ ] la bitacora esta actualizada
- [ ] sabemos cual es el siguiente paso
