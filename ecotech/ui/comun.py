"""Controles compartidos: una tabla y un formulario para ambos roles."""
from datetime import date, datetime
from enum import Enum
from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel,
                             QLineEdit, QComboBox, QDateEdit, QPushButton, QTableWidget,
                             QTableWidgetItem, QMessageBox, QInputDialog)


def combo(opciones):
    control = QComboBox()
    for etiqueta, valor in opciones:
        control.addItem(str(etiqueta), valor)
    return control


def fecha_control():
    control = QDateEdit(QDate.currentDate())
    control.setCalendarPopup(True)
    control.setDisplayFormat('dd/MM/yyyy')
    return control


def valor(control):
    if isinstance(control, QComboBox):
        if control.currentIndex() < 0:
            raise ValueError('Faltan opciones. Registre los datos necesarios y pulse Actualizar.')
        return control.currentData()
    if isinstance(control, QDateEdit):
        return control.date().toPyDate()
    return control.text().strip()


def poner(control, dato):
    if isinstance(control, QComboBox):
        control.setCurrentIndex(control.findData(dato.value if isinstance(dato, Enum) else dato))
    elif isinstance(control, QDateEdit):
        control.setDate(QDate(dato.year, dato.month, dato.day))
    else:
        control.setText(str(dato))


class PantallaTabla(QWidget):
    def __init__(self, servicio, titulo, encabezados):
        super().__init__()
        self.servicio = servicio
        self.seleccionado = None
        self.objetos = []
        self.campos = {}
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(QLabel(titulo))
        self.buscar = QLineEdit()
        self.buscar.setPlaceholderText('Buscar por ID o nombre')
        self.layout.addWidget(self.buscar)
        self.buscar.returnPressed.connect(lambda: self.ejecutar(self.actualizar))
        self.tabla = QTableWidget(0, len(encabezados))
        self.tabla.setHorizontalHeaderLabels(encabezados)
        self.tabla.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla.itemSelectionChanged.connect(self.cargar_seleccion)
        self.layout.addWidget(self.tabla)
        self.formulario = QWidget()
        self.form = QFormLayout(self.formulario)
        self.layout.addWidget(self.formulario)
        self.botones = QHBoxLayout()
        self.layout.addLayout(self.botones)
        self.boton('Actualizar', self.actualizar)

    def campo(self, nombre, etiqueta, control=None):
        control = control if control is not None else QLineEdit()
        self.campos[nombre] = control
        self.form.addRow(etiqueta, control)
        return control

    def boton(self, etiqueta, accion, solo_admin=False):
        boton = QPushButton(etiqueta)
        boton.clicked.connect(lambda: self.ejecutar(accion))
        boton.setVisible(not solo_admin or self.servicio.es_admin)
        self.botones.addWidget(boton)
        return boton

    def ejecutar(self, accion):
        try:
            accion()
        except (ValueError, PermissionError, OSError) as error:
            QMessageBox.warning(self, 'No se pudo completar', str(error))
        except Exception:
            QMessageBox.critical(self, 'Error', 'Ocurrió un error inesperado. Revise la instalación e intente nuevamente.')

    def pintar(self, objetos, filas):
        self.tabla.blockSignals(True)
        self.tabla.clearContents()
        self.objetos = objetos
        self.tabla.setRowCount(len(filas))
        for i, fila in enumerate(filas):
            for j, dato in enumerate(fila):
                if isinstance(dato, (date, datetime)):
                    dato = dato.strftime('%d/%m/%Y')
                self.tabla.setItem(i, j, QTableWidgetItem(str(dato)))
        self.tabla.resizeColumnsToContents()
        self.tabla.clearSelection()
        self.tabla.setCurrentCell(-1, -1)
        self.tabla.blockSignals(False)
        self.nuevo()

    def cargar_seleccion(self):
        fila = self.tabla.currentRow()
        if 0 <= fila < len(self.objetos):
            self.seleccionado = self.objetos[fila]
            self.rellenar()

    def rellenar(self):
        pass

    def nuevo(self):
        self.seleccionado = None
        self.tabla.clearSelection()
        self.tabla.setCurrentCell(-1, -1)
        for control in self.campos.values():
            if isinstance(control, QLineEdit):
                control.clear()
            elif isinstance(control, QComboBox):
                control.setCurrentIndex(0)
            elif isinstance(control, QDateEdit):
                control.setDate(QDate.currentDate())

    def datos(self):
        return {nombre: valor(control) for nombre, control in self.campos.items()}

    def pedir_texto(self,titulo,mensaje):
        return QInputDialog.getText(self, titulo, mensaje)

    def confirmar(self):
        if self.seleccionado is None:
            raise ValueError('Seleccione una fila de la tabla.')
        return QMessageBox.question(self, 'Confirmar eliminación',
                                    '¿Eliminar el registro seleccionado? Se respetarán sus referencias.',
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes

    def terminado(self):
        self.nuevo()
        self.actualizar()
        QMessageBox.information(self, 'EcoTech', 'Operación completada.')
