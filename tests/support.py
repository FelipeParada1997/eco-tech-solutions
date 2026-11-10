"""Repositorio en memoria SOLO para probar servicios y Qt sin un servidor."""
from contextlib import contextmanager
from copy import deepcopy
from datetime import date
from ecotech.entities import (Empleado, Administrador, Departamento, Proyecto,
                              EmpleadoProyecto, TrabajoRealizado, CuentaUsuario)
from ecotech.security.passwords import crear_hash

PASSWORD = 'ClavePruebas123!'


class Cursor:
    def __init__(self, repository):
        self.repository = repository
        self.fila = (1,)

    def execute(self, sql, parametros=None):
        if sql == 'SELECT COUNT(*) FROM EMPLEADO':
            self.fila = (len(self.repository.empleados),)
        elif sql == 'SELECT COUNT(*) FROM USUARIO':
            self.fila = (len(self.repository.cuentas),)
        elif 'FROM PROYECTO' in sql and 'FOR UPDATE' in sql:
            self.fila = (parametros['id'],) if parametros['id'] in self.repository.proyectos else None

    def fetchone(self):
        return self.fila

    def fetchall(self):
        return []


class MemoryRepository:
    def __init__(self, password_hash=None):
        password_hash = password_hash or crear_hash(PASSWORD)
        datos = dict(direccion='Calle 123', telefono='+56912345678',
                     fecha_inicio_contrato=date(2026, 1, 1), salario=1000, id_departamento=1)
        self.empleados = {
            1: Administrador('Ana RRHH', correo_electronico='ana@example.test', tipo_empleado='RECURSOS_HUMANOS', id_empleado=1, **datos),
            2: Empleado('Pedro', correo_electronico='pedro@example.test', tipo_empleado='VENDEDOR', id_empleado=2, **datos),
            3: Empleado('Gerente', correo_electronico='gerente@example.test', tipo_empleado='GERENTE', id_empleado=3, **datos),
        }
        self.departamentos = {1: Departamento('Administración', 3, 1)}
        self.proyectos = {1: Proyecto('Solar', 'Paneles', date(2026, 1, 1), 1)}
        self.asignaciones = {1: EmpleadoProyecto(2, 1, True, 1)}
        self.horas = {}
        self.cuentas = {
            'admin': CuentaUsuario('admin', password_hash, 1, 'ADMIN', id_cuenta=1),
            'pedro': CuentaUsuario('pedro', password_hash, 2, id_cuenta=2),
        }
        self.transacciones = 0

    @contextmanager
    def transaccion(self, escritura=False):
        self.transacciones += 1
        previo = deepcopy((self.empleados, self.departamentos, self.proyectos,
                           self.asignaciones, self.horas, self.cuentas))
        try:
            yield Cursor(self)
        except Exception:
            if escritura:
                (self.empleados, self.departamentos, self.proyectos,
                 self.asignaciones, self.horas, self.cuentas) = previo
            raise

    def bloquear_empleado(self, c, id_empleado):
        if id_empleado not in self.empleados:
            raise ValueError('El empleado no existe.')

    def listar_empleados(self, c):
        return deepcopy(list(self.empleados.values()))

    def obtener_empleado(self, c, id_empleado):
        if id_empleado not in self.empleados:
            raise ValueError('El empleado no existe.')
        return deepcopy(self.empleados[id_empleado])

    def guardar_empleado(self, c, empleado):
        id_empleado = empleado.id_empleado or max(self.empleados, default=0) + 1
        empleado = deepcopy(empleado)
        empleado._id_empleado = id_empleado
        self.empleados[id_empleado] = empleado
        return id_empleado

    def listar_departamentos(self, c):
        return deepcopy(list(self.departamentos.values()))

    def guardar_departamento(self, c, departamento):
        id_depto = departamento.id_departamento or max(self.departamentos, default=0) + 1
        self.departamentos[id_depto] = Departamento(departamento.nombre, departamento.id_gerente, id_depto)
        return id_depto

    def eliminar_departamento(self, c, id_depto):
        del self.departamentos[id_depto]

    def listar_proyectos(self, c):
        return deepcopy(list(self.proyectos.values()))

    def guardar_proyecto(self, c, proyecto):
        id_proyecto = proyecto.id_proyecto or max(self.proyectos, default=0) + 1
        self.proyectos[id_proyecto] = Proyecto(proyecto.nombre, proyecto.descripcion, proyecto.fecha_inicio, id_proyecto)
        return id_proyecto

    def eliminar_proyecto(self, c, id_proyecto):
        del self.proyectos[id_proyecto]

    def listar_asignaciones(self, c):
        return deepcopy(list(self.asignaciones.values()))

    def guardar_asignacion(self, c, asignacion):
        id_asignacion = next((a.id_empleado_proyecto for a in self.asignaciones.values()
                              if a.id_empleado == asignacion.id_empleado and a.id_proyecto == asignacion.id_proyecto),
                             max(self.asignaciones, default=0) + 1)
        self.asignaciones[id_asignacion] = EmpleadoProyecto(asignacion.id_empleado, asignacion.id_proyecto,
                                                          asignacion.activa, id_asignacion)
        return id_asignacion

    def listar_horas(self, c):
        return deepcopy(list(self.horas.values()))

    def guardar_horas(self, c, trabajo):
        id_trabajo = trabajo.id_trabajo or max(self.horas, default=0) + 1
        self.horas[id_trabajo] = TrabajoRealizado(trabajo.id_empleado, trabajo.id_proyecto,
                                                trabajo.fecha, trabajo.horas_trabajadas,
                                                trabajo.descripcion_tareas_realizadas, id_trabajo)
        return id_trabajo

    def obtener_cuenta(self, c, nombre):
        return deepcopy(self.cuentas.get(nombre))

    def listar_cuentas(self, c):
        return [(cuenta.id_cuenta, nombre, cuenta.id_titular, cuenta.rol, 'S' if cuenta.activo else 'N')
                for nombre, cuenta in self.cuentas.items()]

    def crear_cuenta(self, c, usuario, password_hash, empleado, rol):
        if usuario in self.cuentas or any(u.id_titular == empleado for u in self.cuentas.values()):
            raise ValueError('Ya existe una cuenta con ese usuario o empleado.')
        id_cuenta = len(self.cuentas) + 1
        self.cuentas[usuario] = CuentaUsuario(usuario, password_hash, empleado, rol, id_cuenta=id_cuenta)
        return id_cuenta
