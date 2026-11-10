from PyQt6.QtWidgets import QLineEdit
from .comun import PantallaTabla, combo


class VentanaCuentas(PantallaTabla):
    def __init__(self, servicio):
        super().__init__(servicio, 'Crear accesos para empleados existentes',
                         ['ID', 'Usuario', 'Empleado', 'Rol', 'Activo'])
        self.buscar.hide()
        self.campo('empleado_id', 'Titular', combo([]))
        self.campo('usuario', 'Usuario (letras, números y guion bajo)')
        password = self.campo('password', 'Contraseña (12 a 128 caracteres, letras y números)')
        password.setEchoMode(QLineEdit.EchoMode.Password)
        self.campo('rol', 'Rol de acceso', combo([('Empleado', 'EMPLEADO'), ('Administrador de RRHH', 'ADMIN')]))
        self.boton('Crear cuenta', self.guardar, True)
        self.ejecutar(self.actualizar)

    def actualizar(self):
        cuentas = self.servicio.listar_cuentas()
        self.pintar(cuentas, cuentas)
        titulares = {c[2] for c in cuentas}
        control = self.campos['empleado_id']
        control.clear()
        for empleado in self.servicio.listar_empleados():
            if empleado.id_empleado not in titulares:
                control.addItem(f'{empleado.id_empleado} - {empleado.nombre}', empleado.id_empleado)

    def guardar(self):
        datos = self.datos()
        self.servicio.crear_cuenta(datos['empleado_id'], datos['usuario'],
                                  datos['password'], datos['rol'])
        self.terminado()
