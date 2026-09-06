# PLAN_PRO.md — FIA FLASH SYSTEM HARNESS → PRO (v2)

**Qué es:** plan de desarrollo para convertir este kit (v1, casero pero
verificado con tests) en **FIA FLASH SYSTEM HARNESS PRO**: mismo minimalismo,
pero donde la negligencia sea difícil en vez de improbable.

> **Nota sobre la regla de "no promoción":** esa regla aplica a los *proyectos*
> Flash (no se convierten en Harness completo). Este plan es la evolución de la
> *herramienta* misma — otra cosa distinta.

**Estado del plan:** NO INICIADO — Fase 0 pendiente.
**Tamaño:** S/M/L estimado por complejidad relativa, no por tiempo de calendario.

---

## 0. Dónde estamos hoy (v1)

Inventario: 4 plantillas (`FLASH_START`, `FLASH_SECURITY`, `FLASH_VISIBILIDAD_UX`,
`FLASH_TASK_TEMPLATE`), 2 scripts (`bootstrap_flash.py`, `flash_task.py`),
`README.md` y 11 tests en `tests/` (solo stdlib).

Lo que ya funciona y **se conserva**: bootstrap idempotente, inyección de
checklists por heurística de keywords con `\b`, protección anti-sobrescritura
con `--force`, propagación del criterio de éxito, parser tolerante a guiones,
`.gitkeep`, tests del kit.

Los 6 límites que PRO ataca (en orden de gravedad):

1. El estado vive en Markdown y se parsea con regex — frágil ante cualquier cambio de redacción.
2. La validación se *promete* ("no se inventan resultados") pero nada la ejecuta ni la registra.
3. Las aprobaciones son una "sección para rellenar", sin trazabilidad real.
4. El kit no tiene versión: si mejora, los proyectos viejos envejecen en silencio (drift).
5. La seguridad automatizable (secretos, dependencias) depende de que el agente se acuerde.
6. Cero métricas: no se sabe si el umbral del triage está bien calibrado.

## 1. Principios de PRO (no negociables)

1. **Minimalismo intacto.** PRO no añade botones: hace que fallar sea difícil.
   Si una fase convierte el kit en el Harness completo, está mal diseñada.
2. **Cada promesa se convierte en verificación ejecutable.** Lo que no se puede
   automatizar se registra como decisión manual auditable, nunca como silencio.
3. **Migración sin pérdida.** Todo proyecto v1 debe poder migrarse a v2 con un
   comando, y los scripts v1 siguen funcionando durante la transición.
4. **stdlib-first.** La única dependencia externa permitida es la que una fase
   justifique explícitamente (por defecto: ninguna — JSON de stdlib para el estado).

## 2. Hoja de ruta por fases

### Fase 0 — Fundaciones · tamaño S · sin dependencias

- [ ] Repo git inicializado con `.gitignore` (incluye `__pycache__/`).
- [ ] `CHANGELOG.md` con entrada `v1.0.0 — estado actual del kit`.
- [ ] Versionado semántico declarado (`__version__` en los scripts).
- [ ] CI básico (GitHub Actions): los 11 tests actuales en cada push.

**Criterio de aceptación:** push al repo → CI verde; cada archivo lleva versión.

### Fase 1 — CLI unificado · tamaño M · independiente

- [ ] Un solo entrypoint `flash.py` con subcomandos: `init`, `task`, `done`,
      `status`, `doctor` (los tres últimos pueden ser stubs en esta fase).
- [ ] Códigos de salida documentados en `--help` y en el README.
- [ ] Escritura atómica de archivos en todo el kit (temp + rename).
- [ ] `bootstrap_flash.py` y `flash_task.py` quedan como wrappers deprecados
      que delegan en `flash.py` (no se rompe ningún flujo v1).
- [ ] Los 11 tests actuales pasan sin tocarlos; nuevos tests por subcomando.

**Criterio de aceptación:** todo el flujo actual funciona vía `flash.py`; los
scripts v1 siguen operativos y emiten un aviso de deprecación.

### Fase 2 — Estado estructurado · tamaño L · depende de Fase 1

- [ ] `FLASH_STATE.json` como única fuente de verdad: proyecto, triage,
      tareas (`id`, `título`, `objetivo`, `éxito`, `status`:
      `draft → approved → in_progress → blocked → done | escalated`),
      aprobaciones, versión del kit que lo generó.
- [ ] `FLASH_BRIEF.md` pasa a ser una **vista generada** del estado
      (`flash status --render`), regenerable en cualquier momento.
- [ ] Heurística de keywords movida a configuración dentro del estado
      (editable sin tocar código).
- [ ] `flash doctor --migrate`: parsea un `FLASH_BRIEF.md` v1 y genera el
      estado v2 (los regex se concentran aquí, y solo aquí).
- [ ] La anti-sobrescritura pasa a garantía de estado: `task`/`done` consultan
      el `status`, no la presencia del archivo.

**Criterio de aceptación:** cero regex de parsing de estado fuera de la
migración; un brief v1 real se migra sin pérdida (tests con fixtures reales);
los estados inválidos son imposibles, no solo desaconsejados.

### Fase 3 — Gate de validación ejecutada · tamaño L · depende de Fase 2

- [ ] Cada tarea declara su comando de validación (tests/build) en el estado.
- [ ] `flash done T1` ejecuta ese comando, captura salida, código, fecha y hash
      de los archivos tocados, y lo registra. Sin registro exitoso → la tarea
      no puede pasar a `done`.
- [ ] Escape hatch explícito y auditable: `flash done T1 --manual "justificación"`
      queda registrado como validación manual — nunca silencioso.
- [ ] Los checks automatizables de `FLASH_SECURITY.md` se ejecutan aquí cuando
      la tarea los dispare (ver Fase 4).

**Criterio de aceptación:** mentir sobre la validación exige alterar a mano un
registro append-only con hash — ya no basta con tachar una casilla.

### Fase 4 — Auditoría append-only + seguridad automatizada · tamaño M · depende de Fase 3

- [ ] `AUDIT.log` append-only: cada aprobación, cambio de estado y validación,
      con timestamp, autor y hash del alcance.
- [ ] `flash audit`: gitleaks (secretos) + pip-audit (dependencias) + bandit
      (código), ejecutables y registrables como parte del gate de cierre.
- [ ] Dependencia nueva en una tarea → el estado exige aprobación registrada
      antes de permitir `in_progress`.

**Criterio de aceptación:** cada evento del ciclo deja rastro verificable; el
checklist de seguridad automatizable corre solo, el de juicio humano sigue en prosa.

### Fase 5 — Versionado y distribución · tamaño M · depende de Fase 2

- [ ] Kit instalable (pipx/uv tool) o template repo de GitHub, a elegir.
- [ ] Versión del kit estampada en todo archivo generado (plantillas y estado).
- [ ] `flash doctor`: detecta drift entre versión del kit y proyecto, lista
      diferencias y ofrece migración.
- [ ] `CHANGELOG.md` como parte del release.

**Criterio de aceptación:** un proyecto creado con v1 se detecta, se migra y
`doctor` lo confirma sin pérdida de datos.

### Fase 6 — Métricas, documentación viva y CI completa · tamaño M · depende de Fase 3

- [ ] `flash metrics`: tiempo por tarea, bloqueos y motivos, tasa de escalada
      a Harness completo (el termómetro de calibración del triage).
- [ ] Test de documentación viva: los comandos del README se ejecutan en un
      test real — README roto = CI rojo.
- [ ] CI completa: tests + lint (ruff) + tipos (mypy) sobre el kit.

**Criterio de aceptación:** se puede responder "¿cuántas tareas Flash terminaron
en escalada y por qué?" con un comando; la documentación no puede pudrirse
silenciosamente.

## 3. Resumen

| Fase | Entrega | Tamaño | Depende de |
|---|---|---|---|
| 0 | Repo, versión, changelog, CI básico | S | — |
| 1 | CLI unificado + atomicidad + compat v1 | M | — |
| 2 | Estado en JSON, brief como vista, migración | L | 1 |
| 3 | Gate de validación ejecutada | L | 2 |
| 4 | Auditoría append-only + audit de seguridad | M | 3 |
| 5 | Distribución + doctor + drift | M | 2 |
| 4 y 6 pueden ir en paralelo una vez cerrada la 3 | | | |

## 4. Lo que PRO NO hará (guardarraíles)

- Nada de servidores, base de datos, UI web, ni modo multi-agente en paralelo.
- Ninguna dependencia externa sin justificación escrita en el changelog.
- Ninguna feature que convierta el flujo de 3 comandos en un flujo de 10.
- Si algo necesita más: es el Harness completo, y ahí se queda.

## 5. Definición de hecho (v2.0.0)

- [ ] Fases 0-6 con criterio de aceptación cumplido y testificado por tests.
- [ ] Un proyecto completo (init → task → done → cierre) ejecutable sin leer el código.
- [ ] Migración v1→v2 demostrada con un proyecto real.
- [ ] CI verde con tests + lint + tipos.
- [ ] README y FLASH_START actualizados a la realidad v2 (y verificados por el test de Fase 6).

## 6. Decisiones abiertas (se cierran al iniciar su fase)

1. **Formato del estado:** recomendado JSON de stdlib (round-trip perfecto,
   cero dependencias); YAML solo si la edición humana directa del archivo se
   vuelve un requisito.
2. **Nombre del entrypoint:** `flash` choca con el módulo homónimo de terceros
   en algunos entornos; alternativa: `flashpro` o mantener `python -m flash`.
3. **Distribución:** pipx/uv tool (más profesional) vs template repo (más
   simple de mantener); decidir en Fase 5.
4. **Registro de autoría:** ¿quién firma las aprobaciones — usuario humano del
   config, o git? Decidir en Fase 4.
