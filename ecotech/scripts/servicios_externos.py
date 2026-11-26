def consultar_clima():
    print("consultar clima")

def convertir_pago():
    print("convertir pago")

def main():

    while True:

        print("EcoTech - Servicios Externos")
        print("1. Consultar clima de un proyecto")
        print("2. Calcular una conversion de pago")

        opt = input("Seleccione una opción (1 o 2), 0 para salir: ")
        print("elegiste la opción:", opt)

        match opt:
            case "1": consultar_clima()
            case "2": convertir_pago()
            case "0": break
            case _: print("opcion no valida") 

if __name__ == "__main__":
    main()