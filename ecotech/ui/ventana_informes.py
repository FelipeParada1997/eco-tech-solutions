from pathlib import Path
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton, QFileDialog, QMessageBox
from ecotech.reports.pdf import ExportadorPDF
from ecotech.reports.excel import ExportadorExcel


class VentanaInformes(QWidget):
    def __init__(self, servicio):
        super().__init__()
        self.servicio = servicio
        self.informe = None
        layout = QVBoxLayout(self)
        self.vista = QTextEdit()
        self.vista.setReadOnly(True)
        layout.addWidget(self.vista)
        for texto, accion in [('Generar / actualizar informe', self.generar),
                              ('Exportar PDF', lambda: self.exportar(ExportadorPDF(), 'pdf')),
                              ('Exportar Excel', lambda: self.exportar(ExportadorExcel(), 'xlsx'))]:
            boton = QPushButton(texto)
            boton.clicked.connect(lambda checked=False, fn=accion: self.ejecutar(fn))
            layout.addWidget(boton)

    def ejecutar(self, accion):
        try:
            accion()
        except (ValueError, PermissionError, OSError) as error:
            QMessageBox.warning(self, 'Informe', str(error))
        except Exception:
            QMessageBox.critical(self, 'Informe', 'No se pudo generar o guardar el documento.')

    def generar(self):
        self.informe = self.servicio.generar_informe()
        self.vista.setPlainText(self.informe.contenido)

    def exportar(self, exportador, extension):
        self.servicio.autorizar('informes', escritura=True)
        if self.informe is None:
            raise ValueError('Genere el informe antes de exportar.')
        ruta, _ = QFileDialog.getSaveFileName(self, 'Guardar informe', f'Informe.{extension}', f'Documento (*.{extension})')
        if not ruta:
            return
        if not ruta.lower().endswith('.' + extension):
            ruta += '.' + extension
        # Generar antes de abrir el destino: un fallo de exportación no trunca un archivo previo.
        contenido = self.informe.exportar(exportador)
        Path(ruta).write_bytes(contenido)
        QMessageBox.information(self, 'Informe', 'Documento guardado.')
