from io import BytesIO
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from .informe import ExportadorInforme


class ExportadorPDF(ExportadorInforme):
    def exportar(self, informe):
        salida = BytesIO()
        documento = SimpleDocTemplate(salida, pagesize=landscape(A4),
                                      leftMargin=24, rightMargin=24, topMargin=24, bottomMargin=24)
        estilos = getSampleStyleSheet()
        estilos['BodyText'].fontSize = 8
        contenido = [Paragraph(escape(informe.titulo), estilos['Title']),
                     Paragraph(informe.fecha_generacion.strftime('%d/%m/%Y %H:%M'), estilos['Normal'])]
        for seccion in informe.secciones:
            contenido.extend([Spacer(1, 12), Paragraph(escape(seccion.titulo), estilos['Heading2'])])
            datos = [list(seccion.encabezados)] + [
                [Paragraph(escape(str(valor)), estilos['BodyText']) for valor in fila]
                for fila in seccion.filas]
            tabla = Table(datos, colWidths=[documento.width / len(seccion.encabezados)] * len(seccion.encabezados), repeatRows=1)
            tabla.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#217346')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), .3, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            contenido.append(tabla)
        documento.build(contenido)
        return salida.getvalue()
