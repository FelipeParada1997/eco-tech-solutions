from ecotech.database.connection import sesion

def main():
    with sesion() as cursor:
        cursor.execute(
            """
    SELECT table_name
    FROM user_tables
    WHERE table_name IN (
        'EMPLEADO',
        'DEPARTAMENTO',
        'PROYECTO',
        'ASIGNACION',
        'TRABAJO_REALIZADO',
        'USUARIO'
    )
    ORDER BY table_name
""",
        )
        filas = cursor.fetchall()
    for fila in filas:
        print(fila[0])
if __name__ == '__main__':
    main()
