"""Integración opcional REAL. Crea y elimina solo tablas con un prefijo aleatorio.

ECOTECH_TEST_ORACLE=1 python -m pytest tests/test_oracle_live.py -q
Requiere un esquema de pruebas con CREATE TABLE/CREATE SEQUENCE y cuota.
Las seis tablas normales de la aplicación no se leen ni se modifican.
"""
import os
import re
import secrets
from datetime import date
import pytest
import oracledb
from ecotech.config import USUARIO, CONTRASENIA, DSN
from ecotech.database.schema import statements
from ecotech.repositories.oracle import OracleRepository
from ecotech.services.inicializacion import preparar_datos
from ecotech.services.autenticacion import AutenticacionService
from ecotech.services.gestion import GestionService
from ecotech.reports import ExportadorPDF, ExportadorExcel
from tests.test_domain import datos_empleado
from tests.support import PASSWORD

pytestmark = pytest.mark.skipif(os.getenv('ECOTECH_TEST_ORACLE') != '1',
                                reason='Integración Oracle optativa: ECOTECH_TEST_ORACLE=1')


class CursorAislado:
    def __init__(self, cursor, nombres):
        self.cursor = cursor
        self.nombres = nombres

    def execute(self, sql, parametros=None):
        sql = re.sub(r"'(?:''|[^'])*'|\b[A-Z][A-Z0-9_]*\b",
                     lambda m: m.group() if m.group().startswith("'") else self.nombres.get(m.group(), m.group()), sql)
        return self.cursor.execute(sql, parametros) if parametros is not None else self.cursor.execute(sql)

    def __getattr__(self, nombre):
        return getattr(self.cursor, nombre)


class ConexionAislada:
    def __init__(self, conexion, nombres):
        self.conexion = conexion
        self.nombres = nombres

    def cursor(self):
        return CursorAislado(self.conexion.cursor(), self.nombres)

    def __getattr__(self, nombre):
        return getattr(self.conexion, nombre)


@pytest.fixture
def oracle_aislado(tmp_path, monkeypatch):
    monkeypatch.setenv('ECOTECH_KEY_FILE', str(tmp_path / 'clave.key'))
    instrucciones = statements()
    nombres_objetos = []
    tablas = []
    for sql in instrucciones:
        crear = re.match(r'CREATE (TABLE|INDEX) (\w+)', sql)
        if crear:
            nombres_objetos.append(crear.group(2))
            if crear.group(1) == 'TABLE':
                tablas.append(crear.group(2))
        nombres_objetos.extend(re.findall(r'CONSTRAINT (\w+)', sql))
    prefijo = 'T' + secrets.token_hex(2).upper() + '_'
    nombres = {nombre: prefijo + nombre for nombre in nombres_objetos}
    # Cada nombre es interno, no proviene de formularios ni de credenciales.
    assert all(re.fullmatch(r'[A-Z][A-Z0-9_]{0,29}', nombre) for nombre in nombres.values())

    def conectar():
        return oracledb.connect(user=USUARIO, password=CONTRASENIA, dsn=DSN,
                                tcp_connect_timeout=5, retry_count=0)

    creadas = []
    conexion = conectar()
    try:
        cursor = CursorAislado(conexion.cursor(), nombres)
        for sql in instrucciones:
            cursor.execute(sql)
            crear = re.match(r'CREATE TABLE (\w+)', sql)
            if crear:
                creadas.append(nombres[crear.group(1)])
        cursor.close()
        yield OracleRepository(lambda: ConexionAislada(conectar(), nombres))
    finally:
        try:
            with conexion.cursor() as cursor:
                for tabla in reversed(creadas):
                    cursor.execute(f'DROP TABLE {tabla} CASCADE CONSTRAINTS PURGE')
        finally:
            conexion.close()


def test_oracle_full_workflow_and_integrity(oracle_aislado):
    repo = oracle_aislado
    assert preparar_datos(repo, 'admin', PASSWORD)
    assert not preparar_datos(repo, 'admin', PASSWORD)
    auth = AutenticacionService(repo)
    admin = GestionService(auth.autenticar('admin', PASSWORD), repo)
    assert admin.es_admin
    gerente = next(e for e in admin.listar_empleados() if e.tipo_empleado.value == 'GERENTE')
    depto = admin.guardar_departamento('Ventas de prueba', gerente.id_empleado)
    admin.guardar_departamento('Ventas actualizadas', gerente.id_empleado, depto)
    datos = datos_empleado(id_departamento=depto, fecha_inicio_contrato=date(2026, 1, 1))
    id_empleado = admin.guardar_empleado(datos)
    assert admin.listar_empleados('Ana')[0].id_empleado == id_empleado
    admin.crear_cuenta(id_empleado, 'ana', PASSWORD, 'EMPLEADO')
    empleado = GestionService(auth.autenticar('ana', PASSWORD), repo)
    assert len(empleado.listar_empleados()) == 1
    proyecto = admin.guardar_proyecto('Solar', 'Paneles', '01/01/2026')
    admin.guardar_proyecto('Solar actualizado', 'Paneles nuevos', '01/01/2026', proyecto)
    admin.asignar_proyecto(id_empleado, proyecto)
    id_horas = empleado.guardar_horas(proyecto, '02/01/2026', '2.50', 'Diseño')
    empleado.guardar_horas(proyecto, '02/01/2026', '3.25', 'Diseño corregido', id_horas)
    assert empleado.listar_horas()[0].horas_trabajadas == __import__('decimal').Decimal('3.25')
    with pytest.raises(ValueError, match='24'):
        empleado.guardar_horas(proyecto, '02/01/2026', 24, 'Exceso')
    with pytest.raises(PermissionError):
        empleado.guardar_proyecto('No', 'Sin permiso', '01/01/2026')
    admin.asignar_proyecto(id_empleado, proyecto, False)
    with pytest.raises(ValueError, match='activa'):
        empleado.guardar_horas(proyecto, '03/01/2026', 1, 'No asignado')
    admin.asignar_proyecto(id_empleado, proyecto)
    assert len(empleado.listar_asignaciones()) == 1
    with pytest.raises(ValueError, match='Reasigne'):
        admin.eliminar_departamento(depto)
    admin.reasignar_departamento(id_empleado, admin.listar_empleados()[0].id_departamento)
    admin.eliminar_departamento(depto)
    libre = admin.guardar_proyecto('Temporal', 'Sin referencias', '01/01/2026')
    admin.eliminar_proyecto(libre)
    informe = admin.generar_informe()
    assert informe.exportar(ExportadorPDF()).startswith(b'%PDF-')
    assert informe.exportar(ExportadorExcel()).startswith(b'PK')
    # Comprobar en Oracle que el texto personal no se persistió legible.
    with repo.transaccion() as c:
        c.execute('SELECT DATOS_CIFRADOS FROM EMPLEADO WHERE ID_EMPLEADO=:id', {'id': id_empleado})
        valor = c.fetchone()[0]
        guardado = valor.read() if hasattr(valor, 'read') else valor
        assert 'ana@example.test' not in guardado and 'Calle 123' not in guardado
        c.execute('SELECT COUNT(*) FROM TRABAJO_REALIZADO WHERE ID_EMPLEADO=:id', {'id': id_empleado})
        assert c.fetchone()[0] == 1
    # Un error de FK diferida al confirmar revierte toda la escritura.
    with repo.transaccion() as c:
        c.execute('SELECT COUNT(*) FROM DEPARTAMENTO')
        antes = c.fetchone()[0]
    with pytest.raises(ValueError, match='referencias pendientes'):
        with repo.transaccion(True) as c:
            c.execute('INSERT INTO DEPARTAMENTO (NOMBRE,ID_GERENTE) VALUES (:nombre,:gerente)',
                      {'nombre': 'No debe persistir', 'gerente': 99999999})
    with repo.transaccion() as c:
        c.execute('SELECT COUNT(*) FROM DEPARTAMENTO')
        assert c.fetchone()[0] == antes
    empleado.cerrar_sesion()
    with pytest.raises(PermissionError):
        empleado.listar_horas()
