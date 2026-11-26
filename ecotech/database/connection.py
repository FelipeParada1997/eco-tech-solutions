"""Único punto de conexión a Oracle. No abre conexiones al importar."""
from contextlib import contextmanager
import oracledb
import sqlite3
#from ecotech.config import USUARIO, CONTRASENIA, DSN
from ecotech.config import RUTA_SQLITE

def obtener_conexion():
    #return oracledb.connect(user=USUARIO, password=CONTRASENIA, dsn=DSN)

    # .parent obtiene la carpeta que lo contendrá.
    # parents=True crea también las carpetas superiores que falten.
    # exist_ok=True permite continuar si la carpeta ya existe.
    RUTA_SQLITE.parent.mkdir(parents=True, exist_ok=True)

    # Abre una conexión con la base SQLite. Si el archivo no existe, SQLite lo crea
    conexion = sqlite3.connect(RUTA_SQLITE, isolation_level=None)  # isolation_level=None evita que Python abra transacciones automáticamente.

    try:
        # Activa la comprobación de las claves foráneas en ESTA conexión.
        cursor = conexion.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")
        cursor.close() 

    except Exception:
        conexion.close()
        raise   

    return conexion

@contextmanager
def sesion(escritura=False, connection_factory=None):

    conexion = (connection_factory or obtener_conexion)()
    cursor = None
    try:
        cursor = conexion.cursor()

        if escritura:
            cursor.execute("BEGIN IMMEDIATE")  # Inicia una transacción de escritura en SQLite
        else:
            cursor.execute("BEGIN") 

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

    
    # """Cierra cursor/conexión y revierte cualquier escritura que falle."""
    # conexion = (connection_factory or obtener_conexion)()
    # cursor = None
    # try:
    #     cursor = conexion.cursor()
    #     yield cursor
    #     if escritura:
    #         conexion.commit()

    # except Exception:
    #     if escritura:
    #         conexion.rollback()
    #     raise
    # finally:
    #     try:
    #         if cursor is not None:
    #             cursor.close()
    #     finally:
    #         conexion.close()
