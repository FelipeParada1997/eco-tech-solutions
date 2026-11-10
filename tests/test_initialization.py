from unittest.mock import Mock
import pytest
from ecotech.services.inicializacion import preparar_datos
from tests.support import MemoryRepository, PASSWORD


def test_missing_key_for_existing_data_is_not_recreated(monkeypatch, tmp_path, password_hash):
    ruta = tmp_path / 'clave.key'
    monkeypatch.setenv('ECOTECH_KEY_FILE', str(ruta))
    repo = MemoryRepository(password_hash)
    with pytest.raises(ValueError, match='Restaure'):
        preparar_datos(repo, 'admin', PASSWORD)
    assert not ruta.exists()


def test_invalid_initial_user_does_not_touch_database(tmp_path, monkeypatch):
    ruta = tmp_path / 'clave.key'
    monkeypatch.setenv('ECOTECH_KEY_FILE', str(ruta))
    repo = Mock()
    with pytest.raises(ValueError):
        preparar_datos(repo, '!', PASSWORD)
    repo.transaccion.assert_not_called()
    assert not ruta.exists()
