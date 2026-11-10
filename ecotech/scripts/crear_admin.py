"""Completar la carga inicial tras crear las tablas. No agrega administradores extra."""
from getpass import getpass
from ecotech.repositories.oracle import OracleRepository
from ecotech.services.inicializacion import preparar_datos


def crear_admin():
    usuario = input('Usuario del administrador inicial: ').strip()
    password = getpass('Contraseña (12 a 128 caracteres, letras y números): ')
    if password != getpass('Repita la contraseña: '):
        print('Las contraseñas no coinciden.')
        return 1
    try:
        nuevo = preparar_datos(OracleRepository(), usuario, password)
        print('Administrador creado.' if nuevo else 'Administrador existente verificado.')
        return 0
    except (ValueError, OSError) as error:
        print('No se completó la carga inicial:', error)
        return 1


if __name__ == '__main__':
    raise SystemExit(crear_admin())
