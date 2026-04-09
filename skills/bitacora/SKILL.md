# Skill: bitacora

Knowledge base personal para gestionar recursos de proyectos.

## Descripción

Bitácora permite guardar y consultar recursos (links, videos, notas, ideas) asociados a proyectos personales. Cada proyecto tiene su propio archivo de datos en formato Markdown con estructura YAML.

## Uso

### Guardar
- "guarda esto en camper, categoría aislamiento"
- "añade esta idea a camper en electricidad"

### Consultar
- "enséñame camper"
- "enséñame camper, categoría aislamiento"
- "busca en camper: cama plegable"

## Ubicación

- **Código:** `skills/bitacora/`
- **Datos:** `skills/bitacora/data/` (un archivo `.md` por proyecto)
- **Referencias:** `skills/bitacora/ref/`

## Proyectos soportados

La skill es genérica. El usuario puede crear proyectos nuevos indicando el nombre.

Ejemplos: `camper`, `balcon`, `poesia`, `bicicleta`

## Estado de implementación

Ver `ref/bitacora_fases.md` para el plan de desarrollo por fases.

## Implementación disponible

### Guardado, deduplicación y actualización explícita (Fases 1, 3 y 5)

Script disponible:
- `scripts/save_entry.py`

Ejemplos:
```bash
python3 skills/bitacora/scripts/save_entry.py \
  --project camper \
  --category aislamiento \
  --content "Panel XPS para suelo y paredes"

python3 skills/bitacora/scripts/save_entry.py \
  --project camper \
  --category iluminacion \
  --content "https://example.com/guia-luces-led-camper" \
  --source "https://example.com/guia-luces-led-camper" \
  --tag led \
  --tag 12v \
  --additional-content "Comparar tiras LED y focos empotrables"

python3 skills/bitacora/scripts/save_entry.py \
  --project camper \
  --update-source-url "https://example.com/guia-luces-led-camper" \
  --tag interiores \
  --additional-content "Revisar diferencias entre CRI y temperatura de color"
```

Tests:
- `scripts/test_phase1.py`
- `scripts/test_phase3.py`
- `scripts/test_phase5.py`

Ejemplos:
```bash
python3 skills/bitacora/scripts/test_phase1.py
python3 skills/bitacora/scripts/test_phase3.py
```

### Lectura, listado, búsqueda e índices derivados (Fases 2, 4 y 6)

Script disponible:
- `scripts/read_entries.py`

Ejemplos:
```bash
python3 skills/bitacora/scripts/read_entries.py --project camper
python3 skills/bitacora/scripts/read_entries.py --project camper --category Aislamiento
python3 skills/bitacora/scripts/read_entries.py --project camper --search "cama plegable"
python3 skills/bitacora/scripts/read_entries.py --project camper --entry-id entry-1712613864123
python3 skills/bitacora/scripts/read_entries.py --project camper --overview
python3 skills/bitacora/scripts/read_entries.py --global-stats
```

Tests:
- `scripts/test_phase2.py`
- `scripts/test_phase4.py`
- `scripts/test_phase6.py`

Ejemplos:
```bash
python3 skills/bitacora/scripts/test_phase2.py
python3 skills/bitacora/scripts/test_phase4.py
python3 skills/bitacora/scripts/test_phase6.py
```

## Estado actual

- Fase 1 implementada y validada.
- Fase 2 implementada y validada.
- Fase 3 implementada con soporte para `fuente`, `tags`, `contenido_adicional`, tipo explícito y generación de título y resumen.
- Fase 4 implementada con búsqueda textual simple en título, resumen, tags y contenido adicional, además de consulta por `id` para ver una entrada completa.
- Fase 5 implementada con detección de duplicados por URL exacta, bloqueo de append duplicado, actualización explícita sin cambiar `id` ni `fecha`, y avisos más claros ante categorías ambiguas.
- Fase 6 implementada con `--overview` por proyecto, índices dinámicos de categorías y tipos, y `--global-stats` agregadas, siempre derivadas del listado maestro de entradas.
