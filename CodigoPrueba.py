import os
from datetime import datetime

# Lista de campus con descripciones
CAMPUS = {
    "zona core": "Área principal de red de alta velocidad",
    "campus uno": "Edificio principal de la organización",
    "campus matriz": "Sede central de operaciones",
    "sector outsourcing": "Zona para servicios externalizados"
}

# Tipos de dispositivos y sus características
TIPOS_DISPOSITIVO = {
    1: {"nombre": "Router", "servicios": ["Enrutamiento"]},
    2: {"nombre": "Switch", "servicios": ["Datos", "VLAN", "Trunking"]},
    3: {"nombre": "Switch multicapa", "servicios": ["Datos", "VLAN", "Trunking", "Enrutamiento"]},
    4: {"nombre": "Dispositivo final", "servicios": ["Acceso a red"]}
}

JERARQUIAS = ["Núcleo", "Distribución", "Acceso", "Cliente"]

class Dispositivo:
    def __init__(self, tipo, nombre, ip, vlan, jerarquia, servicios):
        self.tipo = tipo
        self.nombre = nombre
        self.ip = ip
        self.vlan = vlan
        self.jerarquia = jerarquia
        self.servicios = servicios
        self.fecha_registro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def to_dict(self):
        return {
            "Tipo": self.tipo,
            "Nombre": self.nombre,
            "IP": self.ip,
            "VLAN": self.vlan,
            "Jerarquía": self.jerarquia,
            "Servicios": self.servicios,
            "Fecha Registro": self.fecha_registro
        }

def clear():
    """Limpia la pantalla de la consola"""
    os.system("cls" if os.name == "nt" else "clear")

def mostrar_campus():
    """Muestra los campus disponibles con sus descripciones"""
    print("\n🏫 CAMPUS DISPONIBLES:")
    for i, (nombre, desc) in enumerate(CAMPUS.items(), 1):
        print(f"{i}. {nombre.upper()} - {desc}")

def seleccionar_campus():
    """Permite al usuario seleccionar un campus"""
    mostrar_campus()
    while True:
        try:
            opcion = int(input("\nSeleccione un campus: ")) - 1
            if 0 <= opcion < len(CAMPUS):
                return list(CAMPUS.keys())[opcion]
            print("❌ Opción inválida. Intente nuevamente.")
        except ValueError:
            print("❌ Por favor ingrese un número válido.")

def listar_dispositivos(campus_seleccionado):
    """Lista todos los dispositivos de un campus con números"""
    nombre_archivo = f"{campus_seleccionado}.txt"
    dispositivos = []
    
    if os.path.exists(nombre_archivo):
        with open(nombre_archivo, "r") as f:
            contenido = f.read()
        
        # Separar cada dispositivo por el delimitador "======"
        dispositivos_raw = contenido.split("="*40)
        dispositivos_raw = [d.strip() for d in dispositivos_raw if d.strip()]
        
        for i, disp in enumerate(dispositivos_raw, 1):
            lineas = disp.split('\n')
            nombre = next((l.split(': ')[1] for l in lineas if l.startswith('Nombre: ')), "Desconocido")
            dispositivos.append((i, disp, nombre))
    
    return dispositivos

def ver_dispositivos():
    """Muestra los dispositivos de un campus seleccionado"""
    clear()
    campus_seleccionado = seleccionar_campus()
    dispositivos = listar_dispositivos(campus_seleccionado)
    
    if dispositivos:
        print(f"\n📡 DISPOSITIVOS EN {campus_seleccionado.upper()}:\n")
        for num, disp, nombre in dispositivos:
            print(f"🔢 {num}. Dispositivo: {nombre}")
            print(disp)
            print()
    else:
        print(f"\n❌ No hay dispositivos registrados en {campus_seleccionado}.")
    
    input("\nPresione Enter para continuar...")

def validar_ip(ip):
    """Valida una dirección IP básica"""
    if ip.lower() == "dhcp":
        return True
    partes = ip.split('.')
    if len(partes) != 4:
        return False
    for parte in partes:
        if not parte.isdigit() or not 0 <= int(parte) <= 255:
            return False
    return True

def seleccionar_servicios(tipo_dispositivo):
    """Permite seleccionar servicios según el tipo de dispositivo"""
    if tipo_dispositivo == 4:  # Dispositivo final tiene servicios fijos
        return "Acceso a red"
    
    servicios_disponibles = TIPOS_DISPOSITIVO[tipo_dispositivo]["servicios"]
    servicios_seleccionados = []
    
    print("\n🔧 SERVICIOS DISPONIBLES:")
    while True:
        for i, servicio in enumerate(servicios_disponibles, 1):
            print(f"{i}. {servicio}")
        print("0. Terminar selección")
        
        try:
            opcion = int(input("Seleccione un servicio (0 para terminar): "))
            if opcion == 0:
                break
            if 1 <= opcion <= len(servicios_disponibles):
                servicio = servicios_disponibles[opcion-1]
                if servicio not in servicios_seleccionados:
                    servicios_seleccionados.append(servicio)
                    print(f"✅ {servicio} añadido")
                else:
                    print("⚠️ Este servicio ya fue seleccionado")
            else:
                print("❌ Opción inválida")
        except ValueError:
            print("❌ Por favor ingrese un número")
    
    return ", ".join(servicios_seleccionados) if servicios_seleccionados else "Ninguno"

def agregar_dispositivo():
    """Agrega un nuevo dispositivo a un campus"""
    clear()
    print("➕ AÑADIR NUEVO DISPOSITIVO\n")
    
    # Selección de campus
    campus_seleccionado = seleccionar_campus()
    nombre_archivo = f"{campus_seleccionado}.txt"
    
    # Selección de tipo de dispositivo
    print("\n📌 TIPO DE DISPOSITIVO:")
    for num, info in TIPOS_DISPOSITIVO.items():
        print(f"{num}. {info['nombre']}")
    
    while True:
        try:
            tipo = int(input("Seleccione el tipo: "))
            if tipo in TIPOS_DISPOSITIVO:
                break
            print("❌ Opción inválida")
        except ValueError:
            print("❌ Por favor ingrese un número")
    
    # Datos del dispositivo
    print("\n📝 INGRESE LOS DATOS DEL DISPOSITIVO")
    while True:
        nombre = input("Nombre del dispositivo: ").strip()
        if nombre:
            break
        print("❌ El nombre no puede estar vacío")
    
    while True:
        ip = input("Dirección IP (o 'DHCP' para asignación automática): ").strip()
        if validar_ip(ip):
            break
        print("❌ IP inválida. Formato esperado: XXX.XXX.XXX.XXX o 'DHCP'")
    
    # VLAN solo para dispositivos de red (no para dispositivos finales)
    if tipo == 4:  # Dispositivo final
        vlan = "N/A"
    else:
        vlan = input("VLANs configuradas (separadas por coma): ").strip()
    
    # Jerarquía adaptada para dispositivos finales
    print("\n🏗️  JERARQUÍA DEL DISPOSITIVO:")
    jerarquias_disponibles = JERARQUIAS.copy()
    if tipo == 4:  # Dispositivo final solo puede ser Cliente
        jerarquia = "Cliente"
        print("1. Cliente (seleccionado automáticamente para dispositivos finales)")
    else:
        for i, jerarquia in enumerate(jerarquias_disponibles, 1):
            print(f"{i}. {jerarquia}")
        
        while True:
            try:
                jerarquia_num = int(input("Seleccione la jerarquía: "))
                if 1 <= jerarquia_num <= len(jerarquias_disponibles):
                    jerarquia = jerarquias_disponibles[jerarquia_num-1]
                    break
                print("❌ Opción inválida")
            except ValueError:
                print("❌ Por favor ingrese un número")
    
    # Servicios (automático para dispositivos finales)
    servicios = seleccionar_servicios(tipo)
    
    # Crear y guardar dispositivo
    dispositivo = Dispositivo(
        tipo=TIPOS_DISPOSITIVO[tipo]["nombre"],
        nombre=nombre,
        ip=ip,
        vlan=vlan,
        jerarquia=jerarquia,
        servicios=servicios
    )
    
    with open(nombre_archivo, "a") as f:
        f.write("\n" + "="*40 + "\n")
        for clave, valor in dispositivo.to_dict().items():
            f.write(f"{clave}: {valor}\n")
        f.write("="*40 + "\n")
    
    print(f"\n✅ Dispositivo '{nombre}' registrado exitosamente en {campus_seleccionado}!")
    input("Presione Enter para continuar...")

def borrar_dispositivo():
    """Elimina un dispositivo específico de un campus"""
    clear()
    print("🗑️  BORRAR DISPOSITIVO\n")
    
    # Selección de campus
    campus_seleccionado = seleccionar_campus()
    nombre_archivo = f"{campus_seleccionado}.txt"
    
    if not os.path.exists(nombre_archivo):
        print(f"\n❌ No hay dispositivos registrados en {campus_seleccionado}.")
        input("\nPresione Enter para continuar...")
        return
    
    # Mostrar dispositivos con números
    dispositivos = listar_dispositivos(campus_seleccionado)
    print(f"\n📡 DISPOSITIVOS EN {campus_seleccionado.upper()}:\n")
    for num, disp, nombre in dispositivos:
        print(f"🔢 {num}. Dispositivo: {nombre}")
    
    # Seleccionar dispositivo a borrar
    while True:
        try:
            opcion = int(input("\nSeleccione el número del dispositivo a borrar (0 para cancelar): "))
            if opcion == 0:
                print("\nOperación cancelada.")
                input("Presione Enter para continuar...")
                return
            if 1 <= opcion <= len(dispositivos):
                break
            print("❌ Número de dispositivo inválido")
        except ValueError:
            print("❌ Por favor ingrese un número válido")
    
    # Confirmar borrado
    dispositivo_seleccionado = dispositivos[opcion-1]
    print(f"\n⚠️  ESTÁ A PUNTO DE BORRAR EL SIGUIENTE DISPOSITIVO:")
    print(dispositivo_seleccionado[1])
    confirmacion = input("\n¿Está seguro que desea borrarlo? (s/n): ").lower()
    
    if confirmacion == 's':
        # Reconstruir el archivo excluyendo el dispositivo seleccionado
        nuevos_dispositivos = [d[1] for i, d in enumerate(dispositivos) if i != opcion-1]
        
        with open(nombre_archivo, "w") as f:
            f.write("\n".join(nuevos_dispositivos))
        
        print("\n✅ Dispositivo borrado exitosamente!")
    else:
        print("\nOperación cancelada.")
    
    input("\nPresione Enter para continuar...")

def menu():
    """Muestra el menú principal"""
    while True:
        clear()
        print("🔌 SISTEMA DE GESTIÓN DE DISPOSITIVOS DE RED")
        print("\n¿Qué desea hacer?")
        print("1. 👀 Ver dispositivos de un campus")
        print("2. 🏫 Ver información de los campus")
        print("3. ➕ Añadir nuevo dispositivo")
        print("4. 🗑️  Borrar dispositivo")
        print("5. 🚪 Salir")
        
        opcion = input("\nSeleccione una opción: ").strip()
        
        if opcion == "1":
            ver_dispositivos()
        elif opcion == "2":
            clear()
            mostrar_campus()
            input("\nPresione Enter para continuar...")
        elif opcion == "3":
            agregar_dispositivo()
        elif opcion == "4":
            borrar_dispositivo()
        elif opcion == "5":
            print("\n👋 ¡Hasta pronto!")
            break
        else:
            print("\n❌ Opción inválida. Intente nuevamente.")
            input("Presione Enter para continuar...")

if __name__ == "__main__":
    menu()