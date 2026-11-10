"""Instalación explícita y repetible del esquema usado por los repositorios."""
from pathlib import Path
import re

from ecotech.database.connection import obtener_conexion


SCHEMA_FILE = Path(__file__).with_name("schema.sql")
TABLE_COLUMNS = {
    "DEPARTAMENTO": {"ID_DEPARTAMENTO", "NOMBRE", "ID_GERENTE"},
    "EMPLEADO": {"ID_EMPLEADO", "DATOS_CIFRADOS", "TIPO_EMPLEADO", "ID_DEPARTAMENTO"},
    "PROYECTO": {"ID_PROYECTO", "NOMBRE", "DESCRIPCION", "FECHA_INICIO"},
    "ASIGNACION": {"ID_ASIGNACION", "ID_EMPLEADO", "ID_PROYECTO", "ACTIVA"},
    "TRABAJO_REALIZADO": {"ID_TRABAJO", "ID_EMPLEADO", "ID_PROYECTO", "FECHA", "HORAS", "DESCRIPCION"},
    "USUARIO": {"ID_USUARIO", "NOMBRE_USUARIO", "PASSWORD_HASH", "ID_EMPLEADO", "ACTIVO", "ROL"},
}


def statements():
    text = re.sub(r"--[^\n]*", "", SCHEMA_FILE.read_text(encoding="utf-8"))
    return [part.strip() for part in text.split(";") if part.strip()]


def instalar(connection_factory=None):
    """Crea objetos faltantes; nunca elimina tablas ni altera columnas existentes.

    Oracle confirma DDL automáticamente: si falla un paso, volver a ejecutar
    continúa con los objetos faltantes. La carga inicial usa su propia transacción.
    """
    connection = (connection_factory or obtener_conexion)()
    cursor = None
    created = []
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT object_name, object_type FROM user_objects")
        objects = set(cursor.fetchall())
        cursor.execute("SELECT table_name, column_name FROM user_tab_columns")
        columns = set(cursor.fetchall())
        # Comprobar todo antes del primer DDL para no reparar un esquema ajeno.
        for table, required in TABLE_COLUMNS.items():
            if (table, "TABLE") in objects:
                missing = sorted(c for c in required if (table, c) not in columns)
                if missing:
                    raise ValueError(
                        f"La tabla {table} no es compatible: faltan {', '.join(missing)}. "
                        "No se modificó el esquema. Use un esquema vacío o una migración revisada."
                    )
        cursor.execute("SELECT constraint_name FROM user_constraints")
        constraints = {row[0] for row in cursor.fetchall()}
        for statement in statements():
            create = re.match(r"CREATE (TABLE|INDEX) (\w+)", statement)
            if create:
                kind, name = create.groups()
                if (name, kind) in objects:
                    continue
            else:
                alter = re.match(r"ALTER TABLE \w+ ADD CONSTRAINT (\w+)", statement)
                if not alter:
                    raise ValueError("Instrucción de instalación no reconocida.")
                kind, name = "CONSTRAINT", alter.group(1)
                if name in constraints:
                    continue
            try:
                cursor.execute(statement)
            except Exception as error:
                detail = error.args[0] if error.args else None
                if getattr(detail, "code", None) == 1031:
                    raise ValueError(
                        f"Permisos insuficientes al crear {kind} {name} (ORA-01031). "
                        "La cuenta de aplicación necesita CREATE TABLE y CREATE SEQUENCE "
                        "para las columnas IDENTITY. Solicite esos permisos en la misma PDB "
                        "y repita usando la cuenta existente. No es necesario otorgar DBA."
                    ) from None
                raise
            created.append(name)
        connection.commit()
        cursor.execute("SELECT ID_DEPARTAMENTO, NOMBRE FROM DEPARTAMENTO ORDER BY ID_DEPARTAMENTO")
        departments = cursor.fetchall()
        return created, departments
    except Exception:
        connection.rollback()
        raise
    finally:
        try:
            if cursor is not None:
                cursor.close()
        finally:
            connection.close()
