# Verificación de v1.1 adaptada a la rúbrica

Fecha: 29 de octubre de 2026. Entorno: Linux, Python 3.14.4,
oracledb 4.0.2, PyQt6 6.11.0 y Qt en modo offscreen.

## Resultados ejecutados

| Comprobación | Resultado |
|---|---|
| Suite habitual completa | **101 aprobadas, 1 omitida**, 17,27 segundos |
| Integración real Oracle, activada por separado | **1 aprobada**, 3,52 segundos |
| Sintaxis de los módulos | Compilación correcta |
| Arranque aislado sin módulos antiguos | Ventana de acceso visible, sin conectar al importar |
| Pantallas con ambos roles | Revisión Qt y capturas con datos ficticios |

La omitida en la suite habitual es la integración Oracle optativa, no un fallo.
Las 69 pruebas de la versión original y las 120 de la primera adaptación son
resultados históricos, no se agregan a este resultado. La reducción de la suite
actual se debe a retirar el aprovisionamiento de usuarios del servidor Oracle y
sustituir sus pruebas por las del instalador simplificado. Se mantienen las pruebas
de dominio, permisos, CRUD, formularios, transacciones y exportaciones.

Comandos:

```bash
QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest -q -p no:cacheprovider
ECOTECH_TEST_ORACLE=1 QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest tests/test_oracle_live.py -q -p no:cacheprovider
```

## Qué se comprobó sin servidor

- Validaciones de correo, teléfono, ID, fecha, salario y horas, incluidos NaN,
  infinito y exceso de decimales.
- Herencia, propiedades sin setter, reasignación, referencias de trabajo y cambios
  de estado en EmpleadoProyecto.
- Contraseñas con sal, acceso inválido, cuenta inactiva y cierre de sesión.
- El empleado solo obtiene su ficha, sus asignaciones, proyectos y horas.
- Se rechazan llamadas administrativas directas, sin depender de botones ocultos.
- CRUD por servicios, protección de referencias, duplicados de correo y cuentas.
- Suma diaria y corrección de horas sin cambiar autor ni proyecto.
- Commit/rollback, cierre de recursos y traducción segura de errores Oracle.
- Validación del usuario inicial antes del DDL y rechazo de clave faltante para
  una base con datos. No se genera otra clave silenciosamente.
- Instalador con la cuenta Oracle configurada: configuración incompleta, credenciales
  privilegiadas rechazadas, validación antes del DDL, cancelación, esquema incompatible,
  verificación del administrador existente y errores sin exponer información privada.
  El .env no se reescribe.
- Pantallas compartidas construidas directamente, campos según rol, conservación de entradas inválidas,
  limpieza de selección al actualizar y cierre de sesión.
- PDF y Excel reales; contrato abstracto y textos que no se convierten en fórmulas.

La persistencia en memoria de tests/support.py es exclusivamente una herramienta
de pruebas. No existe backend SQLite ni modo de datos en memoria en la aplicación.

## Qué se comprobó contra Oracle real

Se usó la configuración privada del entorno para abrir conexiones. La prueba creó
las seis tablas, restricciones e índices con un prefijo aleatorio. Solo trabajó
sobre esos objetos y los eliminó al terminar. No migró, truncó ni modificó las
seis tablas normales del proyecto ni sus credenciales locales.

Recorrido ejecutado:

1. DDL real con columnas IDENTITY y claves foráneas diferidas.
2. Primera carga transaccional; segunda ejecución conserva el administrador.
3. Inicio de sesión ADMIN y EMPLEADO vinculados a empleados distintos.
4. Crear, leer, editar y eliminar departamentos/proyectos con referencias válidas.
5. Alta de empleado y cuenta; almacenamiento/lectura real de CLOB cifrado.
6. Asignar, desasignar y reactivar el mismo vínculo sin borrar horas.
7. Registrar y corregir horas Decimal enviadas numéricamente al controlador.
8. Rechazar exceso de horas, escritura del empleado y asignación inactiva.
9. Informe consistente de las cuatro áreas y generación PDF/Excel.
10. Error de FK diferida al commit: mensaje controlado ORA-02091 y rollback real,
    comprobando que la fila inválida no quedó en Oracle.
11. Cierre de sesión e imposibilidad de seguir consultando con esa cuenta local.

Durante la primera integración se corrigió el aislador de pruebas: no debía
sustituir el literal del rol 'EMPLEADO' al cambiar el nombre de la tabla EMPLEADO.
La prueba adicional de rollback permitió mejorar el mensaje ORA-02091. Ambos
casos y la intervención de IA están declarados en USO_IA.md.

## Límites de esta verificación

No se hicieron pruebas en Windows/macOS, de carga empresarial, múltiples clientes
simultáneos ni certificación de seguridad/privacidad. El test de integración usa
DDL real con nombres prefijados; no se instaló la nueva versión sobre el esquema
anterior. La comprobación de instalación repetida del DDL y esquema incompatible
se cubre adicionalmente mediante simulaciones del catálogo Oracle.

Las capturas son renderizadas en Qt offscreen con datos ficticios. No sustituyen
un ensayo interactivo del equipo en el computador que se usará en la exposición.
Los criterios orales y el análisis personal del uso de IA deben ser defendidos por
los estudiantes; no se consideran aprobados automáticamente por esta suite.

## Simplificación verificada

Se retiró services/instalacion.py y se redujo scripts/instalar.py a la lectura del
.env y la preparación de tablas/cuenta inicial. No se cambió el esquema ni los
algoritmos de seguridad en esta simplificación. Se quitaron las pestañas diferidas
y el acceso dinámico a atributos en los formularios principales.

El código Python de la aplicación pasó de 2.143 a 1.913 líneas. El número de líneas
no mide por sí solo facilidad o calidad: se comprobaron los comportamientos y se
agregó un recorrido de estudio que relaciona llamadas explícitas con la rúbrica.
