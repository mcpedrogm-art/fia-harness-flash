# FLASH-TASK-<N> — <TÍTULO>

**Reglas no negociables:** aprobación humana antes de instalar/conectar nada ·
sin secretos en el código ni en los logs · sin commit/push/deploy sin
autorización · validación real, nunca inventada. (`FLASH_START.md` §4)

## 1. Objetivo y alcance

**Objetivo:** <qué debe conseguirse, en una frase>
**Criterio de éxito:** <resultado observable y comprobable en esta misma sesión>

**Incluye:**
- <elemento 1>

**No incluye (fuera de alcance):**
- <elemento 1>

## 2. Seguridad

<!-- INJECT:FLASH_SECURITY -->
Verifica contra `FLASH_SECURITY.md` los puntos que apliquen a esta tarea.
Si no aplica: "No aplica: esta tarea no toca datos, secretos ni infraestructura".
<!-- /INJECT -->

## 3. Visibilidad / UI-UX

<!-- INJECT:FLASH_VIS_UX -->
Verifica contra `FLASH_VISIBILIDAD_UX.md` los puntos que apliquen a esta tarea.
Si no aplica: "No aplica: esta tarea no toca superficie pública ni interfaz visual".
<!-- /INJECT -->

## 4. Implementación

**Qué se hizo:** <descripción concreta>
**Decisiones y por qué:** <lista breve>
**Casos límite cubiertos:** <entrada inválida / doble ejecución / error / estado vacío>

## 5. Validación

- Tests: <comando y resultado real>
- Build/typecheck: <comando y resultado real>
- Revisión manual: <qué se comprobó>
- Errores preexistentes no relacionados: <lista o "Ninguno">

No se inventan resultados que no se hayan ejecutado de verdad.

## 6. Cierre

- **Resultado:** `TAREA COMPLETADA` / `BLOQUEADA` / `ESTE PROYECTO NECESITA EL HARNESS COMPLETO`
- Archivos tocados: <lista>
- Aprobaciones registradas: <referencia>
- Git: `Commit: SI/NO` · `Push: SI/NO` · `Deploy: SI/NO`
- Próximo paso: <siguiente tarea / cierre del proyecto>

> Si el resultado es `ESTE PROYECTO NECESITA EL HARNESS COMPLETO`: no se
> "promociona" esta tarea. Se cierra el proyecto Flash aquí (ver `FLASH_START.md`
> §7) y se arranca un proyecto nuevo con `INICIO_PROYECTO.md`.
