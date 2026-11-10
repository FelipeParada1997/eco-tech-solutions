from io import BytesIO
from datetime import date
from decimal import Decimal
from openpyxl import load_workbook
import pytest
from ecotech.reports import Informe, Seccion, ExportadorInforme, ExportadorPDF, ExportadorExcel


def test_real_pdf_excel_polymorphism_and_formula_protection():
    informe = Informe.generar('=Informe <EcoTech>', [Seccion('Empleados', ('Nombre', 'Fecha', 'Salario'),
        [('=1+1', date(2026, 1, 1), Decimal('1000.50')), ('<b>Ana</b>', date(2026, 1, 2), 0)])])
    with pytest.raises(TypeError):
        ExportadorInforme()
    pdf = informe.exportar(ExportadorPDF())
    assert pdf.startswith(b'%PDF-') and len(pdf) > 1000
    libro = load_workbook(BytesIO(informe.exportar(ExportadorExcel())))
    hoja = libro['Empleados']
    assert hoja['A1'].data_type == 's'
    assert hoja['A4'].value == '=1+1' and hoja['A4'].data_type == 's'
    assert hoja['C4'].value == 1000.5 and hoja['C4'].data_type == 'n'
    assert hoja['B4'].value.year == 2026
    assert hoja.freeze_panes == 'A4' and hoja.auto_filter.ref == 'A3:C5'
    libro.close()


def test_report_window_generates_and_exports(qapp, messages, entorno, monkeypatch, tmp_path):
    from PyQt6.QtWidgets import QFileDialog
    from ecotech.ui.ventana_informes import VentanaInformes
    _, admin, _ = entorno
    ventana = VentanaInformes(admin)
    ventana.generar()
    assert 'Empleados' in ventana.vista.toPlainText()
    for exportador, extension in [(ExportadorPDF(), 'pdf'), (ExportadorExcel(), 'xlsx')]:
        destino = tmp_path / ('informe.' + extension)
        monkeypatch.setattr(QFileDialog, 'getSaveFileName', lambda *a: (str(destino), ''))
        ventana.exportar(exportador, extension)
        assert destino.stat().st_size > 1000
    ventana.close()
