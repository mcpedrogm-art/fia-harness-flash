# ESTUDIO_MERCADO.md — ¿Existen herramientas como FIA FLASH?

**Fecha:** septiembre 2026 · **Alcance:** estudio informal de escritorio
(búsqueda web, sin entrevistas). Sirve de base al posicionamiento de la web
(`web/index.html`).

---

## 1. Veredicto en 30 segundos

1. **Por arriba, la categoría está llena.** El "desarrollo guiado por
   especificaciones con IA" explotó en 2025-2026: GitHub Spec Kit, Kiro (AWS),
   OpenSpec, BMAD-METHOD, Claude Task Master, GSD, Agent OS… Todos apuntan a
   proyectos **medianos y grandes**, con procesos multi-fase.
2. **Por abajo, está casi vacío.** No hemos encontrado un equivalente directo a
   FIA Flash: gobernanza exprés (1-3 tareas) para scripts y mini-apps, con
   aprobación humana, checklists de seguridad/UX inyectados automáticamente y
   regla anti-scope-creep.
3. **En español, vacío total.** No existe ningún framework publicado del género
   en español — solo guías que explican herramientas inglesas.
4. **El contexto de mercado es ideal:** adopción récord de IA con confianza en
   mínimos históricos. Ese "gap de confianza" es exactamente lo que vende un
   harness de gobernanza.

## 2. El contexto: la paradoja que alimenta la categoría

Datos de la encuesta oficial de Stack Overflow 2025 (~49.000 desarrolladores):

| Dato | Valor | Lectura |
|---|---|---|
| Usan o planean usar IA en desarrollo | **84%** (76% en 2024) | El mercado existe y crece |
| Confían en la precisión de la IA | **33%** (46% desconfía; solo 3% confía "mucho") | La confianza cae 11 puntos en un año |
| Rechazan el "vibe coding" sin control para trabajo profesional | **72%** | Quieren estructura, no improvisación |
| Ven efecto positivo en productividad | 52% | Beneficio real pero discutido |

**La paradoja:** todos construyen con IA, cada vez se fían menos de lo que
sale. La respuesta del mercado fue el *spec-driven development* (Martin Fowler
le dedicó un análisis en 2025): escribir la especificación antes del código y
dejar que el agente la siga. Resultado: una ola de herramientas en 2025-2026.

**El hueco:** todas esas herramientas asumen un proyecto "de verdad" con
semanas de trabajo. Para el caso más común — *quiero un script o mini-app esta
tarde* — son demasiada ceremonia, y hoy la alternativa es construir sin ninguna
red. Ahí vive FIA Flash.

## 3. Competidores y comparables

| Herramienta | Qué es | Foco | Por qué no es Flash |
|---|---|---|---|
| **GitHub Spec Kit** | Toolkit open source de GitHub: specify → plan → tasks → implement, agnóstico del agente | Proyectos medianos, multi-fase | Sin gates de seguridad/UX ni triage de elegibilidad; inglés; demasiado proceso para 1-3 tareas |
| **Kiro (AWS)** | IDE agéntico con flujo requisitos → diseño → tareas | Equipos AWS | Lock-in de IDE y ecosistema; resuelve otra escala |
| **OpenSpec** | SDD ligero, favorecido para proyectos existentes (brownfield) | Proyectos en marcha | Sigue siendo multi-documento y en inglés; sin gobernanza embebida |
| **BMAD-METHOD** (~48k★) | Metodología completa multi-agente: roles PM/arquitecto/dev/QA con workflows YAML | Ciclo de vida entero | Peso y curva altísimos para un mini-script; su propia comunidad lo reconoce |
| **Claude Task Master** | CLI + MCP: parsea PRD → genera tareas con dependencias | Gestión de tareas para agentes | Genera y ordena tareas, pero **no es gobernanza**: sin checklists, sin aprobaciones, sin reglas de elegibilidad |
| **GSD / SuperClaude / Claude Flow** | Marcos de prompts/agentes para Claude Code | Usuarios de Claude Code | Atados a un agente concreto |
| **Agent OS (Builder Methods)** | Estándares y specs instalables por proyecto | Desarrollo agéntico serio | Más completo, más ceremonia; inglés |
| **Backlog.md** | Gestor de tareas en Markdown para humanos + agentes (CLI/kanban) | Tareas, milestones, docs | Es un *gestor de tareas*, no un sistema de gobernanza: sin triage, sin inyección de checklists, sin reglas |
| **CodeRabbit / Greptile** | Revisión de código con IA (SaaS) | QA posterior | Detecta problemas después, en la nube y de pago; Flash previene antes, offline y gratis |

**Nota honesta:** no compiten de frente — cubren otra escala. Spec Kit/BMAD son
el "Harness completo" del ecosistema; FIA Flash es el equivalente a lo que este
kit llama *Modo Flash*.

## 4. Diferenciadores de FIA Flash (lo que nadie más ofrece junto)

1. **La escala correcta.** El único del género pensado para micro-proyectos que
   se cierran en una sesión, con criterio explícito de elegibilidad (triage).
2. **Gobernanza embebida, no externa.** Los checklists de seguridad y UX/SEO no
   viven en un documento aparte que nadie lee: se inyectan solos dentro de cada
   tarea según su contenido (heurística de keywords).
3. **Gates humanos explícitos + regla anti-promoción.** La aprobación humana y
   la prohibición de "alargar" un proyecto Flash son reglas de primera clase.
   En la categoría, el scope creep se gestiona con disciplina personal; aquí,
   con un mecanismo.
4. **Cero dependencias, offline, privado.** Markdown + Python stdlib. Sin
   nube, sin telemetría, sin cuenta. Funciona con cualquier agente de IA —
   o sin ninguno.
5. **Español nativo.** Todo el sistema (reglas, plantillas, heurísticas con
   acentos cubiertos) está pensado en español. Es el único del mercado.
6. **Se aplica a sí mismo.** El kit tiene sus propios 11 tests — la filosofía
   de "validación real" no es prosa, es código.

## 5. Riesgos y amenazas (honestidad incluida)

- **Barrera de entrada baja.** El producto es Markdown + Python: Spec Kit u
  OpenSpec podrían añadir un "modo rápido" mañana. La defensa es la
  especialización (micro-escala), el idioma y la comunidad — no la tecnología.
- **Categoría joven y ruidosa.** Cada mes aparece un framework nuevo
  (Ralph Loop, Claude Flow, GSD…). Hace falta posicionamiento claro o se
  diluye en el ruido.
- **El gate humano no gustará a todos.** Parte del público de vibe coding
  busca justamente no pensar en proceso. El objetivo real es el 46% escéptico
  ( Stack Overflow 2025), no el entusiasta acrítico.
- **Ventana de oportunidad.** El hueco en español es real pero visible: si la
  categoría crece, llegarán traducciones. La ventaja de "nativo" (no
  traducido) es temporal y hay que usarla ahora.

## 6. Mensaje central para la web

> **Para el 84% que ya construye con IA y el 46% que no se fía de lo que sale:
> FIA Flash es el cinturón de seguridad del desarrollo exprés.**
> Toda la gobernanza de un proyecto serio — triage, aprobaciones, seguridad,
> UX, validación real — comprimida en 6 archivos y 3 comandos. Sin nube, sin
> dependencias, en español.

---

## Fuentes

- Stack Overflow Developer Survey 2025 (sección IA): https://survey.stackoverflow.co/2025/ai
- Stack Overflow Blog, resultados 2025: https://stackoverflow.blog/2025/12/29/developers-remain-willing-but-reluctant-to-use-ai-the-2025-developer-survey-results-are-here/
- The Register, "Coders using AI tools more, trusting less": https://www.theregister.com/software/2025/07/29/coders-using-ai-tools-more-trusting-less-stackoverflow/500701
- Martin Fowler, "Understanding Spec-Driven-Development": https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html
- Augment Code, "6 Best Spec-Driven Development Tools": https://www.augmentcode.com/tools/best-spec-driven-development-tools
- Ran the Builder, test comparativo BMAD vs Spec Kit vs OpenSpec: https://ranthebuilder.cloud/blog/i-tested-three-spec-driven-ai-tools-here-s-my-honest-take/
- CodeMySpec, "Best Spec-Driven Development Tools (2026)": https://codemyspec.com/blog/best-spec-driven-development-tools
- WebReactiva, guía SDD en español (confirma el vacío idiomático): https://www.webreactiva.com/blog/openspec
- GitHub Spec Kit: https://github.com/github/spec-kit
- BMAD-METHOD: https://github.com/bmad-code-org/BMAD-METHOD
