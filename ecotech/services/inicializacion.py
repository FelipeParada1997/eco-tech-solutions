"""Primera carga: dos empleados ficticios resuelven gerente y administrador."""
from datetime import date
from ecotech.entities import Empleado, TipoEmpleado
from ecotech import validation as v
from ecotech.security.cifrado import crear_clave, ruta_clave, Cifrado
from ecotech.security.passwords import crear_hash, validar_password


def preparar_datos(repository, usuario, password):
    usuario = v.usuario(usuario)
    validar_password(password)
    with repository.transaccion() as c:
        c.execute('SELECT COUNT(*) FROM EMPLEADO')
        cantidad = c.fetchone()[0]
    if not ruta_clave().exists():
        if cantidad:
            raise ValueError('Falta la clave de una base con empleados. Restaure el respaldo; no se generó otra clave.')
        try:
            crear_clave()
        except FileExistsError:
            pass  # Otra instalación pudo crearla; se valida inmediatamente.
    repository._cifrado = Cifrado()
    password_hash = crear_hash(password)
    with repository.transaccion(True) as c:
        existente = repository.obtener_cuenta(c, usuario)
        if existente is not None:
            if existente.rol != 'ADMIN' or not existente.autenticar(password):
                raise ValueError('El usuario ya existe y no coincide con un administrador activo con esa contraseña.')
            existente.cerrar_sesion()
            return False
        c.execute('SELECT COUNT(*) FROM USUARIO')
        if c.fetchone()[0]:
            raise ValueError('Ya existe una instalación. Cree cuentas desde el administrador; no se cambió ningún acceso.')
        if cantidad or repository.listar_departamentos(c):
            raise ValueError('El esquema contiene datos sin cuenta inicial. Revise la instalación; no se insertaron datos adicionales.')
        # 0 es un marcador transitorio, nunca se confirma: la FK se comprueba al commit.
        departamento = repository.insertar(c,
            'INSERT INTO DEPARTAMENTO (NOMBRE,ID_GERENTE) VALUES (:nombre,:gerente)',
            {'nombre': 'Administración inicial', 'gerente': 0, '_columna_id': 'ID_DEPARTAMENTO'})
        datos = dict(direccion='Dirección de ejemplo', telefono='000000000',
                     fecha_inicio_contrato=date.today(), salario=0, id_departamento=departamento)
        gerente = Empleado('Gerente inicial (editar)', correo_electronico='gerente@example.test',
                           tipo_empleado=TipoEmpleado.GERENTE, **datos)
        id_gerente = repository.guardar_empleado(c, gerente)
        c.execute('UPDATE DEPARTAMENTO SET ID_GERENTE=:gerente WHERE ID_DEPARTAMENTO=:id',
                  {'gerente': id_gerente, 'id': departamento})
        administrador = Empleado('Administrador inicial (editar)', correo_electronico='admin@example.test',
                                 tipo_empleado=TipoEmpleado.RECURSOS_HUMANOS, **datos)
        id_admin = repository.guardar_empleado(c, administrador)
        repository.crear_cuenta(c, usuario, password_hash, id_admin, 'ADMIN')
    return True
