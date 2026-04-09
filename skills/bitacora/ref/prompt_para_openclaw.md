# Prompt para OpenClaw: implementar skill bitacora

Usa este prompt una vez por fase. Cambia únicamente el número de fase en cada sesión.

---

## Prompt (copiar y pegar en OpenClaw)

```
Tienes que implementar la skill bitacora.

Los documentos de referencia están en:
/mnt/c/omi/openclaw/skills/bitacora/ref/

PASO 1 — Lee estos tres archivos antes de hacer absolutamente nada más:
- bitacora_reglas.md  ← léelo primero y trátalo como restricciones obligatorias durante toda la sesión
- bitacora_fases.md
- bitacora_maestro.md

PASO 2 — Implementa únicamente la Fase 0 del plan de fases.
Cada decisión que tomes debe ser compatible con bitacora_reglas.md. Si hay conflicto entre lo que parece conveniente y una regla, gana la regla.

PASO 3 — Reglas de ejecución durante esta sesión:

1. No necesito tu razonamiento interno.
2. Sí necesito un log de progreso breve mientras trabajas.
3. Cada 60-90 segundos, o al completar un subpaso, informa con este formato:
   [ESTADO]
   - fase actual:
   - subpaso actual:
   - archivos inspeccionados/modificados:
   - decisión tomada:
   - siguiente paso:
   - bloqueo detectado: sí/no

4. Si pasan 2 minutos sin avance real, no sigas explorando en silencio:
   - para,
   - resume el bloqueo,
   - propone como máximo 2 opciones compatibles con bitacora_reglas.md,
   - elige la más simple si las reglas ya permiten decidir.

5. No entres en loops:
   - máximo 2 intentos para resolver el mismo bloqueo,
   - si tras 2 intentos no se resuelve, reporta y sigue solo si hay una opción claramente segura,
   - si no la hay, para y reporta.

PASO 4 — Cuando termines la fase:
1. Dame el reporte estructurado definido en el Apéndice A.6.
2. Guarda ese mismo reporte en el archivo de log de la skill:
   /mnt/c/omi/openclaw/skills/bitacora/ref/bitacora_log.md
   - Si el archivo no existe, créalo.
   - Si ya existe, añade el nuevo reporte al final sin borrar los anteriores.
   - Cada entrada del log debe empezar con la fecha y hora exacta del reporte.
   - No modifiques ninguna entrada anterior del log.
```

---

## Cómo usarlo

1. Copia el bloque de texto de arriba.
2. Pégalo en OpenClaw.
3. Espera el reporte estructurado (Apéndice A.6).
4. Revisa el reporte. Si el estado es COMPLETADA, pasa a la siguiente fase.
5. Para la siguiente fase, repite el mismo prompt cambiando **Fase 0** por **Fase 1**, y así sucesivamente.

## Fases disponibles y nivel de thinking recomendado

| Fase | Nombre | Thinking | Motivo |
|------|--------|----------|--------|
| 0 | Preparación y decisiones de ruta | Medio | Tarea concreta y bien especificada |
| 1 | Guardado mínimo funcional | Medio | Lógica simple, sin ambigüedad |
| 2 | Lectura y listado básico | Medio | Parseo y filtrado bien definidos |
| 3 | Campos estructurados completos | Alto | Requiere generar títulos y resúmenes con criterio, e inferir tipos |
| 4 | Búsqueda textual sencilla | Medio | Búsqueda simple, sin ranking complejo |
| 5 | Duplicados básicos y pulido | Medio | Lógica de comparación bien acotada |
| 6 | Índices y mejoras secundarias | Alto | Decisiones de diseño sobre estructura derivada |

## Nota importante

OpenClaw no tiene memoria entre sesiones. Por eso el prompt siempre empieza pidiendo que lea los tres archivos de referencia. No omitas esa parte aunque ya hayas hecho fases anteriores.
