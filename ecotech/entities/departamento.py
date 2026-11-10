from ecotech import validation as v


class Departamento:
    def __init__(self, nombre, id_gerente, id_departamento=None):
        self._id_departamento = v.identificador(id_departamento) if id_departamento is not None else None
        self.editar_departamento(nombre, id_gerente)

    @property
    def id_departamento(self):
        return self._id_departamento

    @property
    def nombre(self):
        return self._nombre

    @property
    def id_gerente(self):
        return self._id_gerente

    def editar_departamento(self, nombre, gerente):
        nombre, gerente = v.texto(nombre, 'Departamento'), v.identificador(gerente)
        self._nombre, self._id_gerente = nombre, gerente
