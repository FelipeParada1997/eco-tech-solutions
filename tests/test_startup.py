"""Comprobar el arranque de una copia del paquete sin archivos antiguos."""
import os
from pathlib import Path
import shutil
import subprocess
import sys


def test_package_starts_without_legacy_files(tmp_path):
    root = Path(__file__).resolve().parents[1]
    shutil.copytree(root / "ecotech", tmp_path / "ecotech", ignore=shutil.ignore_patterns("__pycache__"))
    environment = dict(os.environ, QT_QPA_PLATFORM="offscreen", PYTHONDONTWRITEBYTECODE="1")
    environment.pop("PYTHONPATH", None)
    script = '''
import runpy
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication
original_exec = QApplication.exec
def checked_exec(app):
    windows = app.topLevelWidgets()
    assert any(w.isVisible() and w.windowTitle() == "EcoTech Solutions - Iniciar sesión" for w in windows)
    print("ECOTECH_STARTUP_OK", flush=True)
    QTimer.singleShot(30, app.quit)
    return original_exec()
QApplication.exec = checked_exec
runpy.run_module("ecotech", run_name="__main__")
'''
    result = subprocess.run(
        [sys.executable, "-B", "-c", script], cwd=tmp_path,
        env=environment, text=True, capture_output=True, timeout=20,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "ECOTECH_STARTUP_OK" in result.stdout
