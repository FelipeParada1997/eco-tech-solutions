"""Uso: python -m ecotech.scripts.crear_tablas"""
from ecotech.database.schema import instalar
from ecotech.database.errors import DatabaseError


def main():
    print("=== INSTALAR TABLAS ECOTECH ===")
    try:
        created, departments = instalar()
    except DatabaseError as error:
        code = getattr(error.args[0], "code", None) if error.args else None
        if code == 1017:
            print("Oracle rechazó ORACLE_USER/ORACLE_PASSWORD del .env. No se crearon tablas.")
            print("Use una cuenta Oracle existente; el usuario de acceso a EcoTech se crea después.")
        elif code in (1031, 1950):
            print("La cuenta Oracle necesita CREATE TABLE, CREATE SEQUENCE y cuota en su tablespace.")
        else:
            print("No se pudo completar la instalación:", error)
        print("Corrija la causa y vuelva a ejecutar; los objetos existentes se conservan.")
        return 1
    except ValueError as error:
        print(error)
        return 1
    print(f"Esquema listo. Objetos nuevos: {len(created)}.")
    for identifier, name in departments:
        print(f"Departamento disponible: ID {identifier} — {name}")
    print("Ahora ejecute: python -m ecotech.scripts.crear_admin")
    print("Después inicie: python -m ecotech")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
