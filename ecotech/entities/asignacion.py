from ecotech import validation as v


class EmpleadoProyecto:
    def __init__(self, id_empleado, id_proyecto, activa=True, id_empleado_proyecto=None):
        self._id_empleado = v.identificador(id_empleado)
        self._id_proyecto = v.identificador(id_proyecto)
        self._id_empleado_proyecto = (v.identificador(id_empleado_proyecto)
                                     if id_empleado_proyecto is not None else None)
        if not isinstance(activa, bool):
            raise ValueError('El estado de asignación debe ser booleano.')
        self._activa = activa

    @property
    def id_empleado_proyecto(self):
        return self._id_empleado_proyecto

    @property
    def id_empleado(self):
        return self._id_empleado

    @property
    def id_proyecto(self):
        return self._id_proyecto

    @property
    def activa(self):
        return self._activa

    def asignar(self):
        self._activa = True

    def desasignar(self):
        self._activa = False
