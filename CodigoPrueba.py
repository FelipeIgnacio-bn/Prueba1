import os

# Lista de campus
campus = ["zona core", "campus uno", "campus matriz", "sector outsourcing"]

# Función para limpiar pantalla
def clear():
    os.system("cls" if os.name == "nt" else "clear")

# Función para mostrar los campus
def mostrar_campus():
    print("\nCampus disponibles:")
    for i, c in enumerate(campus, 1):
        print(f"{i}. {c}")

# Función para ver dispositivos
def ver_dispositivos():
    clear()
    mostrar_campus()
    opcion = int(input("\nSeleccione un campus para ver los dispositivos: ")) - 1
    if 0 <= opcion < len(campus):
        nombre_archivo = campus[opcion] + ".txt"
        if os.path.exists(nombre_archivo):
            with open(nombre_archivo, "r") as f:
                print(f.read())
        else:
            print("No hay dispositivos registrados en este campus.")
    input("\nPresione Enter para continuar...")

# Función para añadir dispositivo
def agregar_dispositivo():
    clear()
    mostrar_campus()
    opcion = int(input("\nSeleccione un campus para agregar el dispositivo: ")) - 1
    if 0 <= opcion < len(campus):
        nombre_archivo = campus[opcion] + ".txt"
        dispositivo = {}

        print("\nSeleccione el tipo de dispositivo:")
        print("1. Router\n2. Switch\n3. Switch multicapa")
        tipo = int(input("Opción: "))
        tipos_dispositivo = ["Router", "Switch", "Switch multicapa"]
        dispositivo["Tipo"] = tipos_dispositivo[tipo - 1]

        dispositivo["Nombre"] = input("\nNombre del dispositivo: ")
        dispositivo["IP"] = input("Dirección IP: ")
        dispositivo["VLAN"] = input("VLAN configuradas (separadas por coma): ")

        print("\nSeleccione la jerarquía del dispositivo:")
        print("1. Núcleo\n2. Distribución\n3. Acceso")
        jerarquia = int(input("Opción: "))
        capas = ["Núcleo", "Distribución", "Acceso"]
        dispositivo["Jerarquía"] = capas[jerarquia - 1]

        print("\nSeleccione servicios de red (termine con 0):")
        servicios = []
        if tipo == 1:
            opciones = ["Enrutamiento"]
        elif tipo == 2:
            opciones = ["Datos", "VLAN", "Trunking"]
        else:
            opciones = ["Datos", "VLAN", "Trunking", "Enrutamiento"]

        while True:
            for i, serv in enumerate(opciones, 1):
                print(f"{i}. {serv}")
            print("0. Terminar")
            sel = int(input("Servicio: "))
            if sel == 0:
                break
            if 1 <= sel <= len(opciones):
                servicios.append(opciones[sel - 1])

        dispositivo["Servicios"] = ", ".join(servicios)

        with open(nombre_archivo, "a") as f:
            f.write("\n---------------------------------\n")
            for k, v in dispositivo.items():
                f.write(f"{k}: {v}\n")
            f.write("---------------------------------\n")

        print("\n✅ Dispositivo agregado correctamente.")
        input("Presione Enter para continuar...")

# Menú principal
def menu():
    while True:
        clear()
        print("¿Qué desea hacer?")
        print("1. Ver los dispositivos")
        print("2. Ver los campus")
        print("3. Añadir dispositivo")
        print("4. Salir")
        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            ver_dispositivos()
        elif opcion == "2":
            clear()
            mostrar_campus()
            input("\nPresione Enter para continuar...")
        elif opcion == "3":
            agregar_dispositivo()
        elif opcion == "4":
            print("Saliendo...")
            break
        else:
            print("Opción inválida. Intente nuevamente.")
            input("\nPresione Enter para continuar...")

# Ejecutar el menú
menu()
