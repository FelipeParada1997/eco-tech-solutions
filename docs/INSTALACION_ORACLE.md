# Oracle: configuración e instalación

El programa usa `oracledb` en modo Thin y una cuenta técnica ya existente.
No administra usuarios del servidor Oracle. Esto permite explicar el acceso con
los tres parámetros habituales: usuario, contraseña y DSN.

## Antes de ejecutar el programa

El docente o administrador debe proporcionar una cuenta dedicada en una PDB,
con CREATE SESSION, CREATE TABLE, CREATE SEQUENCE y cuota. Si debe crearla,
puede usar este ejemplo desde su herramienta de administración Oracle, sustituyendo
la contraseña del ejemplo por una privada y usando el tablespace de su entorno:

```sql
CREATE USER ECOTECH IDENTIFIED BY "REEMPLAZAR_POR_CLAVE_PRIVADA"
    DEFAULT TABLESPACE USERS QUOTA 100M ON USERS;
GRANT CREATE SESSION, CREATE TABLE, CREATE SEQUENCE TO ECOTECH;
```

Ese SQL es preparación del laboratorio, no código que ejecute la aplicación.
No usar SYS ni SYSTEM como cuenta habitual del programa. La conexión debe apuntar
a una PDB, por ejemplo XEPDB1, no al contenedor raíz.

Copia .env.example como .env y completa:

- ORACLE_USER: cuenta/esquema técnico, como ECOTECH.
- ORACLE_PASSWORD: su contraseña privada.
- ORACLE_DSN: host:puerto/servicio, como localhost:1521/XEPDB1.
- ECOTECH_KEY_FILE: ruta opcional a la clave; por defecto datos/clave.key.

Las variables del sistema tienen prioridad sobre .env. Si los valores no coinciden,
actualiza la fuente que estás utilizando. La contraseña se lee sin interpolar `$`.
El instalador lee estos valores y no los reescribe ni solicita contraseñas de SYS.

## Instalar

Desde la raíz, con las dependencias instaladas:

```bash
python -m ecotech.scripts.instalar
python -m ecotech
```

El instalador valida usuario y contraseña de EcoTech antes de crear tablas. Después
prepara las seis tablas y la cuenta inicial. Una repetición verifica la cuenta
administradora existente con su contraseña; no la reemplaza. Las cuentas adicionales
se crean desde la pantalla Cuentas del administrador.

La cuenta Oracle es técnica. Los usuarios ADMIN/EMPLEADO están en la tabla USUARIO,
se vinculan a empleados y no son nuevas cuentas del servidor.

Los comandos separados crear_tablas y crear_admin siguen disponibles para revisar
cada etapa manualmente. La ruta habitual es el único comando instalar.

## Datos existentes y recuperación

El esquema nuevo no es compatible con la v1.1 original. El instalador comprueba
columnas antes del primer DDL y rechaza tablas incompatibles. Usa un esquema vacío;
no hay migración automática ni borrado de tablas para resolver conflictos.

Oracle confirma el DDL automáticamente. Ante un fallo, pueden quedar objetos
creados. Corrige permisos/cuota y repite: los objetos compatibles se conservan.
La carga inicial es una transacción distinta: un error revierte sus registros.

La clave Fernet se crea solo para la primera carga. Si ya hay empleados y falta,
restaura el respaldo. Todos los clientes de un esquema necesitan la misma clave.
No incluyas .env ni la clave en Git o en el ZIP de entrega.

Para recuperar una contraseña ADMIN, cierra los clientes y ejecuta
`python -m ecotech.scripts.restablecer_password`. Se requiere acceso a la cuenta
Oracle configurada; no es una opción disponible para empleados en la interfaz.

Errores frecuentes: ORA-01017 credenciales, ORA-01031 permisos, ORA-01950 cuota y
DPY-6005 conexión no disponible. La aplicación muestra mensajes controlados sin SQL
ni credenciales.
