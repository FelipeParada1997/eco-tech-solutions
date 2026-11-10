"""El instalador solo prepara tablas y cuenta inicial en el Oracle configurado."""
from unittest.mock import Mock
import oracledb
import pytest
import ecotech.scripts.instalar as cli

PASSWORD = 'ClaveProfesor123!'


@pytest.fixture
def instalador(monkeypatch):
    monkeypatch.setattr(cli, 'USUARIO', 'ECOTECH')
    monkeypatch.setattr(cli, 'CONTRASENIA', 'CredencialOraclePrivada')
    monkeypatch.setattr(cli, 'DSN', 'localhost:1521/XEPDB1')
    tablas = Mock(return_value=(['EMPLEADO'], []))
    datos = Mock(return_value=True)
    repository = Mock()
    monkeypatch.setattr(cli, 'instalar_tablas', tablas)
    monkeypatch.setattr(cli, 'preparar_datos', datos)
    monkeypatch.setattr(cli, 'OracleRepository', Mock(return_value=repository))
    monkeypatch.setattr('builtins.input', lambda prompt: 'profesor')
    claves = iter([PASSWORD, PASSWORD])
    monkeypatch.setattr(cli, 'getpass', lambda prompt: next(claves))
    return tablas, datos, repository


def test_install_uses_existing_configuration_without_rewriting_env(instalador, monkeypatch, tmp_path, capsys):
    tablas, datos, repository = instalador
    monkeypatch.chdir(tmp_path)
    ruta = tmp_path / '.env'
    contenido = 'ORACLE_USER=mantener\nORACLE_PASSWORD=privada\n'
    ruta.write_text(contenido)
    assert cli.main([]) == 0
    tablas.assert_called_once_with()
    datos.assert_called_once_with(repository, 'profesor', PASSWORD)
    assert ruta.read_text() == contenido
    salida = capsys.readouterr().out
    assert PASSWORD not in salida and 'CredencialOraclePrivada' not in salida
    assert 'Administrador creado' in salida


@pytest.mark.parametrize('variable', ['USUARIO', 'CONTRASENIA', 'DSN'])
def test_incomplete_configuration_stops_before_database(instalador, monkeypatch, variable):
    tablas, datos, _ = instalador
    monkeypatch.setattr(cli, variable, '')
    assert cli.main([]) == 1
    tablas.assert_not_called()
    datos.assert_not_called()


@pytest.mark.parametrize('usuario', ['SYS', 'system'])
def test_privileged_oracle_account_is_not_used(instalador, monkeypatch, usuario):
    tablas, _, _ = instalador
    monkeypatch.setattr(cli, 'USUARIO', usuario)
    assert cli.main([]) == 1
    tablas.assert_not_called()


def test_invalid_app_user_stops_before_ddl(instalador, monkeypatch):
    tablas, _, _ = instalador
    monkeypatch.setattr('builtins.input', lambda prompt: '!')
    assert cli.main([]) == 1
    tablas.assert_not_called()


@pytest.mark.parametrize('password', ['corta', 'abcdefghijklmnop', '123456789012'])
def test_invalid_password_stops_before_ddl(instalador, monkeypatch, password):
    tablas, _, _ = instalador
    monkeypatch.setattr(cli, 'getpass', lambda prompt: password)
    assert cli.main([]) == 1
    tablas.assert_not_called()


def test_password_mismatch_stops_before_ddl(instalador, monkeypatch):
    tablas, _, _ = instalador
    claves = iter([PASSWORD, 'OtraContraseña123!'])
    monkeypatch.setattr(cli, 'getpass', lambda prompt: next(claves))
    assert cli.main([]) == 1
    tablas.assert_not_called()


def test_cancel_stops_before_ddl(instalador, monkeypatch):
    tablas, _, _ = instalador
    monkeypatch.setattr('builtins.input', Mock(side_effect=EOFError))
    assert cli.main([]) == 1
    tablas.assert_not_called()


def test_existing_admin_is_verified_instead_of_replaced(instalador, capsys):
    _, datos, _ = instalador
    datos.return_value = False
    assert cli.main([]) == 0
    assert 'existente verificado' in capsys.readouterr().out


def test_incompatible_schema_does_not_load_data(instalador, capsys):
    tablas, datos, _ = instalador
    tablas.side_effect = ValueError('La tabla EMPLEADO no es compatible.')
    assert cli.main([]) == 1
    datos.assert_not_called()
    assert 'no es compatible' in capsys.readouterr().out


def test_oracle_error_does_not_print_driver_message(instalador, capsys):
    tablas, datos, _ = instalador
    error = oracledb.DatabaseError('SQL con contraseña secreta')
    tablas.side_effect = error
    assert cli.main([]) == 1
    datos.assert_not_called()
    salida = capsys.readouterr().out
    assert 'secreta' not in salida
    assert 'Revise .env' in salida
