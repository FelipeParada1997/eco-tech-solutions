"""Instala las tablas y el primer administrador usando el Oracle del .env."""
import argparse
from getpass import getpass

from ecotech.config import USUARIO, CONTRASENIA, DSN
from ecotech.database.errors import DatabaseError
from ecotech.database.schema import instalar as instalar_tablas
from ecotech.repositories.oracle import OracleRepository
from ecotech.security.passwords import validar_password
from ecotech.services.inicializacion import preparar_datos
from ecotech.validation import usuario as validar_usuario


def main(argv=None):
    parser = argparse.ArgumentParser(
        description='Crear tablas y administrador con una cuenta Oracle ya configurada en .env.')
    parser.parse_args(argv)
    print('=== INSTALAR ECOTECH ===')
    try:
        if not all((USUARIO, CONTRASENIA, DSN)):
            raise ValueError('Complete ORACLE_USER, ORACLE_PASSWORD y ORACLE_DSN en .env.')
        if USUARIO.upper() in ('SYS', 'SYSTEM'):
            raise ValueError('Use una cuenta Oracle dedicada al proyecto, no SYS ni SYSTEM.')

        nombre = validar_usuario(input('Usuario administrador de EcoTech: '))
        password = getpass('Contraseña (12 a 128 caracteres, letras y números): ')
        validar_password(password)
        if password != getpass('Repita la contraseña: '):
            raise ValueError('Las contraseñas no coinciden.')

        # Validar las entradas antes del DDL: Oracle confirma los cambios de estructura.
        objetos, _ = instalar_tablas()
        nuevo = preparar_datos(OracleRepository(), nombre, password)
        print(f'Esquema listo. Objetos nuevos: {len(objetos)}.')
        print('Administrador creado.' if nuevo else 'Administrador existente verificado.')
        print('Inicie con: python -m ecotech')
        return 0
    except (EOFError, KeyboardInterrupt):
        print('\nInstalación interrumpida. Puede corregir la causa y repetir.')
    except (ValueError, OSError) as error:
        print('No se completó la instalación:', error)
    except DatabaseError as error:
        # El mensaje original podría contener información sensible; mostrar solo el código.
        detalle = error.args[0] if error.args else None
        codigo = getattr(detalle, 'full_code', '')
        print('No se pudo instalar en Oracle. Revise .env, la PDB, los permisos y la cuota.', codigo)
    print('Los objetos ya creados se conservan; la carga de datos fallida se revierte.')
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
