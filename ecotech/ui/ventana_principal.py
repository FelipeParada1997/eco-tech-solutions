from PyQt6.QtWidgets import QMainWindow, QTabWidget, QMessageBox
from .ventana_empleados import VentanaEmpleados
from .ventana_departamentos import VentanaDepartamentos
from .ventana_proyectos import VentanaProyectos
from .ventana_asignaciones import VentanaAsignaciones
from .ventana_horas import VentanaHoras
from .ventana_cuentas import VentanaCuentas
from .ventana_informes import VentanaInformes


class VentanaPrincipal(QMainWindow):
    def __init__(self, servicio):
        super().__init__()
        self.servicio = servicio
        self.ventana_login = None
        self.setWindowTitle(f'EcoTech Solutions — {servicio.cuenta.nombre_usuario} — {servicio.cuenta.rol}')
        self.resize(1150, 820)
        self.setStyleSheet("""
            QMainWindow, QWidget { background-color: #f4f7f4; color: #111827; }
            QLabel, QLineEdit, QComboBox, QDateEdit, QTableWidget, QTextEdit, QTabBar, QTabWidget {
                color: #111827;
            }
            QLineEdit, QComboBox, QDateEdit, QTableWidget, QTextEdit {
                background-color: white;
            }
            QPushButton { background-color: #217346; color: white; padding: 6px; border-radius: 3px; }
            QPushButton:disabled { background-color: #84968a; }
            QHeaderView::section { background-color: #e1eee4; color: #111827; padding: 4px; }
        """)
        self.pestanas = QTabWidget()
        self.setCentralWidget(self.pestanas)
        # Ambos roles usan las mismas clases de pantalla.
        titulo_empleados = 'Empleados' if servicio.es_admin else 'Mi ficha'
        titulo_proyectos = 'Proyectos' if servicio.es_admin else 'Mis proyectos'
        self.pestanas.addTab(VentanaEmpleados(servicio), titulo_empleados)
        self.pestanas.addTab(VentanaDepartamentos(servicio), 'Departamentos')
        self.pestanas.addTab(VentanaProyectos(servicio), titulo_proyectos)
        self.pestanas.addTab(VentanaAsignaciones(servicio), 'Asignaciones')
        self.pestanas.addTab(VentanaHoras(servicio), 'Horas')
        if servicio.es_admin:
            self.pestanas.addTab(VentanaCuentas(servicio), 'Cuentas')
            self.pestanas.addTab(VentanaInformes(servicio), 'Informes')
        accion = self.menuBar().addAction('Cerrar sesión')
        accion.triggered.connect(self.cerrar_sesion)

    def cerrar_sesion(self):
        if QMessageBox.question(self, 'Cerrar sesión', '¿Desea cerrar la sesión?',
                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) != QMessageBox.StandardButton.Yes:
            return
        from .ventana_login import VentanaLogin
        self.servicio.cerrar_sesion()
        self.ventana_login = VentanaLogin(self.servicio.repository)
        self.ventana_login.show()
        self.close()

    def closeEvent(self, evento):
        self.servicio.cerrar_sesion()
        super().closeEvent(evento)
