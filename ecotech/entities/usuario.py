from ecotech import validation as v
from ecotech.security.passwords import verificar_password

MODULOS_ADMIN = frozenset({'empleados', 'departamentos', 'proyectos', 'asignaciones', 'horas', 'informes', 'cuentas'})
MODULOS_EMPLEADO = frozenset({'empleados', 'departamentos', 'proyectos', 'asignaciones', 'horas'})


class CuentaUsuario:
    def __init__(self, nombre_usuario, password_hash, id_titular, rol='EMPLEADO',
                 activo=True, id_cuenta=None):
        if rol not in ('ADMIN', 'EMPLEADO'):
            raise ValueError('Rol inválido: elija ADMIN o EMPLEADO.')
        self._id_cuenta = v.identificador(id_cuenta) if id_cuenta is not None else None
        self._nombre_usuario = v.usuario(nombre_usuario)
        self._password_hash = password_hash
        self._id_titular = v.identificador(id_titular)
        self._rol = rol
        self._activo = bool(activo)
        self._sesion_activa = False
        self._permisos = MODULOS_ADMIN if rol == 'ADMIN' else MODULOS_EMPLEADO

    @property
    def id_cuenta(self):
        return self._id_cuenta

    @property
    def nombre_usuario(self):
        return self._nombre_usuario

    @property
    def id_titular(self):
        return self._id_titular

    @property
    def rol(self):
        return self._rol

    @property
    def activo(self):
        return self._activo

    @property
    def permisos(self):
        return self._permisos

    @property
    def sesion_activa(self):
        return self._sesion_activa

    def autenticar(self, password):
        self._sesion_activa = self.activo and verificar_password(password, self._password_hash)
        return self._sesion_activa

    def tiene_permiso(self, modulo):
        return self.activo and self.sesion_activa and modulo in self.permisos

    def cerrar_sesion(self):
        self._sesion_activa = False
