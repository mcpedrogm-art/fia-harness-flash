#!/usr/bin/env python3
"""
TEST_FLASH_TOOLS.PY — Tests del propio kit Modo Flash

Ejecutan los dos scripts de verdad (subprocess) sobre proyectos temporales y
recorren el ciclo completo: bootstrap → tareas → cierre. Solo stdlib: el kit
no exige instalar nada.

Lanzar desde la raíz del kit:
    python -m unittest discover -s tests -v
o directamente:
    python tests/test_flash_tools.py
"""

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent
TEMPLATES = [
    "FLASH_START.md",
    "FLASH_SECURITY.md",
    "FLASH_VISIBILIDAD_UX.md",
    "FLASH_TASK_TEMPLATE.md",
]

BRIEF_COMPLETO = """# Contador CLI

## Objetivo
Un script que cuenta lineas y palabras de un archivo.

## Criterio de éxito
Al ejecutarlo sobre un archivo imprime lineas y palabras y pasa los tests.

## Incluye
- CLI con argparse
- Tests

## No incluye
- GUI
"""

BRIEF_SIN_EXITO = """# Contador CLI

## Objetivo
Un script que cuenta lineas y palabras de un archivo.
"""


def run(script, proj, *args):
    env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUTF8="1")
    return subprocess.run(
        [sys.executable, str(KIT / script), *args],
        cwd=proj, capture_output=True, text=True,
        encoding="utf-8", errors="replace", env=env,
    )


class KitFlashTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.proj = Path(tmp.name) / "proj"
        docs = self.proj / "docs_flash"
        docs.mkdir(parents=True)
        for t in TEMPLATES:
            shutil.copy2(KIT / t, docs / t)

    # -- helpers ----------------------------------------------------------

    def write_brief(self, text=BRIEF_COMPLETO):
        (self.proj / "BRIEF.md").write_text(text, encoding="utf-8")

    def bootstrap(self):
        return run("bootstrap_flash.py", self.proj)

    def preparar_brief(self, *tareas, brief=BRIEF_COMPLETO):
        """Bootstrap + triage marcado + tareas concretas en §3."""
        self.write_brief(brief)
        self.assertEqual(self.bootstrap().returncode, 0)
        p = self.proj / "FLASH_BRIEF.md"
        c = p.read_text(encoding="utf-8")
        cabeza, sep, cola = c.partition("## 3. Tareas")
        c = cabeza.replace("- [ ]", "- [x]") + sep + cola
        c = c.replace(
            "- [ ] T1 — <título corto> — <objetivo en una frase>",
            "\n".join(tareas),
        )
        p.write_text(c, encoding="utf-8")

    def leer(self, name):
        return (self.proj / name).read_text(encoding="utf-8")

    # -- bootstrap ----------------------------------------------------------

    def test_bootstrap_monta_y_extrae_el_brief(self):
        self.write_brief()
        r = self.bootstrap()
        self.assertEqual(r.returncode, 0, r.stderr)
        brief = self.leer("FLASH_BRIEF.md")
        self.assertIn("**Proyecto:** Contador CLI", brief)
        self.assertIn("cuenta lineas y palabras", brief)
        self.assertIn("pasa los tests", brief)  # criterio de éxito extraído
        for t in TEMPLATES:
            self.assertTrue((self.proj / t).exists(), t)
        self.assertTrue((self.proj / "src" / ".gitkeep").exists())
        self.assertTrue((self.proj / "tests" / ".gitkeep").exists())

    def test_bootstrap_es_idempotente(self):
        self.write_brief()
        self.bootstrap()
        antes = self.leer("FLASH_BRIEF.md")
        r = self.bootstrap()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(antes, self.leer("FLASH_BRIEF.md"))

    def test_bootstrap_sin_docs_flash_falla_limpio(self):
        huerfano = self.proj.parent / "huerfano"
        huerfano.mkdir()
        r = run("bootstrap_flash.py", huerfano)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("docs_flash", r.stderr)

    # -- generador de tareas --------------------------------------------------

    def test_tarea_neutra_marca_no_aplica(self):
        self.preparar_brief(
            "- [ ] T1 — CLI contador — script que cuenta lineas de un archivo, con tests")
        r = run("flash_task.py", self.proj)
        self.assertEqual(r.returncode, 0, r.stderr)
        t = self.leer("FLASH_TASK-T1.md")
        self.assertIn("No aplica: esta tarea no toca datos, secretos ni infraestructura.", t)
        self.assertIn("No aplica: esta tarea no toca superficie pública ni interfaz visual.", t)
        self.assertNotIn("bcrypt", t)
        # criterio de éxito propagado desde el brief
        self.assertIn("pasa los tests", t)
        self.assertNotIn("<resultado observable", t)

    def test_tarea_con_seguridad_inyecta_checklist(self):
        self.preparar_brief(
            "- [ ] T1 — Login — añadir login con password y base de datos de usuarios")
        r = run("flash_task.py", self.proj)
        self.assertEqual(r.returncode, 0, r.stderr)
        t = self.leer("FLASH_TASK-T1.md")
        self.assertIn("bcrypt/argon2", t)  # checklist de seguridad inyectado
        self.assertIn("No aplica: esta tarea no toca superficie pública", t)

    def test_tarea_con_ui_inyecta_checklist_vis_ux(self):
        self.preparar_brief(
            "- [ ] T1 — Landing — página web con SEO y formulario de contacto")
        r = run("flash_task.py", self.proj)
        self.assertEqual(r.returncode, 0, r.stderr)
        t = self.leer("FLASH_TASK-T1.md")
        self.assertIn("meta description", t)  # checklist de visibilidad inyectado
        self.assertIn("No aplica: esta tarea no toca datos, secretos", t)

    def test_criterio_sin_definir_avisa_y_deja_placeholder(self):
        self.preparar_brief(
            "- [ ] T1 — CLI contador — cuenta lineas de un archivo",
            brief=BRIEF_SIN_EXITO)
        r = run("flash_task.py", self.proj)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("Criterio de éxito", r.stderr)  # aviso explícito
        self.assertIn("<resultado observable", self.leer("FLASH_TASK-T1.md"))

    def test_no_pisa_una_tarea_rellenada_a_mano(self):
        self.preparar_brief(
            "- [ ] T1 — CLI contador — cuenta lineas de un archivo")
        self.assertEqual(run("flash_task.py", self.proj).returncode, 0)
        tarea = self.proj / "FLASH_TASK-T1.md"
        tarea.write_text(
            self.leer("FLASH_TASK-T1.md") + "\nDECISIONES A MANO — NO PERDER\n",
            encoding="utf-8")
        # segundo intento sin marcar [x]: se niega y el contenido sobrevive
        r = run("flash_task.py", self.proj)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("--force", r.stderr)
        self.assertIn("NO PERDER", tarea.read_text(encoding="utf-8"))
        # con --force sí regenera
        r = run("flash_task.py", self.proj, "--force")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn("NO PERDER", tarea.read_text(encoding="utf-8"))

    def test_flag_task_y_tareas_ya_hechas(self):
        self.preparar_brief(
            "- [x] T1 — Hecha — ya terminada ayer",
            "- [ ] T2 — Segunda — otra cosa pendiente")
        r = run("flash_task.py", self.proj)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue((self.proj / "FLASH_TASK-T2.md").exists())
        self.assertFalse((self.proj / "FLASH_TASK-T1.md").exists())
        r = run("flash_task.py", self.proj, "-t", "T1")  # explícita, aunque esté hecha
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue((self.proj / "FLASH_TASK-T1.md").exists())
        r = run("flash_task.py", self.proj, "-t", "T99")
        self.assertNotEqual(r.returncode, 0)

    def test_titulo_con_guion_no_se_parte(self):
        self.preparar_brief(
            "- [ ] T1 — Setup mini-API — servidor de conteo con cache")
        r = run("flash_task.py", self.proj)
        self.assertEqual(r.returncode, 0, r.stderr)
        t = self.leer("FLASH_TASK-T1.md")
        self.assertIn("# FLASH-TASK-T1 — SETUP MINI-API", t)
        self.assertIn("servidor de conteo con cache", t)

    def test_proyecto_cerrado_cuando_todo_hecho(self):
        self.preparar_brief(
            "- [x] T1 — Unica — ya terminada")
        r = run("flash_task.py", self.proj)
        self.assertEqual(r.returncode, 0)
        self.assertIn("No queda ninguna tarea pendiente", r.stdout)
        self.assertFalse((self.proj / "FLASH_TASK-T1.md").exists())


if __name__ == "__main__":
    unittest.main()
