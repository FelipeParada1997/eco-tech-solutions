from io import BytesIO
from datetime import date, datetime
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from .informe import ExportadorInforme


class ExportadorExcel(ExportadorInforme):
    def exportar(self, informe):
        libro = Workbook()
        libro.remove(libro.active)
        for seccion in informe.secciones:
            hoja = libro.create_sheet(seccion.titulo[:31])
            hoja.append([informe.titulo])
            hoja.append([informe.fecha_generacion.strftime('%d/%m/%Y %H:%M')])
            hoja.append(list(seccion.encabezados))
            for celda in hoja[3]:
                celda.font = Font(bold=True, color='FFFFFF')
                celda.fill = PatternFill('solid', fgColor='217346')
            for fila in seccion.filas:
                hoja.append(list(fila))
                for celda in hoja[hoja.max_row]:
                    # Un texto ingresado por el usuario nunca se interpreta como fórmula.
                    if isinstance(celda.value, str):
                        celda.data_type = 's'
                    elif isinstance(celda.value, (date, datetime)):
                        celda.number_format = 'DD/MM/YYYY'
            # También proteger título y encabezados del contrato de Informe.
            for fila in hoja:
                for celda in fila:
                    if isinstance(celda.value, str):
                        celda.data_type = 's'
            hoja.freeze_panes = 'A4'
            hoja.auto_filter.ref = f'A3:{hoja.cell(3, len(seccion.encabezados)).column_letter}{hoja.max_row}'
            for columna in hoja.columns:
                letra = columna[0].column_letter
                hoja.column_dimensions[letra].width = min(40, max(len(str(c.value or '')) for c in columna) + 3)
        if not informe.secciones:
            libro.create_sheet('Sin datos').append([informe.titulo])
        salida = BytesIO()
        libro.save(salida)
        return salida.getvalue()
