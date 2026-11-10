"""Único punto de conexión a Oracle. No abre conexiones al importar."""
from contextlib import contextmanager
import oracledb
from ecotech.config import USUARIO, CONTRASENIA, DSN

def obtener_conexion():
    return oracledb.connect(user=USUARIO, password=CONTRASENIA, dsn=DSN)

@contextmanager
def sesion(escritura=False, connection_factory=None):
    """Cierra cursor/conexión y revierte cualquier escritura que falle."""
    conexion = (connection_factory or obtener_conexion)()
    cursor = None
    try:
        cursor = conexion.cursor()
        yield cursor
        if escritura:
            conexion.commit()
    except Exception:
        if escritura:
            conexion.rollback()
        raise
    finally:
        try:
            if cursor is not None:
                cursor.close()
        finally:
            conexion.close()
