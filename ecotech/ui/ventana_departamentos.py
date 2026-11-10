from .comun import PantallaTabla, combo, poner
from ecotech.entities import TipoEmpleado


class VentanaDepartamentos(PantallaTabla):
    def __init__(self, servicio):
        super().__init__(servicio, 'Departamentos', ['ID', 'Nombre', 'ID gerente'])
        self.campo('nombre', 'Nombre')
        self.campo('gerente', 'Gerente', combo([]))
        self.formulario.setVisible(servicio.es_admin)
        self.boton('Nuevo / limpiar', self.nuevo, True)
        self.boton('Guardar nuevo o cambios', self.guardar, True)
        self.boton('Eliminar seleccionado', self.eliminar, True)
        self.ejecutar(self.actualizar)

    def actualizar(self):
        if self.servicio.es_admin:
            control = self.campos['gerente']
            control.clear()
            for e in self.servicio.listar_empleados():
                if e.tipo_empleado == TipoEmpleado.GERENTE:
                    control.addItem(f'{e.id_empleado} - {e.nombre}', e.id_empleado)
        departamentos = self.servicio.listar_departamentos(self.buscar.text())
        self.pintar(departamentos, [(d.id_departamento, d.nombre, d.id_gerente) for d in departamentos])

    def rellenar(self):
        poner(self.campos['nombre'], self.seleccionado.nombre)
        poner(self.campos['gerente'], self.seleccionado.id_gerente)

    def guardar(self):
        datos = self.datos()
        id_depto = self.seleccionado.id_departamento if self.seleccionado else None
        self.servicio.guardar_departamento(datos['nombre'], datos['gerente'], id_depto)
        self.terminado()

    def eliminar(self):
        if self.confirmar():
            self.servicio.eliminar_departamento(self.seleccionado.id_departamento)
            self.terminado()
