from .comun import PantallaTabla, fecha_control, poner


class VentanaProyectos(PantallaTabla):
    def __init__(self, servicio):
        super().__init__(servicio, 'Proyectos' if servicio.es_admin else 'Mis proyectos',
                         ['ID', 'Nombre', 'Descripción', 'Fecha inicio'])
        self.campo('nombre', 'Nombre')
        self.campo('descripcion', 'Descripción')
        self.campo('fecha_inicio', 'Fecha de inicio', fecha_control())
        self.formulario.setVisible(servicio.es_admin)
        self.boton('Nuevo / limpiar', self.nuevo, True)
        self.boton('Guardar nuevo o cambios', self.guardar, True)
        self.boton('Eliminar seleccionado', self.eliminar, True)
        self.ejecutar(self.actualizar)

    def actualizar(self):
        proyectos = self.servicio.listar_proyectos(self.buscar.text())
        self.pintar(proyectos, [(p.id_proyecto, p.nombre, p.descripcion, p.fecha_inicio) for p in proyectos])

    def rellenar(self):
        proyecto = self.seleccionado
        poner(self.campos['nombre'], proyecto.nombre)
        poner(self.campos['descripcion'], proyecto.descripcion)
        poner(self.campos['fecha_inicio'], proyecto.fecha_inicio)

    def guardar(self):
        id_proyecto = self.seleccionado.id_proyecto if self.seleccionado else None
        datos = self.datos()
        self.servicio.guardar_proyecto(datos['nombre'], datos['descripcion'],
                                       datos['fecha_inicio'], id_proyecto)
        self.terminado()

    def eliminar(self):
        if self.confirmar():
            self.servicio.eliminar_proyecto(self.seleccionado.id_proyecto)
            self.terminado()
