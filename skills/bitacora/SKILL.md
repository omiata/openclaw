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

### Guardado mínimo (Fase 1)

Script disponible:
- `scripts/save_entry.py`

Ejemplo:
```bash
python3 skills/bitacora/scripts/save_entry.py \
  --project camper \
  --category aislamiento \
  --content "Panel XPS para suelo y paredes"
```

Tests de Fase 1:
- `scripts/test_phase1.py`

Ejemplo:
```bash
python3 skills/bitacora/scripts/test_phase1.py
```

### Lectura y listado básico (Fase 2)

Script disponible:
- `scripts/read_entries.py`

Ejemplos:
```bash
python3 skills/bitacora/scripts/read_entries.py --project camper
python3 skills/bitacora/scripts/read_entries.py --project camper --category Aislamiento
```

Tests de Fase 2:
- `scripts/test_phase2.py`

Ejemplo:
```bash
python3 skills/bitacora/scripts/test_phase2.py
```
