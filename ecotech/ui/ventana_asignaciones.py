from .comun import PantallaTabla, combo, poner


class VentanaAsignaciones(PantallaTabla):
    def __init__(self, servicio):
        super().__init__(servicio, 'Asignaciones' if servicio.es_admin else 'Mis asignaciones',
                         ['ID', 'Empleado', 'Proyecto', 'Estado'])
        self.buscar.hide()
        self.campo('empleado_id', 'Empleado', combo([]))
        self.campo('proyecto_id', 'Proyecto', combo([]))
        self.formulario.setVisible(servicio.es_admin)
        self.boton('Asignar / reactivar', self.asignar, True)
        self.boton('Desasignar seleccionado', self.desasignar, True)
        self.ejecutar(self.actualizar)

    def actualizar(self):
        empleados = {e.id_empleado: e.nombre for e in self.servicio.listar_empleados()}
        proyectos = {p.id_proyecto: p.nombre for p in self.servicio.listar_proyectos()}
        for nombre, opciones in [('empleado_id', empleados), ('proyecto_id', proyectos)]:
            control = self.campos[nombre]
            control.clear()
            for id_dato, etiqueta in opciones.items():
                control.addItem(f'{id_dato} - {etiqueta}', id_dato)
        asignaciones = self.servicio.listar_asignaciones()
        self.pintar(asignaciones, [(a.id_empleado_proyecto, empleados.get(a.id_empleado, a.id_empleado),
                                    proyectos.get(a.id_proyecto, a.id_proyecto), 'Activa' if a.activa else 'Inactiva')
                                   for a in asignaciones])

    def rellenar(self):
        poner(self.campos['empleado_id'], self.seleccionado.id_empleado)
        poner(self.campos['proyecto_id'], self.seleccionado.id_proyecto)

    def asignar(self):
        datos = self.datos()
        self.servicio.asignar_proyecto(datos['empleado_id'], datos['proyecto_id'])
        self.terminado()

    def desasignar(self):
        if self.seleccionado is None:
            raise ValueError('Seleccione una asignación.')
        self.servicio.asignar_proyecto(self.seleccionado.id_empleado, self.seleccionado.id_proyecto, False)
        self.terminado()
