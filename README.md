# EcoTech Solutions v1.1 — POO con Oracle

Aplicación de escritorio Python/PyQt6 con dos roles. Ambos usan las mismas clases
de pantalla; el administrador tiene más datos y acciones disponibles. El servicio
comprueba los permisos antes de consultar o escribir en Oracle.

## Qué puede hacer cada rol

| Pantalla | Administrador | Empleado |
|---|---|---|
| Empleados / Mi ficha | Registrar, buscar, editar y reasignar departamento | Consultar solo su ficha |
| Departamentos | Crear, buscar, editar y eliminar si está vacío | Consultar nombres e ID de gerente |
| Proyectos | Crear, buscar, editar y eliminar si no tiene asignaciones | Consultar sus proyectos actuales y anteriores |
| Asignaciones | Asignar, desasignar y reactivar | Consultar sus asignaciones |
| Horas | Consultar todas; registrar y corregir las propias | Consultar, registrar y corregir las propias |
| Cuentas | Crear una cuenta por empleado, con rol ADMIN o EMPLEADO | Sin acceso |
| Informes | Generar informe y exportar PDF/Excel | Sin acceso |

El cargo laboral no concede permisos. El cargo RECURSOS_HUMANOS se representa
con la clase Administrador, pero necesita además una cuenta con rol ADMIN.
Las horas toman al autor de la cuenta que inició sesión. No se puede elegir otro.

## Instalación en cuatro pasos

Se necesita Python 3.12 o superior, escritorio gráfico y Oracle 12c o superior
accesible mediante una PDB. Se verificó con Python 3.14.4.

**1. Preparar una cuenta Oracle para el proyecto.** Usa una cuenta/esquema vacío
con CREATE SESSION, CREATE TABLE, CREATE SEQUENCE y cuota. Puede proporcionarla
el docente o el administrador de Oracle. El programa no crea usuarios del servidor.
Las cuentas ADMIN/EMPLEADO se crean dentro de la aplicación y son independientes.

**2. Configurar `.env`.** Copia `.env.example` como `.env` y completa tus datos:

```dotenv
ORACLE_USER=tu_cuenta
ORACLE_PASSWORD=tu_contrasena
ORACLE_DSN=localhost:1521/XEPDB1
```

El DSN es host:puerto/servicio. No incluyas `.env` en la entrega. Consulta
[la guía Oracle](docs/INSTALACION_ORACLE.md) si falta la cuenta del servidor.

**3. Instalar dependencias.** Desde esta carpeta:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

En Windows usa `py -m venv .venv` y `.venv\Scripts\python.exe` en lugar de
`.venv/bin/python` en los comandos siguientes.

**4. Instalar tablas y entrar.**

```bash
.venv/bin/python -m ecotech.scripts.instalar
.venv/bin/python -m ecotech
```

El instalador lee la conexión del `.env` y pide el usuario y contraseña del
administrador inicial de EcoTech. No modifica el archivo de configuración.
La contraseña debe tener de 12 a 128 caracteres e incluir letras y números.
No existen contraseñas predeterminadas.

La carga inicial crea un departamento, un gerente ficticio y un administrador
ficticio para resolver las relaciones obligatorias. Edita esos datos antes de un
uso real. El resto de empleados y cuentas se crea desde las pantallas.

**El esquema de la v1.1 original no es compatible con el cifrado y las nuevas
relaciones.** El instalador rechaza esas tablas antes del DDL. Usa un esquema
vacío; no borra, migra ni sobrescribe los datos anteriores.

Oracle confirma el DDL automáticamente. Si se interrumpe, corrige la causa y
repite con la misma cuenta. Se conservan los objetos compatibles existentes;
la carga inicial usa una transacción que se revierte si falla.

## Recorrido para la exposición

1. Entra como administrador y registra un empleado con departamento y cargo.
2. En Cuentas crea su acceso con rol EMPLEADO.
3. Crea un proyecto y asígnale ese empleado.
4. Cierra sesión y entra como empleado. Comprueba que solo ve su ficha, sus
   proyectos, asignaciones y horas; ve también el catálogo de departamentos.
5. Registra horas y selecciona la fila para corregirlas. Prueba un valor inválido:
   el formulario conserva lo escrito y muestra el error.
6. Vuelve como administrador, consulta las horas y genera PDF y Excel.
7. Demuestra CRUD creando, buscando, editando y eliminando un departamento vacío
   y un proyecto sin asignaciones.

Seleccionar una fila carga sus datos. Nuevo / limpiar inicia un registro distinto.
Actualizar vuelve a consultar Oracle y limpia el formulario. Úsalo después de
cambiar datos desde otra pestaña. Todas las pestañas permitidas se crean al entrar.

El cargo no se cambia después del alta. No se eliminan empleados porque el caso
no lo solicita. Desasignar conserva el vínculo inactivo y sus horas. Un proyecto
con asignaciones anteriores tampoco se elimina. Cada empleado necesita asignación
activa para registrar o corregir horas; el total diario no puede superar 24.

## Cómo estudiar el código

Sigue este recorrido: **pantalla → servicio → entidad/repositorio → Oracle**.

| Carpeta | Responsabilidad |
|---|---|
| entities/ | Clases de dominio, atributos, propiedades y validaciones |
| services/ | Acceso, reglas, permisos y datos iniciales |
| repositories/oracle.py | Consultas SQL y conversión de filas |
| database/ | Conexión, commit/rollback y creación del esquema |
| security/ | Hash de contraseñas y cifrado de datos personales |
| reports/ | Informe, contrato abstracto y exportadores PDF/Excel |
| ui/ | Pantallas; comun.py comparte tabla, formulario y mensajes |
| scripts/ | Instalación y recuperación local |

Comienza por [el recorrido explicado](docs/RECORRIDO_PARA_ESTUDIAR.md).
Después consulta [los 20 criterios y defensa](docs/RUBRICA_Y_DEFENSA.md),
[el UML implementado](docs/UML_IMPLEMENTADO.md) y [el apoyo de IA](docs/USO_IA.md).

## Pruebas

```bash
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m pytest -q
```

Las pruebas configuran Qt offscreen y simulan persistencia para no tocar tu base.
La integración real se activa por separado, en Linux:

```bash
ECOTECH_TEST_ORACLE=1 .venv/bin/python -m pytest tests/test_oracle_live.py -q
```

En PowerShell usa `$env:ECOTECH_TEST_ORACLE="1"` antes del comando pytest. Esta
prueba crea seis tablas con prefijo aleatorio y las elimina al terminar. Necesita
cuota y permisos en un esquema de pruebas. No usa las tablas normales del programa.
Consulta [los resultados y límites](docs/VERIFICACION.md).

## Datos y alcance

La primera instalación crea `datos/clave.key` para cifrar los datos personales
con Fernet. `ECOTECH_KEY_FILE` permite elegir otra ruta. Todos los clientes del
mismo esquema necesitan la misma clave. Respáldala junto con la base en privado;
si falta para una base con empleados se exige restaurarla, no se genera otra.
Quien pueda leer base y clave podrá descifrar los datos.

Las contraseñas usan PBKDF2 con sal individual y 600.000 iteraciones. Los campos
personales se cifran; IDs, cargo, departamento, proyectos y tareas no. PDF/Excel
contienen información legible. El sistema no declara cumplimiento legal de privacidad.

Se conserva un alcance académico: solo Oracle, dos roles fijos y consultas
síncronas. No hay API, auditoría, permisos personalizados ni sesiones distribuidas.
La interfaz puede detenerse momentáneamente mientras espera a Oracle. Para recuperar
una contraseña ADMIN, cierra todos los clientes y ejecuta
`python -m ecotech.scripts.restablecer_password` con acceso a las credenciales Oracle.

Capturas con datos ficticios: [administrador](docs/capturas/administrador.png) y
[empleado](docs/capturas/empleado.png).
