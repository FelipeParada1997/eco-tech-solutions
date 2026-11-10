import importlib
import pkgutil
from unittest.mock import Mock
import pytest
from ecotech.entities import CuentaUsuario
from ecotech.security.passwords import crear_hash, generar_hash, verificar_password
from ecotech.services.autenticacion import AutenticacionService
from tests.support import PASSWORD


def test_password_current_and_legacy_formats(password_hash):
    assert verificar_password(PASSWORD, password_hash)
    assert not verificar_password('equivocada', password_hash)
    assert verificar_password(PASSWORD, 'sal:' + generar_hash(PASSWORD, 'sal'))
    assert crear_hash(PASSWORD) != password_hash


@pytest.mark.parametrize('password', ['corta', 'abcdefghijklmnop', '123456789012', 'x' * 129])
def test_new_password_policy(password):
    with pytest.raises(ValueError):
        crear_hash(password)


@pytest.mark.parametrize('guardado', [None, '', 'incorrecto', 'pbkdf2_sha256$999999999$s$h', 'sal:invalido'])
def test_malformed_hash_rejected(guardado):
    assert not verificar_password(PASSWORD, guardado)


def test_account_requires_authentication_and_revokes_on_logout(password_hash):
    cuenta = CuentaUsuario('pedro', password_hash, 2)
    assert not cuenta.tiene_permiso('horas')
    assert cuenta.autenticar(PASSWORD)
    assert cuenta.tiene_permiso('horas')
    assert not cuenta.tiene_permiso('cuentas')
    cuenta.cerrar_sesion()
    assert not cuenta.tiene_permiso('horas')


def test_inactive_and_invalid_roles(password_hash):
    cuenta = CuentaUsuario('pedro', password_hash, 2, activo=False)
    assert not cuenta.autenticar(PASSWORD)
    with pytest.raises(ValueError):
        CuentaUsuario('pedro', password_hash, 2, rol='SUPERADMIN')


def test_authentication_bad_password_unknown_and_casefold(entorno):
    repo, _, _ = entorno
    auth = AutenticacionService(repo)
    assert auth.autenticar('  PEDRO ', PASSWORD).id_titular == 2
    assert auth.autenticar('pedro', 'incorrecta') is None
    assert auth.autenticar('nadie', PASSWORD) is None


def test_all_modules_import_without_connecting(monkeypatch):
    import oracledb
    import ecotech
    connect = Mock(side_effect=AssertionError('No abrir Oracle al importar'))
    monkeypatch.setattr(oracledb, 'connect', connect)
    for modulo in pkgutil.walk_packages(ecotech.__path__, ecotech.__name__ + '.'):
        importlib.import_module(modulo.name)
    connect.assert_not_called()
