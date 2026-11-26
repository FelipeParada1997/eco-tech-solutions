
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
        QMessageBox.information(self,
                                "Open-Meteo",
                                "logica consulta"
        )

    def convertir_pago(self):
        QMessageBox.information(self,
                                "FrankFurter",
                                "Logica conversion")
        


