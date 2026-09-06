#!/usr/bin/env python3
"""
BOOTSTRAP_FLASH.PY — Inicializador de Modo Flash
Arranca un proyecto Flash (independiente, no promocionable al Harness completo):
1. Copia las 4 plantillas de `docs_flash/` a la raíz.
2. Crea `src/` y `tests/`.
3. Busca un brief opcional (BRIEF.md/IDEA.md/brief.md) y genera FLASH_BRIEF.md
   con el brief, el triage de elegibilidad (sin marcar) y una sección de tareas
   vacía lista para rellenar.

A diferencia de `bootstrap.py` del Harness completo, este script NO genera
CONTEXT.md/SPEC.md/PROGRESS.md/DECISIONS.md por separado — todo vive en un
único archivo (`FLASH_BRIEF.md`), a propósito, porque Modo Flash es para
proyectos que se cierran en 1-3 tareas.
"""

import re
import sys
import shutil
from pathlib import Path

REQUIRED_TEMPLATES = [
    "FLASH_START.md",
    "FLASH_SECURITY.md",
    "FLASH_VISIBILIDAD_UX.md",
    "FLASH_TASK_TEMPLATE.md",
]

BRIEF_CANDIDATES = ["BRIEF.md", "brief.md", "IDEA.md", "idea.md", "PRD.md", "MVP.md"]

PY = Path(sys.executable).stem  # "python" en Windows; "python3" en la mayoría de Linux/macOS


def warn(msg):
    print(f"   [!] {msg}", file=sys.stderr)


def fail(msg):
    print(f"❌ {msg}", file=sys.stderr)
    sys.exit(1)


def find_brief_file(root: Path):
    for name in BRIEF_CANDIDATES:
        p = root / name
        if p.exists():
            return p
    return None


def copy_templates(root: Path, docs_dir: Path):
    print("-> Copiando plantillas de Modo Flash...")
    if not docs_dir.exists():
        fail(
            f"No existe la carpeta '{docs_dir.name}/' en {root.resolve()}. "
            f"Modo Flash necesita sus 4 plantillas ahí antes de arrancar."
        )
    missing = []
    for name in REQUIRED_TEMPLATES:
        src = docs_dir / name
        dst = root / name
        if dst.exists():
            print(f"   [.] {name} ya está en la raíz (no se sobrescribe).")
            continue
        if not src.exists():
            missing.append(name)
            continue
        shutil.copy2(src, dst)
        print(f"   [+] Copiado: {name}")
    if missing:
        fail(f"Faltan plantillas obligatorias en '{docs_dir.name}/': {', '.join(missing)}")


def create_folders(root: Path):
    print("-> Creando carpetas...")
    for folder in ("src", "tests"):
        p = root / folder
        if not p.exists():
            p.mkdir(parents=True, exist_ok=True)
            (p / ".gitkeep").touch()  # para que git no ignore la carpeta vacía
            print(f"   [+] Creada: /{folder}")


def extract_brief_fields(brief_path: Path):
    """Extracción deliberadamente simple: un brief Flash debería caber en
    unas pocas líneas, así que no se intenta adivinar tanto como en
    bootstrap.py — si no encuentra una sección, se deja en blanco para que
    el humano/agente la rellene a mano, sin inventar texto genérico."""
    fields = {"title": "", "objective": "", "success": "", "include": [], "exclude": [], "found_any": False}
    if not brief_path or not brief_path.exists():
        return fields

    content = brief_path.read_text(encoding="utf-8")

    title_match = re.search(r"^#\s+(.*)", content, re.MULTILINE)
    if title_match:
        fields["title"] = title_match.group(1).strip()

    obj = re.search(r"(?:##|###)\s*(?:Objetivo|Problema|Idea)\s*\n(.*?)(?=\n##|\Z)", content, re.DOTALL | re.IGNORECASE)
    if obj:
        fields["objective"] = obj.group(1).strip()
        fields["found_any"] = True

    succ = re.search(r"(?:##|###)\s*(?:Criterio de éxito|Éxito|Success)\s*\n(.*?)(?=\n##|\Z)", content, re.DOTALL | re.IGNORECASE)
    if succ:
        fields["success"] = succ.group(1).strip()
        fields["found_any"] = True

    inc = re.search(r"(?:##|###)\s*(?:Incluye|Alcance|Scope)\s*\n(.*?)(?=\n##|\Z)", content, re.DOTALL | re.IGNORECASE)
    if inc:
        fields["include"] = [l.strip("* -") for l in inc.group(1).strip().split("\n") if l.strip().startswith(("*", "-"))]

    exc = re.search(r"(?:##|###)\s*(?:No incluye|Fuera de alcance|Excluido)\s*\n(.*?)(?=\n##|\Z)", content, re.DOTALL | re.IGNORECASE)
    if exc:
        fields["exclude"] = [l.strip("* -") for l in exc.group(1).strip().split("\n") if l.strip().startswith(("*", "-"))]

    # si no hay estructura reconocible, usa el documento entero como objetivo en bruto
    if not fields["found_any"]:
        raw = content.strip()
        if raw:
            fields["objective"] = raw
            warn(
                f"{brief_path.name} no tiene secciones reconocibles (##Objetivo/##Criterio de éxito/...). "
                f"Se copió tal cual como objetivo — revísalo y separa manualmente en FLASH_BRIEF.md."
            )
    return fields


def generate_flash_brief(root: Path, brief_path: Path, fields: dict):
    out_path = root / "FLASH_BRIEF.md"
    if out_path.exists():
        print("   [.] FLASH_BRIEF.md ya existe. No se sobrescribe.")
        return

    title = fields.get("title") or (brief_path.stem.replace("_", " ").title() if brief_path else "Proyecto Flash sin título")
    include_md = "\n".join(f"- {i}" for i in fields["include"]) if fields["include"] else "- <pendiente de completar>"
    exclude_md = "\n".join(f"- {e}" for e in fields["exclude"]) if fields["exclude"] else "- <pendiente de completar>"
    objective = fields["objective"] or "<pendiente — describe en una frase qué hay que construir>"
    success = fields["success"] or "<pendiente — cómo se comprueba que funcionó, en esta misma sesión>"

    content = f"""# FLASH_BRIEF.md — Brief y estado del proyecto Flash

**Proyecto:** {title}
**Modo:** Flash — no promocionable (ver `FLASH_START.md`, cabecera)

## 1. Brief

**Objetivo:** {objective}

**Criterio de éxito:** {success}

**Incluye:**
{include_md}

**No incluye (fuera de alcance):**
{exclude_md}

## 2. Triage de elegibilidad (`FLASH_START.md` §1)

- [ ] Una sola funcionalidad, script o mini-app — cabe en una frase.
- [ ] Nada de pagos, datos de salud, PII sensible ni autenticación compleja.
- [ ] No toca infraestructura delicada.
- [ ] Cero o una integración externa, de solo lectura si la hay.
- [ ] Criterio de éxito comprobable en esta misma sesión.
- [ ] Se cierra en 1 a 3 tareas como mucho.

> ⚠️ Si al revisar con el humano queda alguna casilla sin marcar: **no uses
> Modo Flash** — usa el Harness completo desde cero (`INICIO_PROYECTO.md`).

## 3. Tareas

<!-- Una línea por tarea, formato: - [ ] T<n> — Título corto — objetivo en una frase
     flash_task.py detecta automáticamente la primera pendiente. -->

- [ ] T1 — <título corto> — <objetivo en una frase>

## 4. Aprobaciones y decisiones

<!-- Registro breve: qué se aprobó, cuándo, y por quién. -->

## 5. Estado

Última actualización: recién generado por `bootstrap_flash.py`.
"""
    out_path.write_text(content, encoding="utf-8")
    print("   [+] FLASH_BRIEF.md generado.")


def main():
    root = Path(".")
    docs_dir = root / "docs_flash"

    print("=" * 60)
    print(" MODO FLASH — bootstrap")
    print("=" * 60)

    copy_templates(root, docs_dir)
    create_folders(root)

    brief_path = find_brief_file(root)
    if brief_path:
        print(f"\n[✓] Brief detectado: {brief_path.name}")
        fields = extract_brief_fields(brief_path)
    else:
        print("\n[i] No se encontró BRIEF.md/IDEA.md/brief.md en la raíz.")
        print("    FLASH_BRIEF.md se genera con placeholders — complétalo a mano.")
        fields = {"objective": "", "success": "", "include": [], "exclude": []}

    generate_flash_brief(root, brief_path, fields)

    print("\n🎉 Bootstrap de Modo Flash completado.")
    print("👉 Próximo paso: completa el Triage (§2) y la sección de Tareas (§3) de")
    print("   FLASH_BRIEF.md a mano, consigue la aprobación humana, y ejecuta:")
    print(f"   {PY} flash_task.py")


if __name__ == "__main__":
    main()
