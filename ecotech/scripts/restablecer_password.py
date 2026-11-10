"""Recuperación local de un administrador. Ejecutar con la aplicación cerrada."""
from getpass import getpass
from ecotech import validation as v
from ecotech.repositories.oracle import OracleRepository
from ecotech.security.passwords import crear_hash


def restablecer_password():
    try:
        nombre = v.usuario(input('Usuario administrador a recuperar: '))
        password = getpass('Nueva contraseña: ')
        if password != getpass('Repita la contraseña: '):
            raise ValueError('Las contraseñas no coinciden.')
        codificado = crear_hash(password)
        repo = OracleRepository()
        with repo.transaccion(True) as c:
            c.execute("UPDATE USUARIO SET PASSWORD_HASH=:hash WHERE NOMBRE_USUARIO=:usuario AND ROL='ADMIN'",
                      {'hash': codificado, 'usuario': nombre})
            if c.rowcount != 1:
                raise ValueError('No existe ese administrador.')
        print('Contraseña actualizada. Puede iniciar la aplicación.')
        return 0
    except (ValueError, OSError) as error:
        print('No se actualizó la contraseña:', error)
        return 1


if __name__ == '__main__':
    raise SystemExit(restablecer_password())
