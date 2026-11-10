import sys
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import QApplication
from ecotech.ui.ventana_login import VentanaLogin


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    palette = app.palette()
    palette.setColor(QPalette.ColorRole.Window, QColor('#f4f7f4'))
    palette.setColor(QPalette.ColorRole.WindowText, QColor('#111827'))
    palette.setColor(QPalette.ColorRole.Base, QColor('#ffffff'))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor('#eef2f7'))
    palette.setColor(QPalette.ColorRole.Text, QColor('#111827'))
    palette.setColor(QPalette.ColorRole.Button, QColor('#e6ebf1'))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor('#111827'))
    palette.setColor(QPalette.ColorRole.Highlight, QColor('#217346'))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor('#ffffff'))
    app.setPalette(palette)

    ventana = VentanaLogin()
    ventana.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()

