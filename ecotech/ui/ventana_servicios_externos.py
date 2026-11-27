
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox)

class VentanaServiciosExternos(QWidget):

    def __init__(self, servicio):

        super().__init__()
        #Contiene la cuenta del usuario que inicio sesion
        self.servicio = servicio

        layout = QVBoxLayout(self)
        titulo = QLabel("Servicios Externos - EcoTech")
        self.boton_clima = QPushButton("Consultar clima del proyecto")
        self.boton_conversion = QPushButton("Calcular conversion de pago")

        self.boton_clima.clicked.connect(self.consultar_clima)
        self.boton_conversion.clicked.connect(self.convertir_pago)

        layout.addWidget(titulo)
        layout.addWidget(self.boton_clima)
        layout.addWidget(self.boton_conversion)

        layout.addStretch()

    def consultar_clima(self):

        try:
            self.servicio.autorizar("servicios_externos")

        except PermissionError:

            QMessageBox.warning(self,
                                "Acceso denegado",
                                "La sesion termino o no tiene permiso para este servicio")
            return

        QMessageBox.information(self,
        "Open-Meteo",
        "Acceso autorizado. Logica del clima.")

    def convertir_pago(self):

        try:
            self.servicio.autorizar("servicios_externos")

        except PermissionError:
            QMessageBox.warning(self,
                                "Acceso denegado",
                                "La sesion termino o no tiene permiso para este servicio")
            return
        
        QMessageBox.information(self,
                                "FrankFurter",
                                "Acceso Autorizado. Logica conversion")
        


