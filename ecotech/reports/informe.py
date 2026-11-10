"""El informe conoce el contrato del exportador, no el formato del archivo."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from ecotech.validation import texto


@dataclass
class Seccion:
    titulo: str
    encabezados: tuple
    filas: list


class ExportadorInforme(ABC):
    @abstractmethod
    def exportar(self, informe):
        """Devuelve bytes de un documento."""


class Informe:
    def __init__(self, titulo, secciones):
        self._titulo = texto(titulo, 'Título')
        self._fecha_generacion = datetime.now()
        self._secciones = tuple(secciones)

    @property
    def titulo(self):
        return self._titulo

    @property
    def fecha_generacion(self):
        return self._fecha_generacion

    @property
    def secciones(self):
        return self._secciones

    @property
    def contenido(self):
        partes = [self.titulo, self.fecha_generacion.strftime('%d/%m/%Y %H:%M')]
        for seccion in self.secciones:
            partes.extend(['', seccion.titulo, ' | '.join(seccion.encabezados)])
            partes.extend(' | '.join(str(v) for v in fila) for fila in seccion.filas)
        return '\n'.join(partes)

    @classmethod
    def generar(cls, titulo, secciones):
        return cls(titulo, secciones)

    def exportar(self, exportador):
        return exportador.exportar(self)
