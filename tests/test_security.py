import pytest
from cryptography.fernet import Fernet
from ecotech.security.cifrado import Cifrado, crear_clave


def test_personal_data_is_encrypted_and_wrong_key_rejected(tmp_path):
    ruta = tmp_path / 'clave.key'
    crear_clave(ruta)
    cifrado = Cifrado(ruta.read_bytes())
    datos = {'nombre': 'Ana', 'salario': '1000', 'correo': 'ana@example.test'}
    guardado = cifrado.cifrar(datos)
    assert 'Ana' not in guardado and 'ana@example.test' not in guardado
    assert cifrado.descifrar(guardado) == datos
    with pytest.raises(ValueError, match='descifrar'):
        Cifrado(Fernet.generate_key()).descifrar(guardado)
    with pytest.raises(FileExistsError):
        crear_clave(ruta)
    assert cifrado.descifrar(guardado) == datos


def test_no_silent_key_creation(monkeypatch, tmp_path):
    monkeypatch.setenv('ECOTECH_KEY_FILE', str(tmp_path / 'inexistente.key'))
    with pytest.raises(ValueError, match='clave'):
        Cifrado()
    assert not (tmp_path / 'inexistente.key').exists()
