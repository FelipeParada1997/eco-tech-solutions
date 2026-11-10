from .comun import PantallaTabla, combo, fecha_control, poner


class VentanaHoras(PantallaTabla):
    def __init__(self, servicio):
        super().__init__(servicio, 'Horas de todos / registro de mis horas' if servicio.es_admin else 'Mis horas',
                         ['ID', 'Empleado', 'Proyecto', 'Fecha', 'Horas', 'Descripción'])
        self.buscar.hide()
        self.campo('proyecto_id', 'Mi proyecto asignado', combo([]))
        self.campo('fecha', 'Fecha', fecha_control())
        self.campo('horas', 'Horas (máximo dos decimales)')
        self.campo('descripcion', 'Descripción de tareas')
        self.boton('Nuevo / limpiar', self.nuevo)
        self.boton_guardar = self.boton('Guardar mis horas / corregir selección propia', self.guardar)
        self.ejecutar(self.actualizar)

    def actualizar(self):
        proyectos = {p.id_proyecto: p.nombre for p in self.servicio.listar_proyectos()}
        ids = {a.id_proyecto for a in self.servicio.listar_asignaciones()
               if a.id_empleado == self.servicio.cuenta.id_titular and a.activa}
        control = self.campos['proyecto_id']
        control.clear()
        for id_proyecto in sorted(ids):
            control.addItem(f'{id_proyecto} - {proyectos.get(id_proyecto, id_proyecto)}', id_proyecto)
        trabajos = self.servicio.listar_horas()
        self.pintar(trabajos, [(t.id_trabajo, t.id_empleado, proyectos.get(t.id_proyecto, t.id_proyecto),
                               t.fecha, t.horas_trabajadas, t.descripcion_tareas_realizadas) for t in trabajos])
        self.boton_guardar.setEnabled(True)
        control.setEnabled(True)

    def rellenar(self):
        t = self.seleccionado
        propio = t.id_empleado == self.servicio.cuenta.id_titular
        poner(self.campos['proyecto_id'], t.id_proyecto)
        poner(self.campos['fecha'], t.fecha)
        poner(self.campos['horas'], t.horas_trabajadas)
        poner(self.campos['descripcion'], t.descripcion_tareas_realizadas)
        self.campos['proyecto_id'].setEnabled(False)
        self.boton_guardar.setEnabled(propio)

    def nuevo(self):
        super().nuevo()
        self.campos['proyecto_id'].setEnabled(True)
        self.boton_guardar.setEnabled(True)

    def guardar(self):
        id_trabajo = self.seleccionado.id_trabajo if self.seleccionado else None
        datos = self.datos()
        self.servicio.guardar_horas(datos['proyecto_id'], datos['fecha'], datos['horas'],
                                   datos['descripcion'], id_trabajo)
        self.terminado()
