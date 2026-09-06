# FLASH_VISIBILIDAD_UX.md — Visibilidad + UI/UX en una sola pasada

Versión fusionada y reducida de `AEO_GEO_SEO.md` + `UI_UX_EXCLUSIVA.md` del
Harness completo. Aplica **solo si** la tarea crea o modifica una pantalla,
página pública o componente visual — si no, se marca "No aplica" y ya está.

**Visibilidad básica** *(solo si hay una página/pieza pública indexable)*
- [ ] `<title>` y meta description propios de la página, no genéricos.
- [ ] Un solo `h1`, jerarquía de encabezados coherente (`h2`/`h3` en orden).
- [ ] Imágenes con `alt` descriptivo.
- [ ] La primera frase del contenido ya responde a la pregunta principal — ayuda
      tanto a aparecer como respuesta destacada (AEO) como a que un asistente
      de IA cite el contenido (GEO), sin necesitar más aparato que esto.

**UI/UX básica** *(solo si hay pantalla o componente visual)*
- [ ] Hay una acción principal clara — no "todo es igual de importante".
- [ ] No es una copia genérica de un template: al menos una decisión visual
      propia (tipografía, color, layout) justificada en una frase.
- [ ] Estados cubiertos: vacío, cargando, error — no solo el caso feliz.
- [ ] Accesibilidad básica: contraste suficiente, navegable por teclado, responsive.

Si nada de esto aplica, se indica explícitamente:
`No aplica: esta tarea no toca superficie pública ni interfaz visual.`

> Si el proyecto necesita algo más que esto — estrategia de keywords, `llms.txt`,
> Design DNA propio con auditoría anti-clon, multi-idioma — **no es Flash**: ese
> nivel de detalle vive en `AEO_GEO_SEO.md` y `UI_UX_EXCLUSIVA.md` del Harness
> completo.
