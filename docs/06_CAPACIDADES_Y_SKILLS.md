# CAPACIDADES Y SKILLS

## Estado actual

OpenClaw ya funciona, pero todavia no vamos a instalar skills extra sin necesidad clara.

## Regla actual

- [x] no instalar skills por probar
- [x] anadir skills solo cuando aporten una funcion concreta
- [x] documentar cada skill nueva

## Capacidades ya resueltas

- [x] OpenAI con OAuth
- [x] Gateway funcionando
- [x] Telegram basico funcionando

## Capacidades pendientes para mas adelante

- [ ] audio en Telegram
- [ ] transcripcion de audio
- [ ] respuesta por voz si hace falta
- [ ] automatizaciones concretas
- [ ] watcher de Kleinanzeigen

## Skills

### Estado

No se ha decidido instalar ninguna skill extra por ahora.

### Criterio

Una skill solo se instala si cumple estas dos condiciones:

1. resuelve una necesidad real
2. sabemos en que carpeta debe vivir y como documentarla

## Donde iran las skills

### Skills globales de OpenClaw

Si algun dia hacen falta para todo el sistema:

```text
C:\Users\Omar\.openclaw\skills
```

### Skills del workspace principal

Si son propias de tu trabajo diario en el workspace:

```text
C:\omi\openclaw\skills
```

### Skills del watcher

Solo si algun dia fueran especificas de ese proyecto:

```text
C:\omi\openclaw\projects\kleinanzeigen-watcher\skills
```

## Regla importante

No instalar skills en una carpeta rara distinta a la convencion.
