from PyQt6.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from ecotech.services.autenticacion import AutenticacionService
from ecotech.services.gestion import GestionService
from .ventana_principal import VentanaPrincipal


class VentanaLogin(QWidget):
    def __init__(self, repository=None):
        super().__init__()
        self.auth_service = AutenticacionService(repository)
        self.ventana_principal = None
        self.setWindowTitle('EcoTech Solutions - Iniciar sesión')
        self.resize(430, 260)
        self.setStyleSheet("""
            QWidget { background-color: #f4f7f4; color: #111827; }
            QLabel, QLineEdit, QComboBox, QDateEdit { color: #111827; }
            QLineEdit, QComboBox, QDateEdit { background-color: white; }
            QPushButton { background-color: #217346; color: white; padding: 6px; border-radius: 3px; }
        """)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel('ECOTECH SOLUTIONS'))
        layout.addWidget(QLabel('Ingrese su cuenta de administrador o empleado.'))
        form = QFormLayout()
        self.usuario = QLineEdit()
        self.contrasena = QLineEdit()
        self.contrasena.setEchoMode(QLineEdit.EchoMode.Password)
        form.addRow('Usuario', self.usuario)
        form.addRow('Contraseña', self.contrasena)
        layout.addLayout(form)
        boton = QPushButton('Ingresar')
        boton.clicked.connect(self.iniciar_sesion)
        self.contrasena.returnPressed.connect(self.iniciar_sesion)
        layout.addWidget(boton)

    def iniciar_sesion(self):
        try:
            cuenta = self.auth_service.autenticar(self.usuario.text(), self.contrasena.text())
            if cuenta is None:
                QMessageBox.warning(self, 'Acceso denegado', 'Usuario o contraseña incorrectos, o cuenta inactiva.')
                return
            # Crear el servicio de gestión con la cuenta autenticada
            servicio = GestionService(cuenta, self.auth_service.repository)
            self.ventana_principal = VentanaPrincipal(servicio)
            self.ventana_principal.show()
            self.contrasena.clear()
            self.close()
        except (ValueError, PermissionError, OSError) as error:
            QMessageBox.warning(self, 'Acceso', str(error))
        except Exception:
            QMessageBox.critical(self, 'Acceso', 'No fue posible iniciar la aplicación. Revise la instalación.')
