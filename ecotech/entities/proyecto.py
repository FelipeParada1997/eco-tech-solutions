from ecotech import validation as v


class Proyecto:
    def __init__(self, nombre, descripcion, fecha_inicio, id_proyecto=None):
        self._id_proyecto = v.identificador(id_proyecto) if id_proyecto is not None else None
        self.editar_proyecto(nombre, descripcion, fecha_inicio)

    @property
    def id_proyecto(self):
        return self._id_proyecto

    @property
    def nombre(self):
        return self._nombre

    @property
    def descripcion(self):
        return self._descripcion

    @property
    def fecha_inicio(self):
        return self._fecha_inicio

    def editar_proyecto(self, nombre, descripcion, fecha_inicio):
        datos = v.texto(nombre, 'Proyecto'), v.texto(descripcion, 'Descripción', 1000), v.fecha(fecha_inicio)
        self._nombre, self._descripcion, self._fecha_inicio = datos
