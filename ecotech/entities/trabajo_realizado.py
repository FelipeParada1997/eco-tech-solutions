from decimal import Decimal
from ecotech import validation as v


class TrabajoRealizado:
    def __init__(self, id_empleado, id_proyecto, fecha, horas, descripcion, id_trabajo=None):
        self._id_trabajo = v.identificador(id_trabajo) if id_trabajo is not None else None
        self._id_empleado = v.identificador(id_empleado)
        self._id_proyecto = v.identificador(id_proyecto)
        self.modificar_registro(fecha, horas, descripcion)

    @property
    def id_trabajo(self):
        return self._id_trabajo

    @property
    def id_trabajo_realizado(self):
        return self._id_trabajo

    @property
    def id_empleado(self):
        return self._id_empleado

    @property
    def id_proyecto(self):
        return self._id_proyecto

    @property
    def fecha(self):
        return self._fecha

    @property
    def horas_trabajadas(self):
        return self._horas

    @property
    def descripcion_tareas_realizadas(self):
        return self._descripcion

    def modificar_registro(self, fecha, horas, descripcion):
        datos = (v.fecha(fecha), v.cantidad(horas, 'Horas', Decimal('0.01'), Decimal('24')),
                 v.texto(descripcion, 'Descripción de tareas', 1000))
        self._fecha, self._horas, self._descripcion = datos

    def validar(self):
        self.modificar_registro(self.fecha, self.horas_trabajadas, self.descripcion_tareas_realizadas)
        return True
