from datetime import date
from decimal import Decimal
import pytest
from ecotech.entities import Administrador, Empleado, Departamento, Proyecto, EmpleadoProyecto, TrabajoRealizado
from ecotech import validation as v


def datos_empleado(**cambios):
    datos = dict(nombre='Ana', direccion='Calle 123', telefono='12345678',
                 correo_electronico='ana@example.test', fecha_inicio_contrato='01/01/2026',
                 salario=1000, tipo_empleado='VENDEDOR', id_departamento=1)
    datos.update(cambios)
    return datos


def test_inheritance_properties_and_relationships():
    admin = Administrador(**datos_empleado(tipo_empleado='RECURSOS_HUMANOS'), id_empleado=1)
    assert isinstance(admin, Empleado)
    empleado = admin.registrar_empleado(**datos_empleado())
    departamento = Departamento('Ventas', 1, 2)
    empleado.reasignar_departamento(departamento)
    assert empleado.id_departamento == 2
    assert empleado.validar_datos()
    with pytest.raises(AttributeError):
        empleado.id_empleado = 9
    proyecto = Proyecto('Solar', 'Paneles', date(2026, 1, 1), 3)
    trabajo = admin.registrar_trabajo(proyecto, '02/01/2026', '1.25', 'Diseño')
    assert trabajo.id_empleado == 1 and trabajo.id_proyecto == 3
    trabajo.modificar_registro('03/01/2026', '2.5', 'Pruebas')
    assert trabajo.horas_trabajadas == Decimal('2.5')
    with pytest.raises(AttributeError):
        trabajo.id_proyecto = 9
    asignacion = EmpleadoProyecto(1, 3, id_empleado_proyecto=5)
    asignacion.desasignar()
    assert not asignacion.activa
    asignacion.asignar()
    assert asignacion.activa


@pytest.mark.parametrize('cambio', [dict(salario='NaN'), dict(salario='Infinity'), dict(salario=-1),
                                  dict(salario='1.234'), dict(correo_electronico='mal@correo'),
                                  dict(telefono='abc'), dict(fecha_inicio_contrato='31/02/2026'),
                                  dict(id_departamento=0), dict(nombre=''), dict(tipo_empleado='otro')])
def test_invalid_employee(cambio):
    with pytest.raises(ValueError):
        Empleado(**datos_empleado(**cambio))


@pytest.mark.parametrize('horas', ['NaN', 'Infinity', '-1', '0', '24.01', '1.234'])
def test_invalid_hours(horas):
    with pytest.raises(ValueError):
        TrabajoRealizado(1, 1, date.today(), horas, 'Tarea')


def test_invalid_edit_leaves_object_unchanged():
    p = Proyecto('Solar', 'Paneles', date(2026, 1, 1), 1)
    with pytest.raises(ValueError):
        p.editar_proyecto('Otro nombre', '', '02/01/2026')
    assert p.nombre == 'Solar' and p.descripcion == 'Paneles'


@pytest.mark.parametrize('id_invalido', [True, False, 0, -1, '1.5', 1.5, None])
def test_invalid_ids(id_invalido):
    with pytest.raises(ValueError):
        v.identificador(id_invalido)
