#!/usr/bin/env python3
"""
FLASH_TASK.PY — Generador de tareas de Modo Flash
Lee FLASH_BRIEF.md, detecta la primera tarea pendiente de la sección "## 3. Tareas"
y genera FLASH_TASK-<n>.md a partir de FLASH_TASK_TEMPLATE.md, inyectando los
checklists de FLASH_SECURITY.md y FLASH_VISIBILIDAD_UX.md que apliquen, y rellena
el objetivo y el criterio de éxito desde el brief.

Nunca sobrescribe un FLASH_TASK-<n>.md ya existente, salvo que se pase --force
(puede contener trabajo rellenado a mano).

Reutiliza dos decisiones de diseño ya probadas en el generador del Harness
completo (`task_generator.py`), porque ahí evitaron bugs reales:
  1. Inyección por marcadores `<!-- INJECT:X --> ... <!-- /INJECT -->`, nunca
     por coincidencia literal de texto (frágil ante cualquier cambio de
     redacción/comillas).
  2. Palabras clave con límite de palabra (\\b), nunca por subcadena (evita
     falsos positivos del tipo "vista" dentro de "entrevista").
"""

import re
import sys
import argparse
from pathlib import Path

PY = Path(sys.executable).stem  # "python" en Windows; "python3" en la mayoría de Linux/macOS

FILES = {
    "brief": "FLASH_BRIEF.md",
    "security": "FLASH_SECURITY.md",
    "vis_ux": "FLASH_VISIBILIDAD_UX.md",
    "template": "FLASH_TASK_TEMPLATE.md",
}

INJECT_MARKERS = {"security": "FLASH_SECURITY", "vis_ux": "FLASH_VIS_UX"}
NOT_APPLICABLE = {
    "security": "No aplica: esta tarea no toca datos, secretos ni infraestructura.",
    "vis_ux": "No aplica: esta tarea no toca superficie pública ni interfaz visual.",
}

SEC_KEYWORDS = ["bbdd", "database", "datos", "auth", "login", "password", "contraseña",
                "seguridad", "permisos", "permiso", "rls", "secret", "secreto", "token",
                "api", "servidor", "infra", "deploy", "despliegue", "credencial", "webhook"]
VIS_KEYWORDS = ["landing", "pagina", "página", "web", "seo", "aeo", "geo", "contenido",
                "ui", "ux", "pantalla", "interfaz", "diseño", "componente", "formulario",
                "vista", "boton", "botón", "layout"]


def warn(msg):
    print(f"   [!] {msg}", file=sys.stderr)


def fail(msg):
    print(f"❌ {msg}", file=sys.stderr)
    sys.exit(1)


def load(path: Path, required=True):
    if not path.exists():
        if required:
            fail(f"No se encontró {path.name}. ¿Ejecutaste antes `{PY} bootstrap_flash.py`?")
        return ""
    return path.read_text(encoding="utf-8")


def _compile_kw(keywords):
    return re.compile(r"\b(?:" + "|".join(re.escape(k) for k in keywords) + r")\b", re.IGNORECASE)


_SEC_RE = _compile_kw(SEC_KEYWORDS)
_VIS_RE = _compile_kw(VIS_KEYWORDS)


def parse_tasks(brief_content: str):
    """Extrae las tareas de la sección '## 3. Tareas':
    - [ ] T1 — Título corto — objetivo en una frase
    Tolera '-'/'*' como viñeta, mayúsculas/minúsculas en 'T', y como separadores
    '—', '–' o un guion rodeado de espacios. Un guion pegado al texto
    (p. ej. "mini-API") NO separa: pertenece al título."""
    section = re.search(r"##\s*3\.\s*Tareas\s*\n(.*?)(?=\n##|\Z)", brief_content, re.DOTALL | re.IGNORECASE)
    if not section:
        return []
    tasks = []
    sep = r"(?:\s*[—–]\s*|\s-\s)"
    line_re = re.compile(
        rf"^[\-\*]\s*\[( |x|X)\]\s*[Tt](\d+){sep}(.+?){sep}(.+)$"
    )
    for line in section.group(1).split("\n"):
        m = line_re.match(line.strip())
        if not m:
            continue
        done_mark, num, title, objective = m.groups()
        tasks.append({
            "id": f"T{num}",
            "title": title.strip(),
            "objective": objective.strip(),
            "done": done_mark.lower() == "x",
        })
    return tasks


def check_triage(brief_content: str):
    """Devuelve (total, marcadas) de la sección '## 2. Triage de elegibilidad'."""
    section = re.search(r"##\s*2\.\s*Triage de elegibilidad.*?\n(.*?)(?=\n##|\Z)", brief_content, re.DOTALL | re.IGNORECASE)
    if not section:
        return (0, 0)
    boxes = re.findall(r"\[( |x|X)\]", section.group(1))
    done = sum(1 for b in boxes if b.lower() == "x")
    return (len(boxes), done)


def parse_brief_success(brief_content: str):
    """Criterio de éxito del §1 Brief de FLASH_BRIEF.md (admite varias líneas,
    hasta el siguiente campo '**...**' o encabezado). Devuelve "" si no está
    definido o si sigue siendo el placeholder '<pendiente ...>' del bootstrap."""
    m = re.search(
        r"\*\*Criterio de éxito:\*\*\s*(.*?)(?=\n\s*\*\*|\n#{1,6}\s|\Z)",
        brief_content, re.DOTALL,
    )
    if not m:
        return ""
    text = m.group(1).strip()
    if not text or text.startswith("<pendiente"):
        return ""
    return re.sub(r"\s*\n\s*", " ", text)  # cabe en una línea dentro de la tarea


def analyze(task: dict):
    text = f"{task['title']} {task['objective']}"
    return {"security": bool(_SEC_RE.search(text)), "vis_ux": bool(_VIS_RE.search(text))}


def inject(template: str, key: str, replacement: str):
    marker = INJECT_MARKERS[key]
    pattern = re.compile(rf"<!--\s*INJECT:{marker}\s*-->.*?<!--\s*/INJECT\s*-->", re.DOTALL)
    if not pattern.search(template):
        return template, False
    return pattern.sub(lambda _m: replacement.replace("\\", "\\\\"), template, count=1), True


def build_task_file(project_dir: Path, task: dict, reqs: dict, success: str = "") -> str:
    template = load(project_dir / FILES["template"])
    output = template.replace("<N>", task["id"]).replace("<TÍTULO>", task["title"].upper() or task["id"])
    output = output.replace("<qué debe conseguirse, en una frase>", task["objective"])
    if success:
        output = output.replace(
            "<resultado observable y comprobable en esta misma sesión>", success)

    for key, filekey in (("security", "security"), ("vis_ux", "vis_ux")):
        if reqs[key]:
            source_path = project_dir / FILES[filekey]
            if not source_path.exists():
                warn(f"{source_path.name} no existe: '{key}' queda como no verificable.")
                replacement = f"No verificable: falta el archivo `{source_path.name}`."
            else:
                # Copia el documento completo: son medias páginas, no hace falta
                # trocearlo por secciones como en el Harness completo.
                body = load(source_path)
                body = re.sub(r"^#.*\n", "", body, count=1).strip()  # sin repetir el título
                replacement = body
        else:
            replacement = NOT_APPLICABLE[key]

        output, found = inject(output, key, replacement)
        if not found:
            warn(f"No se encontró el marcador <!-- INJECT:{INJECT_MARKERS[key]} --> en "
                 f"{FILES['template']}. Esa sección quedó sin modificar — revísala a mano.")
    return output


def main():
    parser = argparse.ArgumentParser(description="Genera la siguiente FLASH-TASK-<n>.md pendiente.")
    parser.add_argument("--task", "-t", type=str, help="ID de tarea concreto (ej: T2). Si se omite, la primera pendiente.")
    parser.add_argument("--dir", "-d", type=str, default=".", help="Directorio raíz del proyecto.")
    parser.add_argument("--force", "-f", action="store_true",
                        help="Sobrescribe FLASH_TASK-<n>.md si ya existe (por defecto se niega, "
                             "para no perder contenido rellenado a mano).")
    args = parser.parse_args()
    project_dir = Path(args.dir)

    brief_content = load(project_dir / FILES["brief"])
    total, done = check_triage(brief_content)
    if total == 0:
        warn("No se encontró la sección '## 2. Triage de elegibilidad' en FLASH_BRIEF.md.")
    elif done < total:
        warn(f"Triage incompleto: {done}/{total} casillas marcadas en FLASH_BRIEF.md §2. "
             f"Confírmalo con el humano antes de seguir generando tareas.")

    tasks = parse_tasks(brief_content)
    if not tasks:
        fail(
            "No se encontró ninguna tarea con el formato "
            "'- [ ] T<n> — Título — objetivo' en la sección '## 3. Tareas' de "
            f"{FILES['brief']}."
        )

    if args.task:
        task = next((t for t in tasks if t["id"].lower() == args.task.lower()), None)
        if task is None:
            disponibles = ", ".join(t["id"] for t in tasks)
            fail(f"'{args.task}' no aparece en FLASH_BRIEF.md. Tareas encontradas: {disponibles}.")
    else:
        task = next((t for t in tasks if not t["done"]), None)
        if task is None:
            print("✅ No queda ninguna tarea pendiente en FLASH_BRIEF.md. Revisa el cierre (FLASH_START.md §7).")
            sys.exit(0)
        print(f"-> Detectada siguiente tarea pendiente: {task['id']} — {task['title']}")

    out_path = project_dir / f"FLASH_TASK-{task['id']}.md"
    if out_path.exists() and not args.force:
        fail(
            f"{out_path.name} ya existe: puede contener trabajo rellenado a mano y "
            f"no se sobrescribe. Para regenerarla a propósito, añade --force."
        )

    reqs = analyze(task)
    print(f"   - Seguridad: {'SÍ' if reqs['security'] else 'NO'}")
    print(f"   - Visibilidad/UI-UX: {'SÍ' if reqs['vis_ux'] else 'NO'}")
    print("   (heurística por palabras clave: revisa manualmente si no encaja con la tarea real)")

    success = parse_brief_success(brief_content)
    if not success:
        warn("FLASH_BRIEF.md §1 no tiene un Criterio de éxito definido: "
             "la tarea se genera con ese campo sin rellenar.")

    content = build_task_file(project_dir, task, reqs, success)
    out_path.write_text(content, encoding="utf-8")
    print(f"\n🎉 Generado: {out_path}")
    print("👉 Rellénala, marca la tarea [x] en FLASH_BRIEF.md y vuelve a lanzar el script.")


if __name__ == "__main__":
    main()
