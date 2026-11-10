from .comun import PantallaTabla, combo, fecha_control, poner
from ecotech.entities import TipoEmpleado


class VentanaEmpleados(PantallaTabla):
    def __init__(self, servicio):
        super().__init__(servicio, 'Empleados' if servicio.es_admin else 'Mi ficha de empleado',
                         ['ID', 'Nombre', 'Dirección', 'Teléfono', 'Correo', 'Contrato', 'Salario', 'Cargo', 'Departamento'])
        for nombre, etiqueta in [('nombre', 'Nombre'), ('direccion', 'Dirección'),
                                 ('telefono', 'Teléfono'), ('correo_electronico', 'Correo')]:
            self.campo(nombre, etiqueta)
        self.campo('fecha_inicio_contrato', 'Inicio contrato', fecha_control())
        self.campo('salario', 'Salario (0 o mayor)')
        self.campo('tipo_empleado', 'Cargo laboral', combo([(t.value, t.value) for t in TipoEmpleado]))
        self.campo('id_departamento', 'Departamento', combo([]))
        self.formulario.setVisible(servicio.es_admin)
        self.boton('Nuevo / limpiar', self.nuevo, True)
        self.boton('Guardar nuevo o cambios', self.guardar, True)
        self.boton('Reasignar departamento', self.reasignar, True)
        self.ejecutar(self.actualizar)

    def actualizar(self):
        departamentos = self.servicio.listar_departamentos()
        control = self.campos['id_departamento']
        control.clear()
        for d in departamentos:
            control.addItem(f'{d.id_departamento} - {d.nombre}', d.id_departamento)
        empleados = self.servicio.listar_empleados(self.buscar.text())
        self.pintar(empleados, [(e.id_empleado, e.nombre, e.direccion, e.telefono, e.correo_electronico,
                                e.fecha_inicio_contrato, e.salario, e.tipo_empleado.value, e.id_departamento)
                               for e in empleados])
        self.campos['tipo_empleado'].setEnabled(True)

    def rellenar(self):
        empleado = self.seleccionado
        poner(self.campos['nombre'], empleado.nombre)
        poner(self.campos['direccion'], empleado.direccion)
        poner(self.campos['telefono'], empleado.telefono)
        poner(self.campos['correo_electronico'], empleado.correo_electronico)
        poner(self.campos['fecha_inicio_contrato'], empleado.fecha_inicio_contrato)
        poner(self.campos['salario'], empleado.salario)
        poner(self.campos['tipo_empleado'], empleado.tipo_empleado)
        poner(self.campos['id_departamento'], empleado.id_departamento)
        self.campos['tipo_empleado'].setEnabled(False)

    def nuevo(self):
        super().nuevo()
        self.campos['tipo_empleado'].setEnabled(True)

    def guardar(self):
        id_empleado = self.seleccionado.id_empleado if self.seleccionado else None
        self.servicio.guardar_empleado(self.datos(), id_empleado)
        self.terminado()

    def reasignar(self):
        if self.seleccionado is None:
            raise ValueError('Seleccione el empleado y luego el nuevo departamento.')
        departamento = self.campos['id_departamento'].currentData()
        self.servicio.reasignar_departamento(self.seleccionado.id_empleado, departamento)
        self.terminado()
