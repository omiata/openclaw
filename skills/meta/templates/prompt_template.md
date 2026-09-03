# Prompt para [Agent]: implementar skill [skill] (v[X.Y] — Trabajo por Bloques)

> Los principios de diseño que dan forma a este prompt están documentados en:
> `skills/meta/PROMPT_ENGINEERING.md` — leer antes de adaptar este patrón.

Usa este prompt una vez por **BLOQUE**. Sustituye el `[N]` del bloque en el PASO 2 en cada sesión nueva.

---

## Prompt base (copiar y pegar en [Agent])

```text
Tienes que implementar la versión [X.Y] de la skill [skill].
Estaremos trabajando por BLOQUES lógicos consecutivos.

Los documentos de referencia v[X.Y] están en:
[ruta base de referencia — p.ej. /mnt/c/omi/openclaw/skills/[skill]/ref/]

PASO 1 — Lee estos archivos ANTES de hacer absolutamente nada más.
Considéralos tu única fuente de verdad durante toda la sesión:
- [skill]_reglas.md  ← léelo primero. Son restricciones obligatorias.
- [skill]_fases.md
- [skill]_maestro.md

PASO 2 — Implementa únicamente el Bloque [N].
Busca su definición en [skill]_fases.md, bajo la sección de "Agrupación por bloques".
- Ejecuta las fases del bloque en orden.
- Respeta estrictamente el SCOPE de archivos definido para el bloque.
- Aplica el criterio de BACKUP indicado.
- Asegúrate de pasar todos los tests listados en la fase. 
En caso de conflicto entre lo más cómodo y las reglas, ganan las reglas.

PASO 3 — Reglas de ejecución universales:
1. No necesito ver tu razonamiento interno. Sí necesito un log de progreso al
   terminar cada subpaso con el formato [ESTADO] (fase, subpaso, decisión, bloqueo).
2. Si pasan 2 minutos sin avance real: para, resume, propón 2 opciones.
3. Máximo 2 intentos distintos para resolver el mismo bloqueo o test fallido.
   Si sigue sin resolverse: para y reporta.

PASO 4 — Cierre del bloque:
Cuando todas las fases del bloque pasen todos sus tests (ver regla de testing):
1. Imprímeme un reporte estructurado final (formato del Apéndice A.6 de fases).
2. Añade ese mismo reporte haciendo append al log: [ruta]/[skill]_log.md 
3. Añade una entrada al changelog: [ruta]/[skill]_changelog.md
```

---

## Nota importante
[Agent] no tiene memoria entre sesiones. El PASO 1 de lectura obligatoria previene alucinaciones y contaminación entre desarrollos.
Iniciar sesión nueva (`/new` o equivalente) antes de cada bloque y ajustar el nivel de "Thinking" (Alto/Medio) dependiendo de lo indicado en la fase.
