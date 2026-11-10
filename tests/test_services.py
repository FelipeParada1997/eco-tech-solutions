from datetime import date
import pytest
from ecotech.entities import Proyecto, TrabajoRealizado
from tests.test_domain import datos_empleado
from tests.support import PASSWORD


def test_employee_reads_only_own_data(entorno):
    repo, admin, empleado = entorno
    assert [e.id_empleado for e in empleado.listar_empleados()] == [2]
    assert len(admin.listar_empleados()) == 3
    assert [a.id_empleado for a in empleado.listar_asignaciones()] == [2]
    repo.proyectos[2] = Proyecto('Privado', 'No asignado', date(2026, 1, 1), 2)
    assert [p.id_proyecto for p in empleado.listar_proyectos()] == [1]
    assert len(admin.listar_proyectos()) == 2


@pytest.mark.parametrize('operacion', [
    lambda s: s.guardar_empleado(datos_empleado()),
    lambda s: s.guardar_departamento('Otra', 3),
    lambda s: s.eliminar_departamento(1),
    lambda s: s.reasignar_departamento(2, 1),
    lambda s: s.guardar_proyecto('Otro', 'Paneles', '01/01/2026'),
    lambda s: s.eliminar_proyecto(1),
    lambda s: s.asignar_proyecto(2, 1),
    lambda s: s.crear_cuenta(3, 'gerente', PASSWORD, 'EMPLEADO'),
    lambda s: s.listar_cuentas(),
    lambda s: s.generar_informe(),
])
def test_employee_cannot_bypass_buttons(entorno, operacion):
    repo, _, empleado = entorno
    antes = repo.transacciones
    with pytest.raises(PermissionError):
        operacion(empleado)
    assert repo.transacciones == antes


def test_logout_rejects_previously_open_screens(entorno):
    repo, _, empleado = entorno
    empleado.cerrar_sesion()
    antes = repo.transacciones
    with pytest.raises(PermissionError):
        empleado.listar_horas()
    with pytest.raises(PermissionError):
        empleado.guardar_horas(1, '02/01/2026', 2, 'Tarea')
    assert repo.transacciones == antes


def test_department_project_crud_and_references(entorno):
    repo, admin, _ = entorno
    id_depto = admin.guardar_departamento('Ventas', 3)
    admin.guardar_departamento('Ventas nuevas', 3, id_depto)
    assert admin.listar_departamentos('nuevas')[0].nombre == 'Ventas nuevas'
    admin.reasignar_departamento(2, id_depto)
    with pytest.raises(ValueError, match='Reasigne'):
        admin.eliminar_departamento(id_depto)
    admin.reasignar_departamento(2, 1)
    admin.eliminar_departamento(id_depto)
    assert id_depto not in repo.departamentos
    id_proyecto = admin.guardar_proyecto('Eólico', 'Turbinas', '01/01/2026')
    admin.guardar_proyecto('Eólico nuevo', 'Pruebas', '02/01/2026', id_proyecto)
    assert admin.listar_proyectos('nuevo')[0].descripcion == 'Pruebas'
    admin.eliminar_proyecto(id_proyecto)
    with pytest.raises(ValueError, match='trazabilidad'):
        admin.eliminar_proyecto(1)


def test_new_employee_duplicate_email_and_account(entorno):
    repo, admin, _ = entorno
    id_empleado = admin.guardar_empleado(datos_empleado(correo_electronico='nueva@example.test'))
    admin.crear_cuenta(id_empleado, 'nuevo', PASSWORD, 'EMPLEADO')
    assert repo.cuentas['nuevo'].id_titular == id_empleado
    with pytest.raises(ValueError, match='correo'):
        admin.guardar_empleado(datos_empleado(nombre='Otra', correo_electronico='nueva@example.test'))
    with pytest.raises(ValueError, match='Recursos Humanos'):
        admin.crear_cuenta(3, 'gerente', PASSWORD, 'ADMIN')


def test_assignment_reactivation_preserves_hours_and_id(entorno):
    repo, admin, empleado = entorno
    id_horas = empleado.guardar_horas(1, '02/01/2026', 2, 'Tarea')
    admin.asignar_proyecto(2, 1, False)
    assert not repo.asignaciones[1].activa and id_horas in repo.horas
    with pytest.raises(ValueError, match='activa'):
        empleado.guardar_horas(1, '03/01/2026', 2, 'Tarea')
    admin.asignar_proyecto(2, 1)
    assert len(repo.asignaciones) == 1 and repo.asignaciones[1].activa


def test_hours_identity_limits_and_correction(entorno):
    repo, admin, empleado = entorno
    id_horas = empleado.guardar_horas(1, '02/01/2026', 20, 'Desarrollo')
    assert repo.horas[id_horas].id_empleado == 2
    with pytest.raises(ValueError, match='24'):
        empleado.guardar_horas(1, '02/01/2026', 5, 'Exceso')
    empleado.guardar_horas(1, '02/01/2026', 4, 'Corrección', id_horas)
    empleado.guardar_horas(1, '02/01/2026', 20, 'Otra tarea')
    assert sum(t.horas_trabajadas for t in repo.horas.values()) == 24
    with pytest.raises(ValueError, match='contrato'):
        empleado.guardar_horas(1, '31/12/2025', 1, 'Antes')
    assert len(admin.listar_horas()) == 2
    with pytest.raises(ValueError, match='activa'):
        admin.guardar_horas(1, '02/01/2026', 1, 'Sin asignación')


def test_employee_cannot_correct_anothers_hours(entorno):
    repo, admin, empleado = entorno
    repo.horas[10] = TrabajoRealizado(1, 1, '02/01/2026', 1, 'Privado', 10)
    assert empleado.listar_horas() == []
    with pytest.raises(PermissionError):
        empleado.guardar_horas(1, '02/01/2026', 2, 'Suplantar', 10)
    assert repo.horas[10].id_empleado == 1


def test_report_contains_four_areas_and_requires_admin(entorno):
    _, admin, empleado = entorno
    empleado.guardar_horas(1, '02/01/2026', 2, 'Desarrollo')
    informe = admin.generar_informe()
    assert [s.titulo for s in informe.secciones] == ['Empleados', 'Departamentos', 'Proyectos', 'Horas']
    assert 'Pedro' in informe.contenido and 'Desarrollo' in informe.contenido
