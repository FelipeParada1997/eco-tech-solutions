import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
from PyQt6.QtWidgets import QApplication, QMessageBox


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance() or QApplication([])
    return app


@pytest.fixture
def messages(monkeypatch):
    calls = []
    for name in ("information", "warning", "critical"):
        monkeypatch.setattr(
            QMessageBox, name,
            lambda *args, kind=name: calls.append((kind, args[1], args[2])),
        )
    monkeypatch.setattr(
        QMessageBox, "question", lambda *args: QMessageBox.StandardButton.Yes
    )
    return calls


@pytest.fixture(scope='session')
def password_hash():
    from ecotech.security.passwords import crear_hash
    from tests.support import PASSWORD
    return crear_hash(PASSWORD)


@pytest.fixture
def entorno(password_hash):
    from tests.support import MemoryRepository, PASSWORD
    from ecotech.services.autenticacion import AutenticacionService
    from ecotech.services.gestion import GestionService
    repo = MemoryRepository(password_hash)
    auth = AutenticacionService(repo)
    admin = GestionService(auth.autenticar('admin', PASSWORD), repo)
    empleado = GestionService(auth.autenticar('pedro', PASSWORD), repo)
    return repo, admin, empleado
