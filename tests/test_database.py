from unittest.mock import Mock

import pytest

from ecotech.database.connection import sesion
from ecotech.repositories.oracle import OracleRepository
from ecotech.entities import Empleado


@pytest.mark.parametrize("write", [False, True])
def test_session_success_closes_resources_and_only_commits_writes(write):
    conn = Mock()
    with sesion(escritura=write, connection_factory=lambda: conn) as cursor:
        assert cursor is conn.cursor.return_value
    assert conn.commit.call_count == int(write)
    conn.rollback.assert_not_called()
    cursor.close.assert_called_once()
    conn.close.assert_called_once()


@pytest.mark.parametrize("write", [False, True])
def test_session_failure_closes_resources_and_rolls_back_writes(write):
    conn = Mock()
    with pytest.raises(ValueError, match="fallo"):
        with sesion(escritura=write, connection_factory=lambda: conn):
            raise ValueError("fallo")
    conn.commit.assert_not_called()
    assert conn.rollback.call_count == int(write)
    conn.cursor.return_value.close.assert_called_once()
    conn.close.assert_called_once()


def test_connection_closes_when_cursor_creation_or_close_fails():
    for stage in ("create", "close"):
        conn = Mock()
        if stage == "create":
            conn.cursor.side_effect = ValueError("cursor")
        else:
            conn.cursor.return_value.close.side_effect = ValueError("cursor")
        with pytest.raises(ValueError, match="cursor"):
            with sesion(connection_factory=lambda: conn):
                pass
        conn.close.assert_called_once()


def test_write_commit_error_rolls_back():
    conn = Mock()
    conn.commit.side_effect = ValueError("commit")
    with pytest.raises(ValueError, match="commit"):
        with sesion(escritura=True, connection_factory=lambda: conn):
            pass
    conn.rollback.assert_called_once()
    conn.close.assert_called_once()



def test_repository_binds_personal_data_and_returned_identity():
    from cryptography.fernet import Fernet
    from ecotech.security.cifrado import Cifrado
    from tests.test_domain import datos_empleado
    conexion = Mock()
    cursor = conexion.cursor.return_value
    cursor.var.return_value.getvalue.return_value = [42]
    cifrado = Cifrado(Fernet.generate_key())
    repo = OracleRepository(lambda: conexion, cifrado)
    entrada = "Ana ' OR 1=1 --"
    empleado = Empleado(**datos_empleado(nombre=entrada))
    with repo.transaccion(True) as c:
        id_empleado = repo.guardar_empleado(c, empleado)
    assert id_empleado == 42
    sql, parametros = cursor.execute.call_args.args
    assert 'RETURNING ID_EMPLEADO INTO :nuevo_id' in sql
    assert entrada not in sql and entrada not in parametros['datos']
    assert cifrado.descifrar(parametros['datos'])['nombre'] == entrada
    conexion.commit.assert_called_once()


@pytest.mark.parametrize('codigo', [2292, 2091])
def test_oracle_failure_becomes_safe_message_and_rolls_back(codigo):
    import oracledb
    conexion = Mock()
    detalle = Mock(code=codigo, full_code=f'ORA-{codigo:05d}')
    conexion.cursor.return_value.execute.side_effect = oracledb.DatabaseError(detalle)
    repo = OracleRepository(lambda: conexion)
    with pytest.raises(ValueError, match='referencias pendientes'):
        with repo.transaccion(True) as c:
            repo.eliminar_departamento(c, 1)
    conexion.rollback.assert_called_once()
    conexion.commit.assert_not_called()
    conexion.close.assert_called_once()
