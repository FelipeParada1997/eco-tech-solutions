"""Reglas y permisos. La interfaz no puede saltarlos ocultando o mostrando botones."""
from ecotech import validation as v
from ecotech.entities import (Administrador, Departamento, Proyecto,
                              EmpleadoProyecto, TipoEmpleado)
from ecotech.repositories.oracle import OracleRepository
from ecotech.security.passwords import crear_hash


class GestionService:
    def __init__(self, cuenta, repository=None):
        self.cuenta = cuenta
        self.repository = repository if repository is not None else OracleRepository()

    @property
    def es_admin(self):
        return self.cuenta.rol == 'ADMIN'

    def autorizar(self, modulo, escritura=False):
        if not self.cuenta.tiene_permiso(modulo):
            raise PermissionError('La sesión terminó o no tiene permiso para este módulo.')
        if escritura and not self.es_admin:
            raise PermissionError('Esta operación corresponde al administrador.')

    def cerrar_sesion(self):
        self.cuenta.cerrar_sesion()

    def listar_empleados(self, buscar=''):
        self.autorizar('empleados')
        with self.repository.transaccion() as cursor:
            empleados = self.repository.listar_empleados(cursor)
        if not self.es_admin:
            empleados = [e for e in empleados if e.id_empleado == self.cuenta.id_titular]
        termino = buscar.strip().casefold()
        return [e for e in empleados if not termino or termino in e.nombre.casefold() or termino == str(e.id_empleado)]

    def guardar_empleado(self, datos, id_empleado=None):
        self.autorizar('empleados', escritura=True)
        if id_empleado is not None:
            id_empleado = v.identificador(id_empleado)
        with self.repository.transaccion(True) as cursor:
            administrador = self.repository.obtener_empleado(cursor, self.cuenta.id_titular)
            if not isinstance(administrador, Administrador):
                raise ValueError('El administrador debe ser un empleado de Recursos Humanos.')
            empleado = administrador.registrar_empleado(
                datos['nombre'], datos['direccion'], datos['telefono'],
                datos['correo_electronico'], datos['fecha_inicio_contrato'],
                datos['salario'], datos['tipo_empleado'], datos['id_departamento'],
                id_empleado)
            departamentos = self.repository.listar_departamentos(cursor)
            if not any(d.id_departamento == empleado.id_departamento for d in departamentos):
                raise ValueError('El departamento no existe.')
            # Bloqueo común para las comprobaciones que dependen del conjunto de empleados.
            cursor.execute('SELECT ID_DEPARTAMENTO FROM DEPARTAMENTO ORDER BY ID_DEPARTAMENTO FOR UPDATE')
            cursor.fetchall()
            existentes = self.repository.listar_empleados(cursor)
            for otro in existentes:
                if otro.id_empleado != id_empleado and otro.correo_electronico == empleado.correo_electronico:
                    raise ValueError('Ya existe un empleado con ese correo.')
            if id_empleado is not None:
                anterior = self.repository.obtener_empleado(cursor, id_empleado)
                if anterior.tipo_empleado != empleado.tipo_empleado:
                    raise ValueError('El cargo no se cambia desde este formulario. Cree el empleado con su cargo correcto.')
                if any(t.id_empleado == id_empleado and t.fecha < empleado.fecha_inicio_contrato
                       for t in self.repository.listar_horas(cursor)):
                    raise ValueError('El contrato no puede comenzar después de horas ya registradas.')
            return self.repository.guardar_empleado(cursor, empleado)

    def listar_departamentos(self, buscar=''):
        self.autorizar('departamentos')
        with self.repository.transaccion() as cursor:
            departamentos = self.repository.listar_departamentos(cursor)
        termino = buscar.strip().casefold()
        return [d for d in departamentos if not termino or termino in d.nombre.casefold() or termino == str(d.id_departamento)]

    def guardar_departamento(self, nombre, gerente, id_departamento=None):
        self.autorizar('departamentos', escritura=True)
        departamento = Departamento(nombre, gerente, id_departamento)
        with self.repository.transaccion(True) as cursor:
            empleado = self.repository.obtener_empleado(cursor, departamento.id_gerente)
            if empleado.tipo_empleado != TipoEmpleado.GERENTE:
                raise ValueError('Seleccione un empleado con cargo GERENTE.')
            return self.repository.guardar_departamento(cursor, departamento)

    def eliminar_departamento(self, id_departamento):
        self.autorizar('departamentos', escritura=True)
        id_departamento = v.identificador(id_departamento)
        with self.repository.transaccion(True) as cursor:
            if any(e.id_departamento == id_departamento for e in self.repository.listar_empleados(cursor)):
                raise ValueError('Reasigne los empleados antes de eliminar su departamento.')
            self.repository.eliminar_departamento(cursor, id_departamento)

    def reasignar_departamento(self, empleado_id, departamento_id):
        self.autorizar('empleados', escritura=True)
        empleado_id, departamento_id = v.identificador(empleado_id), v.identificador(departamento_id)
        with self.repository.transaccion(True) as cursor:
            self.repository.bloquear_empleado(cursor, empleado_id)
            empleado = self.repository.obtener_empleado(cursor, empleado_id)
            departamento = next((d for d in self.repository.listar_departamentos(cursor)
                                 if d.id_departamento == departamento_id), None)
            if departamento is None:
                raise ValueError('El departamento no existe.')
            empleado.reasignar_departamento(departamento)
            self.repository.guardar_empleado(cursor, empleado)

    def listar_proyectos(self, buscar=''):
        self.autorizar('proyectos')
        with self.repository.transaccion() as cursor:
            proyectos = self.repository.listar_proyectos(cursor)
            if not self.es_admin:
                ids = {a.id_proyecto for a in self.repository.listar_asignaciones(cursor)
                       if a.id_empleado == self.cuenta.id_titular}
                proyectos = [p for p in proyectos if p.id_proyecto in ids]
        termino = buscar.strip().casefold()
        return [p for p in proyectos if not termino or termino in p.nombre.casefold() or termino == str(p.id_proyecto)]

    def guardar_proyecto(self, nombre, descripcion, fecha_inicio, id_proyecto=None):
        self.autorizar('proyectos', escritura=True)
        proyecto = Proyecto(nombre, descripcion, fecha_inicio, id_proyecto)
        with self.repository.transaccion(True) as cursor:
            if id_proyecto is not None:
                cursor.execute('SELECT ID_PROYECTO FROM PROYECTO WHERE ID_PROYECTO=:id FOR UPDATE', {'id': proyecto.id_proyecto})
                if cursor.fetchone() is None:
                    raise ValueError('El proyecto no existe.')
                if any(t.id_proyecto == proyecto.id_proyecto and t.fecha < proyecto.fecha_inicio
                       for t in self.repository.listar_horas(cursor)):
                    raise ValueError('El inicio no puede ser posterior a horas ya registradas.')
            return self.repository.guardar_proyecto(cursor, proyecto)

    def eliminar_proyecto(self, id_proyecto):
        self.autorizar('proyectos', escritura=True)
        id_proyecto = v.identificador(id_proyecto)
        with self.repository.transaccion(True) as cursor:
            if any(a.id_proyecto == id_proyecto for a in self.repository.listar_asignaciones(cursor)):
                raise ValueError('No se elimina un proyecto con asignaciones, incluidas las inactivas: conserva su trazabilidad.')
            self.repository.eliminar_proyecto(cursor, id_proyecto)

    def listar_asignaciones(self):
        self.autorizar('asignaciones')
        with self.repository.transaccion() as cursor:
            asignaciones = self.repository.listar_asignaciones(cursor)
        return [a for a in asignaciones if self.es_admin or a.id_empleado == self.cuenta.id_titular]

    def asignar_proyecto(self, empleado_id, proyecto_id, activa=True):
        self.autorizar('asignaciones', escritura=True)
        asignacion = EmpleadoProyecto(empleado_id, proyecto_id, activa)
        with self.repository.transaccion(True) as cursor:
            self.repository.bloquear_empleado(cursor, asignacion.id_empleado)
            if not any(p.id_proyecto == asignacion.id_proyecto for p in self.repository.listar_proyectos(cursor)):
                raise ValueError('El proyecto no existe.')
            if not activa:
                existente = next((a for a in self.repository.listar_asignaciones(cursor)
                                  if a.id_empleado == asignacion.id_empleado and a.id_proyecto == asignacion.id_proyecto), None)
                if existente is None:
                    raise ValueError('La asignación no existe.')
                existente.desasignar()
                asignacion = existente
            else:
                asignacion.asignar()
            self.repository.guardar_asignacion(cursor, asignacion)

    def listar_horas(self):
        self.autorizar('horas')
        with self.repository.transaccion() as cursor:
            horas = self.repository.listar_horas(cursor)
        return [t for t in horas if self.es_admin or t.id_empleado == self.cuenta.id_titular]

    def guardar_horas(self, proyecto_id, fecha, horas, descripcion, id_trabajo=None):
        self.autorizar('horas')
        proyecto_id = v.identificador(proyecto_id)
        if id_trabajo is not None:
            id_trabajo = v.identificador(id_trabajo)
        with self.repository.transaccion(True) as cursor:
            # El autor siempre se toma de la cuenta: no se acepta un ID desde la vista.
            empleado_id = self.cuenta.id_titular
            self.repository.bloquear_empleado(cursor, empleado_id)
            cursor.execute('SELECT ID_PROYECTO FROM PROYECTO WHERE ID_PROYECTO=:id FOR UPDATE', {'id': proyecto_id})
            if cursor.fetchone() is None:
                raise ValueError('El proyecto no existe.')
            empleado = self.repository.obtener_empleado(cursor, empleado_id)
            proyecto = next(p for p in self.repository.listar_proyectos(cursor) if p.id_proyecto == proyecto_id)
            asignacion = next((a for a in self.repository.listar_asignaciones(cursor)
                               if a.id_empleado == empleado_id and a.id_proyecto == proyecto_id and a.activa), None)
            if asignacion is None:
                raise ValueError('Necesita una asignación activa a ese proyecto.')
            trabajo = empleado.registrar_trabajo(proyecto, fecha, horas, descripcion)
            registros = self.repository.listar_horas(cursor)
            if id_trabajo is not None:
                trabajo = next((t for t in registros if t.id_trabajo == id_trabajo
                                and t.id_empleado == empleado_id), None)
                if trabajo is None or trabajo.id_proyecto != proyecto_id:
                    raise PermissionError('Solo puede corregir sus horas conservando el proyecto original.')
                trabajo.modificar_registro(fecha, horas, descripcion)
            if trabajo.fecha < max(empleado.fecha_inicio_contrato, proyecto.fecha_inicio):
                raise ValueError('La fecha debe ser posterior o igual al inicio del contrato y del proyecto.')
            total = sum(t.horas_trabajadas for t in registros if t.id_empleado == empleado_id
                        and t.fecha == trabajo.fecha and t.id_trabajo != id_trabajo)
            if total + trabajo.horas_trabajadas > 24:
                raise ValueError('El total de horas del empleado no puede superar 24 en un día.')
            return self.repository.guardar_horas(cursor, trabajo)

    def listar_cuentas(self):
        self.autorizar('cuentas', escritura=True)
        with self.repository.transaccion() as cursor:
            return self.repository.listar_cuentas(cursor)

    def crear_cuenta(self, empleado_id, usuario, password, rol):
        self.autorizar('cuentas', escritura=True)
        empleado_id, usuario = v.identificador(empleado_id), v.usuario(usuario)
        if rol not in ('ADMIN', 'EMPLEADO'):
            raise ValueError('Rol inválido.')
        password_hash = crear_hash(password)
        with self.repository.transaccion(True) as cursor:
            empleado = self.repository.obtener_empleado(cursor, empleado_id)
            if rol == 'ADMIN' and not isinstance(empleado, Administrador):
                raise ValueError('Una cuenta ADMIN corresponde a un empleado de Recursos Humanos. El cargo por sí solo no concede acceso.')
            return self.repository.crear_cuenta(cursor, usuario, password_hash, empleado_id, rol)

    def generar_informe(self):
        self.autorizar('informes', escritura=True)
        from ecotech.reports.informe import Seccion
        with self.repository.transaccion() as cursor:
            # Una misma instantánea consistente de Oracle para las cuatro áreas.
            cursor.execute('SET TRANSACTION READ ONLY')
            empleados = self.repository.listar_empleados(cursor)
            departamentos = self.repository.listar_departamentos(cursor)
            proyectos = self.repository.listar_proyectos(cursor)
            trabajos = self.repository.listar_horas(cursor)
            administrador = next(e for e in empleados if e.id_empleado == self.cuenta.id_titular)
            if not isinstance(administrador, Administrador):
                raise ValueError('La cuenta administradora debe pertenecer a Recursos Humanos.')
            secciones = [
                Seccion('Empleados', ('ID', 'Nombre', 'Correo', 'Departamento', 'Cargo', 'Salario'),
                        [(e.id_empleado, e.nombre, e.correo_electronico, e.id_departamento,
                          e.tipo_empleado.value, e.salario) for e in empleados]),
                Seccion('Departamentos', ('ID', 'Nombre', 'Gerente'),
                        [(d.id_departamento, d.nombre, d.id_gerente) for d in departamentos]),
                Seccion('Proyectos', ('ID', 'Nombre', 'Descripción', 'Inicio'),
                        [(p.id_proyecto, p.nombre, p.descripcion, p.fecha_inicio) for p in proyectos]),
                Seccion('Horas', ('ID', 'Empleado', 'Proyecto', 'Fecha', 'Horas', 'Tareas'),
                        [(t.id_trabajo, t.id_empleado, t.id_proyecto, t.fecha,
                          t.horas_trabajadas, t.descripcion_tareas_realizadas) for t in trabajos]),
            ]
            return administrador.generar_informe('Informe de gestión EcoTech', secciones)
