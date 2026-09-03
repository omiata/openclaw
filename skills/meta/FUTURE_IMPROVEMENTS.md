# Futuras Mejoras, Ideas y Próximos Pasos

Este documento sirve como recolección de ideas, lecciones aprendidas y mejoras de orquestación que se deben implementar en futuras versiones, sin romper la metodología actual que ya está funcionando de forma estable.

## Lecciones Aprendidas (Lessons Learned)

### 1. El Scope bloquea los comandos Git de OpenClaw
- **Contexto:** En el Bloque 1 (Fase 7), OpenClaw completó la migración y los tests correctamente, pero no ejecutó el comando `git commit` a pesar de que la regla de hacer un commit por fase exitosa estaba configurada.
- **Razón:** El agente fue increíblemente obediente al "Scope estricto" que definimos (que le prohibía tocar nada fuera de sus scripts y el archivo `camper.md`). Al no estar explícitamente permitida la carpeta oculta `.git/` o la ejecución de comandos git, OpenClaw se auto-censuró y priorizó el scope.

## Próximos Pasos a Automatizar (Next Steps / New Ideas)

### Automatización de Commits por OpenClaw
- **Objetivo:** Quiero que OpenClaw retome la capacidad de hacer `git commit` automáticamente por sí solo DESPUÉS de que cada fase sea completada con éxito.
- **Solución futura a explorar:** Para las nuevas skills o iteraciones futuras, habrá que encontrar una manera de inyectar en el prompt base de OpenClaw (o en los Scope explícitos de la fase) una excepción global que le diga: *"La ejecución de comandos de versionado (`git add`, `git commit`) no cuenta como una violación del scope."* 
- **Alternativa:** Añadir una directriz explicita en las Reglas de Oro indicando que el repositorio Git de la carpeta actual siempre se asume dentro del ámbito permitido de ejecución CLI para la generación técnica del changelog/commit, aunque su directorio `.git/` no se liste en el archivo del prompt.

### Notificaciones push por Telegram para procesos desatendidos
- **Objetivo:** Que OpenClaw avise automáticamente al móvil (Telegram) cuando un bloque se completa con éxito, falla irremediablemente, o si requiere interacción humana para salir de un bloqueo.
- **Implementación sugerida:** Por definir. Seguramente pase por configurar un bot/script CLI local simple (`tools/telegram_notify`) y añadir al "PASO 3 - Reglas de ejecución" del prompt una directriz para que lo dispare ante ciertos hitos.
