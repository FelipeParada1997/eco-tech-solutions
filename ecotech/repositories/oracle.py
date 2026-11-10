"""SQL de la aplicación. Todos los valores del usuario se envían como parámetros.

Los métodos reciben el cursor de una transacción iniciada por el servicio.
Así una operación de negocio se confirma completa o se revierte completa.
"""
from contextlib import contextmanager
from ecotech.database.connection import sesion
from ecotech.database.errors import DatabaseError
from ecotech.entities import (Empleado, Administrador, TipoEmpleado, Departamento,
                              Proyecto, EmpleadoProyecto, TrabajoRealizado, CuentaUsuario)
from ecotech.security.cifrado import Cifrado


class OracleRepository:
    def __init__(self, connection_factory=None, cifrado=None):
        self.connection_factory = connection_factory
        self._cifrado = cifrado

    @property
    def cifrado(self):
        if self._cifrado is None:
            self._cifrado = Cifrado()
        return self._cifrado

    @contextmanager
    def transaccion(self, escritura=False):
        try:
            with sesion(escritura, self.connection_factory) as cursor:
                yield cursor
        except DatabaseError as error:
            detalle = error.args[0] if error.args else None
            codigo = getattr(detalle, 'code', None)
            if codigo == 1:
                mensaje = 'Ya existe una cuenta o asignación con esos datos.'
            elif codigo == 2091:
                mensaje = 'Oracle revirtió la transacción al confirmar. Revise las restricciones y referencias pendientes.'
            elif codigo in (2291, 2292):
                mensaje = 'La operación tiene referencias pendientes. Revise empleados, departamentos, proyectos y asignaciones.'
            else:
                mensaje = 'No se pudo completar la operación en Oracle. Revise la conexión, el esquema y los permisos.'
            # El código ayuda a diagnosticar sin enviar SQL ni credenciales.
            codigo_seguro = getattr(detalle, 'full_code', '')
            if codigo_seguro:
                mensaje += f' ({codigo_seguro})'
            raise ValueError(mensaje) from None

    def insertar(self, cursor, sql, parametros):
        salida = cursor.var(int)
        cursor.execute(sql + ' RETURNING ' + parametros.pop('_columna_id') + ' INTO :nuevo_id',
                       dict(parametros, nuevo_id=salida))
        valor = salida.getvalue()
        return int(valor[0] if isinstance(valor, list) else valor)

    def bloquear_empleado(self, cursor, id_empleado):
        cursor.execute('SELECT ID_EMPLEADO FROM EMPLEADO WHERE ID_EMPLEADO=:id FOR UPDATE', {'id': id_empleado})
        if cursor.fetchone() is None:
            raise ValueError('El empleado no existe.')

    def listar_empleados(self, cursor):
        cursor.execute('SELECT ID_EMPLEADO, DATOS_CIFRADOS, TIPO_EMPLEADO, ID_DEPARTAMENTO FROM EMPLEADO ORDER BY ID_EMPLEADO')
        resultado = []
        for id_empleado, cifrado, tipo, departamento in cursor.fetchall():
            datos = self.cifrado.descifrar(cifrado)
            clase = Administrador if tipo == TipoEmpleado.RECURSOS_HUMANOS.value else Empleado
            resultado.append(clase(**datos, tipo_empleado=tipo, id_departamento=departamento,
                                   id_empleado=id_empleado))
        return resultado

    def obtener_empleado(self, cursor, id_empleado):
        # Reutiliza la conversión de filas. El volumen previsto es el de una entrega académica.
        for empleado in self.listar_empleados(cursor):
            if empleado.id_empleado == id_empleado:
                return empleado
        raise ValueError('El empleado no existe.')

    def guardar_empleado(self, cursor, empleado):
        datos = dict(nombre=empleado.nombre, direccion=empleado.direccion,
                     telefono=empleado.telefono, correo_electronico=empleado.correo_electronico,
                     fecha_inicio_contrato=empleado.fecha_inicio_contrato.isoformat(),
                     salario=str(empleado.salario))
        parametros = {'datos': self.cifrado.cifrar(datos), 'tipo': empleado.tipo_empleado.value,
                      'departamento': empleado.id_departamento}
        if empleado.id_empleado is None:
            parametros['_columna_id'] = 'ID_EMPLEADO'
            return self.insertar(cursor, 'INSERT INTO EMPLEADO (DATOS_CIFRADOS, TIPO_EMPLEADO, ID_DEPARTAMENTO) VALUES (:datos,:tipo,:departamento)', parametros)
        parametros['id'] = empleado.id_empleado
        cursor.execute('UPDATE EMPLEADO SET DATOS_CIFRADOS=:datos, TIPO_EMPLEADO=:tipo, ID_DEPARTAMENTO=:departamento WHERE ID_EMPLEADO=:id', parametros)
        if cursor.rowcount != 1:
            raise ValueError('El empleado no existe.')
        return empleado.id_empleado

    def listar_departamentos(self, cursor):
        cursor.execute('SELECT ID_DEPARTAMENTO, NOMBRE, ID_GERENTE FROM DEPARTAMENTO ORDER BY ID_DEPARTAMENTO')
        return [Departamento(nombre, gerente, id_depto) for id_depto, nombre, gerente in cursor.fetchall()]

    def guardar_departamento(self, cursor, departamento):
        parametros = {'nombre': departamento.nombre, 'gerente': departamento.id_gerente}
        if departamento.id_departamento is None:
            parametros['_columna_id'] = 'ID_DEPARTAMENTO'
            return self.insertar(cursor, 'INSERT INTO DEPARTAMENTO (NOMBRE, ID_GERENTE) VALUES (:nombre,:gerente)', parametros)
        parametros['id'] = departamento.id_departamento
        cursor.execute('UPDATE DEPARTAMENTO SET NOMBRE=:nombre, ID_GERENTE=:gerente WHERE ID_DEPARTAMENTO=:id', parametros)
        if cursor.rowcount != 1:
            raise ValueError('El departamento no existe.')
        return departamento.id_departamento

    def eliminar_departamento(self, cursor, id_departamento):
        cursor.execute('DELETE FROM DEPARTAMENTO WHERE ID_DEPARTAMENTO=:id', {'id': id_departamento})
        if cursor.rowcount != 1:
            raise ValueError('El departamento no existe.')

    def listar_proyectos(self, cursor):
        cursor.execute('SELECT ID_PROYECTO, NOMBRE, DESCRIPCION, FECHA_INICIO FROM PROYECTO ORDER BY ID_PROYECTO')
        return [Proyecto(nombre, descripcion, fecha, id_proyecto) for id_proyecto, nombre, descripcion, fecha in cursor.fetchall()]

    def guardar_proyecto(self, cursor, proyecto):
        parametros = {'nombre': proyecto.nombre, 'descripcion': proyecto.descripcion,
                      'fecha': proyecto.fecha_inicio}
        if proyecto.id_proyecto is None:
            parametros['_columna_id'] = 'ID_PROYECTO'
            return self.insertar(cursor, 'INSERT INTO PROYECTO (NOMBRE, DESCRIPCION, FECHA_INICIO) VALUES (:nombre,:descripcion,:fecha)', parametros)
        parametros['id'] = proyecto.id_proyecto
        cursor.execute('UPDATE PROYECTO SET NOMBRE=:nombre, DESCRIPCION=:descripcion, FECHA_INICIO=:fecha WHERE ID_PROYECTO=:id', parametros)
        if cursor.rowcount != 1:
            raise ValueError('El proyecto no existe.')
        return proyecto.id_proyecto

    def eliminar_proyecto(self, cursor, id_proyecto):
        cursor.execute('DELETE FROM PROYECTO WHERE ID_PROYECTO=:id', {'id': id_proyecto})
        if cursor.rowcount != 1:
            raise ValueError('El proyecto no existe.')

    def listar_asignaciones(self, cursor):
        cursor.execute('SELECT ID_ASIGNACION, ID_EMPLEADO, ID_PROYECTO, ACTIVA FROM ASIGNACION ORDER BY ID_ASIGNACION')
        return [EmpleadoProyecto(empleado, proyecto, activa == 'S', id_asignacion)
                for id_asignacion, empleado, proyecto, activa in cursor.fetchall()]

    def guardar_asignacion(self, cursor, asignacion):
        parametros = {'empleado': asignacion.id_empleado, 'proyecto': asignacion.id_proyecto,
                      'activa': 'S' if asignacion.activa else 'N'}
        cursor.execute('UPDATE ASIGNACION SET ACTIVA=:activa WHERE ID_EMPLEADO=:empleado AND ID_PROYECTO=:proyecto', parametros)
        if cursor.rowcount == 0:
            parametros['_columna_id'] = 'ID_ASIGNACION'
            return self.insertar(cursor, 'INSERT INTO ASIGNACION (ID_EMPLEADO,ID_PROYECTO,ACTIVA) VALUES (:empleado,:proyecto,:activa)', parametros)

    def listar_horas(self, cursor):
        cursor.execute('SELECT ID_TRABAJO,ID_EMPLEADO,ID_PROYECTO,FECHA,HORAS,DESCRIPCION FROM TRABAJO_REALIZADO ORDER BY FECHA DESC,ID_TRABAJO')
        return [TrabajoRealizado(empleado, proyecto, fecha, horas, descripcion, id_trabajo)
                for id_trabajo, empleado, proyecto, fecha, horas, descripcion in cursor.fetchall()]

    def guardar_horas(self, cursor, trabajo):
        parametros = {'empleado': trabajo.id_empleado, 'proyecto': trabajo.id_proyecto,
                      'fecha': trabajo.fecha, 'horas': trabajo.horas_trabajadas,
                      'descripcion': trabajo.descripcion_tareas_realizadas}
        if trabajo.id_trabajo is None:
            parametros['_columna_id'] = 'ID_TRABAJO'
            return self.insertar(cursor, 'INSERT INTO TRABAJO_REALIZADO (ID_EMPLEADO,ID_PROYECTO,FECHA,HORAS,DESCRIPCION) VALUES (:empleado,:proyecto,:fecha,:horas,:descripcion)', parametros)
        parametros['id'] = trabajo.id_trabajo
        # No permite cambiar el autor ni el proyecto al corregir un registro.
        cursor.execute('UPDATE TRABAJO_REALIZADO SET FECHA=:fecha,HORAS=:horas,DESCRIPCION=:descripcion WHERE ID_TRABAJO=:id AND ID_EMPLEADO=:empleado AND ID_PROYECTO=:proyecto', parametros)
        if cursor.rowcount != 1:
            raise ValueError('El registro no existe o no pertenece al empleado.')
        return trabajo.id_trabajo

    def obtener_cuenta(self, cursor, nombre):
        cursor.execute('SELECT ID_USUARIO,NOMBRE_USUARIO,PASSWORD_HASH,ID_EMPLEADO,ROL,ACTIVO FROM USUARIO WHERE NOMBRE_USUARIO=:nombre', {'nombre': nombre})
        fila = cursor.fetchone()
        if fila is None:
            return None
        id_cuenta, usuario, password_hash, titular, rol, activo = fila
        return CuentaUsuario(usuario, password_hash, titular, rol, activo == 'S', id_cuenta)

    def listar_cuentas(self, cursor):
        cursor.execute('SELECT ID_USUARIO,NOMBRE_USUARIO,ID_EMPLEADO,ROL,ACTIVO FROM USUARIO ORDER BY ID_USUARIO')
        return cursor.fetchall()

    def crear_cuenta(self, cursor, usuario, password_hash, empleado, rol):
        return self.insertar(cursor, 'INSERT INTO USUARIO (NOMBRE_USUARIO,PASSWORD_HASH,ID_EMPLEADO,ROL) VALUES (:usuario,:hash,:empleado,:rol)',
                             {'usuario': usuario, 'hash': password_hash, 'empleado': empleado,
                              'rol': rol, '_columna_id': 'ID_USUARIO'})
