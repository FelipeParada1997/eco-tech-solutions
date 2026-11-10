from ecotech.ui.ventana_principal import VentanaPrincipal
from ecotech.ui.ventana_login import VentanaLogin
from ecotech.ui.ventana_empleados import VentanaEmpleados
from ecotech.ui.ventana_proyectos import VentanaProyectos
from ecotech.ui.ventana_departamentos import VentanaDepartamentos
from ecotech.ui.ventana_asignaciones import VentanaAsignaciones
from ecotech.ui.ventana_horas import VentanaHoras
from ecotech.ui.comun import poner
from tests.support import PASSWORD


def test_same_screen_classes_different_permissions(qapp, messages, entorno):
    _, admin, empleado = entorno
    administrador = VentanaPrincipal(admin)
    trabajador = VentanaPrincipal(empleado)
    assert administrador.pestanas.count() == 7
    assert trabajador.pestanas.count() == 5
    assert isinstance(administrador.pestanas.widget(0), VentanaEmpleados)
    assert isinstance(trabajador.pestanas.widget(0), VentanaEmpleados)
    assert not administrador.pestanas.widget(0).formulario.isHidden()
    assert trabajador.pestanas.widget(0).formulario.isHidden()
    assert trabajador.pestanas.widget(0).tabla.rowCount() == 1
    # Todas las pantallas se construyen directamente, sin gestores de carga diferida.
    for ventana in (administrador, trabajador):
        for indice in range(ventana.pestanas.count()):
            ventana.pestanas.setCurrentIndex(indice)
            assert ventana.pestanas.widget(indice).servicio is ventana.servicio
    assert not messages
    administrador.close()
    trabajador.close()


def test_project_and_department_ui_crud(qapp, messages, entorno):
    repo, admin, _ = entorno
    ventana = VentanaProyectos(admin)
    poner(ventana.campos['nombre'], 'Eólico')
    poner(ventana.campos['descripcion'], 'Turbinas')
    ventana.guardar()
    assert len(repo.proyectos) == 2
    ventana.tabla.selectRow(1)
    assert ventana.seleccionado.nombre == 'Eólico'
    poner(ventana.campos['nombre'], 'Eólico editado')
    ventana.guardar()
    assert repo.proyectos[2].nombre == 'Eólico editado'
    ventana.tabla.selectRow(1)
    ventana.eliminar()
    assert len(repo.proyectos) == 1
    deptos = VentanaDepartamentos(admin)
    poner(deptos.campos['nombre'], 'Ventas')
    deptos.guardar()
    assert repo.departamentos[2].id_gerente == 3
    deptos.tabla.selectRow(1)
    deptos.eliminar()
    assert len(repo.departamentos) == 1
    ventana.close()
    deptos.close()


def test_employee_cannot_write_even_calling_hidden_ui_method(qapp, messages, entorno):
    repo, _, empleado = entorno
    ventana = VentanaProyectos(empleado)
    poner(ventana.campos['nombre'], 'Intento')
    poner(ventana.campos['descripcion'], 'No autorizado')
    ventana.ejecutar(ventana.guardar)
    assert len(repo.proyectos) == 1
    assert 'administrador' in messages[-1][2]
    ventana.close()


def test_assignment_and_hours_forms(qapp, messages, entorno):
    repo, admin, empleado = entorno
    asignaciones = VentanaAsignaciones(admin)
    asignaciones.tabla.selectRow(0)
    asignaciones.desasignar()
    assert not repo.asignaciones[1].activa
    # La lista de empleados empieza por administrador; elegir al empleado 2.
    poner(asignaciones.campos['empleado_id'], 2)
    asignaciones.asignar()
    assert repo.asignaciones[1].activa
    horas = VentanaHoras(empleado)
    poner(horas.campos['fecha'], __import__('datetime').date(2026, 1, 2))
    poner(horas.campos['horas'], '2.5')
    poner(horas.campos['descripcion'], 'Diseño')
    horas.guardar()
    assert repo.horas[1].id_empleado == 2
    horas.tabla.selectRow(0)
    assert not horas.campos['proyecto_id'].isEnabled()
    poner(horas.campos['horas'], '3')
    horas.guardar()
    assert repo.horas[1].horas_trabajadas == 3
    horas.close()
    asignaciones.close()


def test_invalid_form_retains_input_and_logout_clears_session(qapp, messages, entorno):
    _, admin, _ = entorno
    ventana = VentanaProyectos(admin)
    poner(ventana.campos['nombre'], 'Sin descripción')
    ventana.ejecutar(ventana.guardar)
    assert ventana.campos['nombre'].text() == 'Sin descripción'
    principal = VentanaPrincipal(admin)
    principal.cerrar_sesion()
    assert not admin.cuenta.sesion_activa
    assert isinstance(principal.ventana_login, VentanaLogin)
    principal.ventana_login.close()
    principal.close()
    ventana.close()


def test_login_routes_authenticated_account_and_clears_password(qapp, messages, entorno):
    repo, _, _ = entorno
    ventana = VentanaLogin(repo)
    ventana.usuario.setText('pedro')
    ventana.contrasena.setText('equivocada')
    ventana.iniciar_sesion()
    assert ventana.ventana_principal is None
    ventana.contrasena.setText(PASSWORD)
    ventana.iniciar_sesion()
    assert ventana.ventana_principal.servicio.cuenta.rol == 'EMPLEADO'
    assert ventana.contrasena.text() == ''
    ventana.ventana_principal.close()
    ventana.close()


def test_refresh_clears_edit_selection_and_old_values(qapp, messages, entorno):
    _, admin, _ = entorno
    ventana = VentanaProyectos(admin)
    ventana.tabla.selectRow(0)
    assert ventana.campos['nombre'].text() == 'Solar'
    ventana.actualizar()
    assert ventana.seleccionado is None
    assert ventana.campos['nombre'].text() == ''
    ventana.close()
