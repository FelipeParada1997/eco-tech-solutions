"""Empleado encapsula los datos personales y valida sus cambios."""
from enum import Enum
from ecotech import validation as v


class TipoEmpleado(str, Enum):
    GERENTE = 'GERENTE'
    RECURSOS_HUMANOS = 'RECURSOS_HUMANOS'
    VENDEDOR = 'VENDEDOR'


class Empleado:
    def __init__(self, nombre, direccion, telefono, correo_electronico,
                 fecha_inicio_contrato, salario, tipo_empleado, id_departamento,
                 id_empleado=None):
        self._id_empleado = v.identificador(id_empleado) if id_empleado is not None else None
        # Validar primero: una edición inválida no cambia parcialmente el objeto.
        datos = (v.texto(nombre, 'Nombre'), v.texto(direccion, 'Dirección', 500),
                 v.telefono(telefono), v.correo(correo_electronico),
                 v.fecha(fecha_inicio_contrato), v.cantidad(salario, 'Salario'),
                 TipoEmpleado(tipo_empleado), v.identificador(id_departamento))
        (self._nombre, self._direccion, self._telefono, self._correo_electronico,
         self._fecha_inicio_contrato, self._salario, self._tipo_empleado,
         self._id_departamento) = datos

    @property
    def id_empleado(self):
        return self._id_empleado

    @property
    def nombre(self):
        return self._nombre

    @property
    def direccion(self):
        return self._direccion

    @property
    def telefono(self):
        return self._telefono

    @property
    def correo_electronico(self):
        return self._correo_electronico

    @property
    def fecha_inicio_contrato(self):
        return self._fecha_inicio_contrato

    @property
    def salario(self):
        return self._salario

    @property
    def tipo_empleado(self):
        return self._tipo_empleado

    @property
    def id_departamento(self):
        return self._id_departamento

    def asignar_departamento(self, departamento):
        self._id_departamento = v.identificador(departamento.id_departamento)

    def reasignar_departamento(self, nuevo):
        self.asignar_departamento(nuevo)

    def registrar_trabajo(self, proyecto, fecha, horas, descripcion):
        from .trabajo_realizado import TrabajoRealizado
        return TrabajoRealizado(self.id_empleado, proyecto.id_proyecto, fecha, horas, descripcion)

    def validar_datos(self):
        # El constructor contiene las mismas reglas para altas y lecturas de Oracle.
        Empleado(self.nombre, self.direccion, self.telefono, self.correo_electronico,
                 self.fecha_inicio_contrato, self.salario, self.tipo_empleado,
                 self.id_departamento, self.id_empleado)
        return True


class Administrador(Empleado):
    """Es un empleado de RRHH; la cuenta decide sus permisos efectivos."""
    def registrar_empleado(self, nombre, direccion, telefono, correo_electronico,
                           fecha_inicio_contrato, salario, tipo_empleado,
                           id_departamento, id_empleado=None):
        return Empleado(nombre, direccion, telefono, correo_electronico,
                        fecha_inicio_contrato, salario, tipo_empleado,
                        id_departamento, id_empleado)

    def generar_informe(self, titulo, secciones):
        from ecotech.reports.informe import Informe
        return Informe.generar(titulo, secciones)
