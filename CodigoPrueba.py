import re
import os
import sys
import platform
import subprocess # <<< NUEVO: Para un ping más controlado
from time import sleep
from datetime import datetime
import json # <<< NUEVO: Para persistencia de datos

# 🌈 Paleta de colores y estilos
class Color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

# ---------------- GLOBAL VARIABLES ----------------
current_user = None
menu_history = []
NOMBRE_ARCHIVO_DATOS = "dispositivos_red.json" # <<< NUEVO: Nombre del archivo para guardar datos
# ---------------------------------------------------

# 🎨 Diseño de la interfaz
def limpiar_pantalla():
    os.system('cls' if os.name == 'nt' else 'clear')

def mostrar_barra_progreso(duracion_segundos, mensaje="Cargando...", prefijo="", sufijo="Completado"):
    total_pasos = 20
    tiempo_por_paso = duracion_segundos / total_pasos if total_pasos > 0 and duracion_segundos > 0 else 0

    print(f"{Color.BLUE}{prefijo}{mensaje}{Color.END}")
    for i in range(total_pasos + 1):
        porcentaje = int((i / total_pasos) * 100) if total_pasos > 0 else 100
        barra = '█' * i + ' ' * (total_pasos - i)
        print(f"\r{Color.GREEN}[{barra}] {porcentaje}%{Color.END}", end="", flush=True)
        if tiempo_por_paso > 0:
            sleep(tiempo_por_paso)
    print(f"\n{Color.GREEN}{sufijo}{Color.END}\n")
    if duracion_segundos == 0 and tiempo_por_paso == 0:
        porcentaje = 100
        barra = '█' * total_pasos
        print(f"\r{Color.GREEN}[{barra}] {porcentaje}%{Color.END}", end="", flush=True)
        print(f"\n{Color.GREEN}{sufijo}{Color.END}\n")
    sleep(0.5)


def mostrar_titulo(titulo, con_usuario=True):
    limpiar_pantalla()
    print(f"{Color.BLUE}{'═' * 70}{Color.END}")
    print(f"{Color.BOLD}{Color.PURPLE}{titulo.center(70)}{Color.END}")
    if con_usuario and current_user:
        usuario_info = f"Usuario: {current_user}"
        print(f"{Color.DARKCYAN}{usuario_info.center(70)}{Color.END}")
    print(f"{Color.BLUE}{'═' * 70}{Color.END}\n")

def mostrar_mensaje(mensaje, tipo="info", esperar_enter=False):
    icono = ""
    color = Color.BLUE
    if tipo == "error": icono = "❌ "; color = Color.RED
    elif tipo == "exito": icono = "✅ "; color = Color.GREEN
    elif tipo == "advertencia": icono = "⚠️ "; color = Color.YELLOW
    elif tipo == "info": icono = "ℹ️ "
    print(f"{color}{Color.BOLD}{icono}{mensaje}{Color.END}\n")
    if esperar_enter:
        input(f"{Color.GREEN}Presione Enter para continuar...{Color.END}")

# ---------------- PERSISTENCIA DE DATOS (JSON) ----------------
def cargar_dispositivos_desde_archivo():
    """Carga la lista de dispositivos desde un archivo JSON."""
    try:
        if os.path.exists(NOMBRE_ARCHIVO_DATOS):
            with open(NOMBRE_ARCHIVO_DATOS, 'r', encoding='utf-8') as f:
                dispositivos = json.load(f)
                mostrar_mensaje(f"Datos cargados desde '{NOMBRE_ARCHIVO_DATOS}'.", "info")
                return dispositivos
        else:
            mostrar_mensaje(f"Archivo '{NOMBRE_ARCHIVO_DATOS}' no encontrado. Se iniciará con una lista vacía.", "advertencia")
            return []
    except (json.JSONDecodeError, IOError) as e:
        mostrar_mensaje(f"Error al cargar datos desde '{NOMBRE_ARCHIVO_DATOS}': {e}. Se iniciará con una lista vacía.", "error")
        return []

def guardar_dispositivos_en_archivo(dispositivos_lista):
    """Guarda la lista de dispositivos en un archivo JSON."""
    try:
        with open(NOMBRE_ARCHIVO_DATOS, 'w', encoding='utf-8') as f:
            json.dump(dispositivos_lista, f, indent=4, ensure_ascii=False)
        # No mostrar mensaje de guardado exitoso aquí para no saturar, se maneja en cada función que guarda.
    except IOError as e:
        mostrar_mensaje(f"Error al guardar datos en '{NOMBRE_ARCHIVO_DATOS}': {e}", "error", esperar_enter=True)

# ---------------- SISTEMA DE INICIO DE SESIÓN ----------------
USUARIOS_PREDEFINIDOS = {
    "Emanuel": "pruebaredes",
    "Felipe": "pruebaredes",
    "Nicolas": "pruebaredes"
}

def iniciar_sesion():
    global current_user
    intentos_fallidos = 0
    max_intentos = 3
    while intentos_fallidos < max_intentos:
        mostrar_titulo("INICIO DE SESIÓN", con_usuario=False)
        usuario = input(f"{Color.GREEN}👤 Nombre de Usuario: {Color.END}").strip()
        contrasena = input(f"{Color.GREEN}🔑 Contraseña: {Color.END}").strip()
        if usuario in USUARIOS_PREDEFINIDOS and USUARIOS_PREDEFINIDOS[usuario] == contrasena:
            current_user = usuario
            mostrar_barra_progreso(1, mensaje="Autenticando...", sufijo=f"¡Bienvenido, {current_user}!")
            return True
        else:
            intentos_fallidos += 1
            restantes = max_intentos - intentos_fallidos
            if restantes > 0:
                mostrar_mensaje(f"Usuario o contraseña incorrectos. Intentos restantes: {restantes}", "error")
                sleep(2)
            else:
                mostrar_mensaje("Demasiados intentos fallidos. El programa se cerrará.", "error")
                sleep(3); limpiar_pantalla(); sys.exit()
    return False

# ---------------- DEFINICIÓN DE CONSTANTES Y VALIDACIONES ----------------
SERVICIOS_VALIDOS = {'DNS': '🔍 DNS', 'DHCP': '🌐 DHCP', 'WEB': '🕸️ Servicio Web', 'BD': '🗃️ Base de Datos', 'CORREO': '✉️ Servicio de Correo', 'VPN': '🛡️ VPN'}
TIPOS_DISPOSITIVO = {'PC': '💻 PC', 'SERVIDOR':'🖧 Servidor', 'ROUTER': '📶 Router', 'SWITCH': '🔀 Switch', 'FIREWALL': '🔥 Firewall', 'IMPRESORA': '🖨️ Impresora'}
CAPAS_RED = {'NUCLEO': '💎 Núcleo (Core)', 'DISTRIBUCION': '📦 Distribución', 'ACCESO': '🔌 Acceso', 'N/A': 'N/A'} # N/A añadido

def validar_ip(ip):
    if not ip: # Permite IP vacía que se tratará como "N/A"
        return True
    if not re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', ip):
        raise ValueError("Formato incorrecto. Debe ser X.X.X.X donde X es un número (0-255)")
    octetos = ip.split('.')
    if len(octetos) != 4:
        raise ValueError("La IP debe tener exactamente 4 partes separadas por puntos")
    for i, octeto_str in enumerate(octetos):
        try:
            octeto_num = int(octeto_str)
            if not (0 <= octeto_num <= 255):
                raise ValueError(f"El octeto '{octeto_num}' no es válido (debe estar entre 0-255)")
        except ValueError:
            raise ValueError(f"El octeto '{octeto_str}' no es un número válido.")

    primer_octeto = int(octetos[0])
    if primer_octeto == 0:
        raise ValueError("El primer octeto no puede ser 0 (red 'esta red').")
    if primer_octeto == 127:
        raise ValueError("Las IPs 127.x.x.x están reservadas para loopback.")
    if primer_octeto >= 224 and primer_octeto <= 239:
        raise ValueError("Las IPs 224.x.x.x a 239.x.x.x están reservadas para multicast.")
    if primer_octeto >= 240:
        raise ValueError("Las IPs 240.x.x.x y superiores están reservadas para uso futuro.")
    if ip == "255.255.255.255":
        raise ValueError("La IP 255.255.255.255 está reservada para broadcast limitado.")
    return True


def validar_nombre(nombre):
    if not re.match(r'^[a-zA-Z0-9\-\.\s_]+$', nombre):
        raise ValueError("Nombre contiene caracteres inválidos. Permitidos: letras, números, espacios, guiones, puntos y guiones bajos.")
    if not 3 <= len(nombre.strip()) <= 50:
        raise ValueError("El nombre debe tener entre 3 y 50 caracteres.")
    return True

def validar_servicios_lista(servicios_lista):
    for servicio in servicios_lista:
        if servicio not in SERVICIOS_VALIDOS.values():
            raise ValueError(f"Servicio inválido en la lista: {servicio}")
    return True

def validar_vlans_input(vlans_str):
    if not vlans_str.strip():
        return []
    vlan_list_str = vlans_str.split(',')
    vlans_int = []
    for v_str in vlan_list_str:
        v_str = v_str.strip()
        if not v_str.isdigit():
            raise ValueError(f"VLAN '{v_str}' no es un número válido.")
        v_int = int(v_str)
        if not (1 <= v_int <= 4094):
            raise ValueError(f"VLAN '{v_int}' fuera del rango válido (1-4094).")
        if v_int in vlans_int:
             mostrar_mensaje(f"VLAN '{v_int}' ya ingresada en esta lista. Se omitirá el duplicado.", "advertencia")
        else:
            vlans_int.append(v_int)
    return sorted(list(set(vlans_int)))


def crear_dispositivo(tipo, nombre, ip=None, ubicacion=None, servicios=None, vlans=None): # 'capa' renombrada a 'ubicacion'
    try:
        validar_nombre(nombre)
        if ip and ip != "N/A": validar_ip(ip)
        if servicios: validar_servicios_lista(servicios)

        dispositivo_data = {
            "TIPO": tipo,
            "NOMBRE": nombre,
            "IP": ip if ip else "N/A",
            "UBICACION": ubicacion if ubicacion else "N/A", # Usando UBICACION consistentemente
            "SERVICIOS": servicios if servicios else [],
            "VLANS": vlans if vlans else []
        }
        return dispositivo_data
    except ValueError as e:
        mostrar_mensaje(f"Error al definir datos del dispositivo: {e}", "error")
        return None

# ---------------- FUNCIONES DE MENÚ Y NAVEGACIÓN ----------------
def push_menu_history(menu_function): menu_history.append(menu_function)
def pop_menu_history():
    if len(menu_history) > 1: menu_history.pop()
    elif len(menu_history) == 1: return menu_history[0]
    return menu_history[-1] if menu_history else None


def ir_a_menu_principal():
    global menu_history
    if menu_history:
        menu_principal_func = menu_history[0]
        menu_history = [menu_principal_func]
        mostrar_barra_progreso(0.5, "Volviendo al Menú Principal...")
        menu_principal_func()
    else:
        mostrar_mensaje("Error: No se encuentra el menú principal en el historial.", "error")
        main()

def salir_del_programa():
    mostrar_titulo("SALIR DEL PROGRAMA")
    confirmar = input(f"{Color.YELLOW}❓ ¿Está seguro de que desea salir? (s/n): {Color.END}").lower()
    if confirmar == 's':
        mostrar_barra_progreso(1, "Cerrando sesión y saliendo...", sufijo="¡Hasta pronto! 👋")
        limpiar_pantalla(); sys.exit()
    else:
        mostrar_mensaje("Operación cancelada.", "info"); sleep(1)
        if menu_history: menu_history[-1]()
        else: main()

def mostrar_opciones_navegacion(menu_actual_func, es_menu_principal=False):
    print(f"\n{Color.BLUE}{'─' * 70}{Color.END}")
    opciones_nav = {}
    if not es_menu_principal and len(menu_history) > 1:
        opciones_nav['b'] = (f"{Color.YELLOW}b. ⬅️ Volver al Menú Anterior{Color.END}", lambda: pop_menu_history()())
    if not es_menu_principal:
        opciones_nav['m'] = (f"{Color.YELLOW}m. 🏠 Volver al Menú Principal{Color.END}", ir_a_menu_principal)
    opciones_nav['s'] = (f"{Color.YELLOW}s. 🚪 Salir del Programa (Directo){Color.END}", salir_del_programa)

    if not opciones_nav and es_menu_principal:
        print(f"{Color.BLUE}{'─' * 70}{Color.END}")
        return input(f"{Color.GREEN}↳ Seleccione una opción del menú: {Color.END}").strip().lower()

    for _, (texto, _) in opciones_nav.items(): print(texto)
    print(f"{Color.BLUE}{'─' * 70}{Color.END}")

    while True:
        prompt_partes = ["↳ Seleccione opción del menú"]
        nav_keys = list(opciones_nav.keys())
        if nav_keys: prompt_partes.append(f"o navegación ({', '.join(nav_keys)})")

        opcion_input = input(f"{Color.GREEN}{' '.join(prompt_partes)}: {Color.END}").strip().lower()

        if opcion_input in opciones_nav:
            _, funcion_nav = opciones_nav[opcion_input]
            if funcion_nav.__code__.co_name == "<lambda>":
                funcion_destino = pop_menu_history()
                if funcion_destino:
                    mostrar_barra_progreso(0.5, "Volviendo...")
                    funcion_destino()
                    return None
                else:
                    mostrar_mensaje("No hay menú anterior o error de navegación.", "info")
                    sleep(1)
                    menu_actual_func()
                    return None
            else:
                funcion_nav()
                return None
        else:
            return opcion_input


# ------------------- FUNCIONALIDAD DE PING (MEJORADA) -------------------
def hacer_ping(ip_address):
    if not ip_address or ip_address == "N/A":
        mostrar_mensaje("Este dispositivo no tiene una IP asignada para hacer ping.", "advertencia", esperar_enter=True)
        return

    param_conteo = '-n' if platform.system().lower() == 'windows' else '-c'
    comando = ['ping', param_conteo, '4', ip_address]

    mostrar_titulo(f"PING A {ip_address}")
    print(f"{Color.CYAN}Ejecutando comando: {' '.join(comando)}{Color.END}\n")
    print(f"{Color.YELLOW}Enviando paquetes, por favor espere (timeout 10s)...{Color.END}\n")

    try:
        resultado_proceso = subprocess.run(comando, capture_output=True, text=True, timeout=10, check=False, errors='replace')

        print(f"{Color.BLUE}{'-'*30} INICIO SALIDA PING {'-'*30}{Color.END}")
        if resultado_proceso.stdout:
            print(f"{Color.DARKCYAN}Salida Estándar:{Color.END}\n{resultado_proceso.stdout}")
        if resultado_proceso.stderr:
            print(f"{Color.RED}Salida de Error:{Color.END}\n{resultado_proceso.stderr}")
        print(f"{Color.BLUE}{'-'*31} FIN SALIDA PING {'-'*31}{Color.END}\n")

        if resultado_proceso.returncode == 0:
            fallo_logico = False
            if platform.system().lower() != 'windows':
                if "0 received" in resultado_proceso.stdout or \
                   "100.0% packet loss" in resultado_proceso.stdout or \
                   "100% packet loss" in resultado_proceso.stdout:
                    fallo_logico = True
            elif platform.system().lower() == 'windows':
                 if "Host de destino inaccesible." in resultado_proceso.stdout or \
                    "Destination host unreachable." in resultado_proceso.stdout or \
                    "Tiempo de espera agotado para esta solicitud." in resultado_proceso.stdout or \
                    "Request timed out." in resultado_proceso.stdout or \
                    "inaccesible" in resultado_proceso.stdout.lower() or \
                    "unreachable" in resultado_proceso.stdout.lower():
                    if "recibidos = 0" in resultado_proceso.stdout or "Received = 0" in resultado_proceso.stdout:
                         fallo_logico = True
                 elif 'ttl=' not in resultado_proceso.stdout.lower():
                        match_perdida_total = re.search(r"(perdidos|Lost)\s*=\s*4\s*\(100%\s*(pérdida|loss)\)", resultado_proceso.stdout)
                        if match_perdida_total:
                            fallo_logico = True
                 elif 'bytes=' not in resultado_proceso.stdout.lower() and 'tiempo=' not in resultado_proceso.stdout.lower() and 'time=' not in resultado_proceso.stdout.lower():
                             fallo_logico = True

            if fallo_logico:
                 mostrar_mensaje(f"⚠️  PING a {ip_address} PARECE HABER FALLADO (posible pérdida total de paquetes o host inalcanzable), aunque el comando finalizó sin error del sistema.", "advertencia")
            else:
                mostrar_mensaje(f"✅ PING a {ip_address} EXITOSO (código de retorno del sistema: {resultado_proceso.returncode}).", "exito")
        else:
            mostrar_mensaje(f"❌ PING a {ip_address} FALLIDO (código de retorno del sistema: {resultado_proceso.returncode}). El host podría ser inalcanzable o la red tener problemas.", "error")

    except subprocess.TimeoutExpired:
        mostrar_mensaje(f"❌ PING a {ip_address} FALLIDO: Tiempo de espera agotado (10 segundos).", "error")
    except FileNotFoundError:
        mostrar_mensaje(f"❌ Error Crítico: El comando 'ping' no se encontró en el sistema. Asegúrese de que esté instalado y en el PATH del sistema.", "error")
    except Exception as e:
        mostrar_mensaje(f"❌ Ocurrió un error inesperado al ejecutar el comando ping: {e}", "error")

    input(f"{Color.GREEN}Presione Enter para continuar...{Color.END}")


def menu_ping_dispositivo(dispositivos_lista):
    current_menu_func = lambda: menu_ping_dispositivo(dispositivos_lista)
    push_menu_history(current_menu_func)
    while True:
        mostrar_titulo("🌐 PROBAR CONECTIVIDAD (PING)")
        dispositivos_con_ip = [d for d in dispositivos_lista if d.get("IP") and d.get("IP") != "N/A"]
        if not dispositivos_con_ip:
            mostrar_mensaje("No hay dispositivos con IPs asignadas para hacer ping.", "advertencia", esperar_enter=True)
            pop_menu_history()(); return

        print(f"{Color.BOLD}Seleccione un dispositivo para hacer PING:{Color.END}")
        for i, d in enumerate(dispositivos_con_ip, 1):
            print(f"{Color.YELLOW}{i}.{Color.END} {d.get('NOMBRE')} ({d.get('IP')})")

        opcion = mostrar_opciones_navegacion(current_menu_func)

        if opcion is None: return

        try:
            opcion_num = int(opcion)
            if 1 <= opcion_num <= len(dispositivos_con_ip):
                hacer_ping(dispositivos_con_ip[opcion_num - 1].get("IP"))
            else:
                mostrar_mensaje(f"Opción inválida. Debe ser entre 1 y {len(dispositivos_con_ip)} o una opción de navegación.", "error"); sleep(2)
        except ValueError:
            mostrar_mensaje("Entrada inválida. Por favor, ingrese un número o una opción de navegación.", "error"); sleep(2)


# ---------------- FUNCIONES DE GESTIÓN DE DISPOSITIVOS ----------------
def seleccionar_opcion_menu(opciones_dict, titulo_seleccion, prompt_usuario, permitir_cancelar=False, valor_actual=None):
    print(f"\n{Color.BOLD}{titulo_seleccion}{Color.END}")
    if valor_actual:
        print(f"{Color.DARKCYAN}Valor actual: {valor_actual}{Color.END}")

    opciones_list = list(opciones_dict.items())
    for i, (_, valor_mostrado) in enumerate(opciones_list, 1):
        print(f"{Color.YELLOW}{i}.{Color.END} {valor_mostrado}")
    if permitir_cancelar:
        print(f"{Color.YELLOW}0.{Color.END} Cancelar / Volver{' (Mantener actual)' if valor_actual else ''}")

    while True:
        try:
            opcion_input = input(f"\n{Color.GREEN}↳ {prompt_usuario} (1-{len(opciones_list)}{', 0' if permitir_cancelar else ''}): {Color.END}").strip()
            if permitir_cancelar and opcion_input == "0":
                return None # Indica cancelación o mantener valor actual si se usa en modificar
            opcion_num = int(opcion_input)
            if 1 <= opcion_num <= len(opciones_list):
                return opciones_list[opcion_num-1][1] # Devuelve el valor descriptivo
            else:
                mostrar_mensaje(f"Opción debe ser entre 1 y {len(opciones_list)}{' o 0' if permitir_cancelar else ''}.", "error")
        except ValueError:
            mostrar_mensaje("Entrada numérica inválida.", "error")

def ingresar_ip_interactivo(dispositivos_lista, dispositivo_actual=None):
    """ Permite ingresar una IP, validarla y verificar unicidad (excepto para el dispositivo_actual)."""
    while True:
        valor_actual_ip = dispositivo_actual.get("IP", "N/A") if dispositivo_actual else "N/A"
        prompt = f"{Color.GREEN}↳ Ingrese la dirección IP del dispositivo (Actual: {valor_actual_ip}, Enter para mantener o si no aplica): {Color.END}" if dispositivo_actual else f"{Color.GREEN}↳ Ingrese la dirección IP del dispositivo (Enter si no aplica): {Color.END}"

        ip = input(prompt).strip()

        if dispositivo_actual and not ip: # Mantener IP actual si se está modificando y no se ingresa nada
            return valor_actual_ip

        if not ip: # Para agregar nuevo dispositivo o si se borra la IP en modificación
            return "N/A"
        try:
            validar_ip(ip)
            if ip != "N/A":
                for disp in dispositivos_lista:
                    if disp is dispositivo_actual: # No comparar consigo mismo si se está modificando
                        continue
                    if disp.get("IP") == ip:
                        raise ValueError(f"La IP '{ip}' ya está asignada al dispositivo '{disp.get('NOMBRE')}'. Use una IP única.")
            return ip
        except ValueError as e:
            mostrar_mensaje(f"{str(e)}", "error")
            if "Formato incorrecto" in str(e) or "Octeto" in str(e):
                print(f"{Color.YELLOW}💡 Ejemplos: 192.168.1.10, 10.0.0.5{Color.END}")


def agregar_dispositivo_interactivo(dispositivos_lista):
    current_menu_func = lambda: agregar_dispositivo_interactivo(dispositivos_lista)
    push_menu_history(current_menu_func)
    mostrar_titulo("📱 AGREGAR NUEVO DISPOSITIVO")

    tipo = seleccionar_opcion_menu(TIPOS_DISPOSITIVO, "Seleccione el tipo de dispositivo:", "Tipo", permitir_cancelar=True)
    if tipo is None:
        pop_menu_history()(); return

    nombre = ""
    while not nombre:
        temp_nombre = input(f"{Color.GREEN}↳ Nombre del dispositivo (3-50 caract.): {Color.END}").strip()
        try:
            validar_nombre(temp_nombre)
            if any(d.get("NOMBRE","").lower() == temp_nombre.lower() for d in dispositivos_lista):
                mostrar_mensaje(f"El nombre '{temp_nombre}' ya existe. Intente con otro.", "advertencia")
            else:
                nombre = temp_nombre
        except ValueError as e:
            mostrar_mensaje(str(e), "error")

    ip_asignada = "N/A"
    tipo_key = next((k for k, v in TIPOS_DISPOSITIVO.items() if v == tipo), None)
    # Todos los dispositivos pueden tener IP opcionalmente
    ip_asignada = ingresar_ip_interactivo(dispositivos_lista)
    if ip_asignada is None: # Esto no debería pasar con la lógica actual de ingresar_ip_interactivo
        pop_menu_history()(); return


    ubicacion_asignada = "N/A" # Usamos 'ubicacion' en lugar de 'capa'
    # La ubicación (Capa de Red) es más relevante para Routers y Switches, pero puede ser opcional para otros.
    if tipo_key in ['ROUTER', 'SWITCH']:
        ubicacion_sel = seleccionar_opcion_menu(CAPAS_RED, "Seleccione la ubicación/capa de red:", "Ubicación/Capa", permitir_cancelar=True)
        if ubicacion_sel is None:
            mostrar_mensaje("Se asignará 'N/A' a la ubicación/capa de red.", "info")
            sleep(1)
        else:
            ubicacion_asignada = ubicacion_sel
    else: # Para otros tipos de dispositivo, preguntar si se desea añadir ubicación
        if input(f"{Color.GREEN}¿Desea especificar una ubicación/capa de red para este {tipo}? (s/n): {Color.END}").lower() == 's':
            ubicacion_sel = seleccionar_opcion_menu(CAPAS_RED, "Seleccione la ubicación/capa de red:", "Ubicación/Capa", permitir_cancelar=True)
            if ubicacion_sel:
                ubicacion_asignada = ubicacion_sel


    servicios_sel_list = []
    if tipo_key in ['SERVIDOR', 'ROUTER', 'FIREWALL']: # Servicios aplican principalmente a estos
        print(f"\n{Color.BOLD}🛠️  Agregar servicios al dispositivo '{nombre}':{Color.END}")
        print(f"{Color.DARKCYAN}Puede ingresar varios números de servicio separados por comas (ej: 1,3,5).{Color.END}")
        print(f"{Color.DARKCYAN}Presione Enter si no desea agregar servicios.{Color.END}")

        servicios_opciones_list = list(SERVICIOS_VALIDOS.items())
        for i, (_, valor_mostrado) in enumerate(servicios_opciones_list, 1):
            print(f"{Color.YELLOW}{i}.{Color.END} {valor_mostrado}")

        while True:
            servicios_input = input(f"{Color.GREEN}↳ Ingrese números de servicios (separados por coma, o Enter para omitir): {Color.END}").strip()
            if not servicios_input:
                break
            servicios_temp_list = []
            numeros_servicios_str = servicios_input.split(',')
            valido = True
            for num_str in numeros_servicios_str:
                num_str = num_str.strip()
                if not num_str.isdigit():
                    mostrar_mensaje(f"'{num_str}' no es un número válido para servicio.", "error"); valido = False; break
                num_int = int(num_str)
                if not (1 <= num_int <= len(servicios_opciones_list)):
                    mostrar_mensaje(f"Número de servicio '{num_int}' fuera de rango (1-{len(servicios_opciones_list)}).", "error"); valido = False; break
                servicio_elegido_valor = servicios_opciones_list[num_int - 1][1]
                if servicio_elegido_valor not in servicios_temp_list:
                    servicios_temp_list.append(servicio_elegido_valor)
                else:
                    mostrar_mensaje(f"Servicio '{servicio_elegido_valor}' ya incluido en esta entrada.", "advertencia")
            if valido:
                servicios_sel_list = sorted(list(set(servicios_temp_list)))
                mostrar_mensaje(f"Servicios seleccionados: {', '.join(servicios_sel_list) if servicios_sel_list else 'Ninguno'}", "exito")
                break
            else:
                servicios_sel_list = []

    vlans_list = []
    # VLANs pueden aplicar a muchos dispositivos, no solo switches.
    if input(f"{Color.GREEN}¿Desea asignar VLANs a este {tipo}? (s/n): {Color.END}").lower() == 's':
        print(f"\n{Color.BOLD}🔗 Agregar VLANs al dispositivo '{nombre}':{Color.END}")
        print(f"{Color.DARKCYAN}Puede ingresar varias VLANs separadas por comas (ej: 10,20,30).{Color.END}")
        print(f"{Color.DARKCYAN}Presione Enter si no desea asignar VLANs.{Color.END}")
        while True:
            vlans_input_str = input(f"{Color.GREEN}↳ Ingrese VLANs (números entre 1-4094, separados por coma): {Color.END}").strip()
            if not vlans_input_str:
                break
            try:
                vlans_list = validar_vlans_input(vlans_input_str)
                mostrar_mensaje(f"VLANs asignadas: {', '.join(map(str, vlans_list)) if vlans_list else 'Ninguna'}", "exito")
                break
            except ValueError as e:
                mostrar_mensaje(str(e), "error")
                vlans_list = []

    nuevo_disp = crear_dispositivo(tipo, nombre, ip_asignada, ubicacion_asignada, servicios_sel_list, vlans_list)

    if nuevo_disp:
        dispositivos_lista.append(nuevo_disp)
        guardar_dispositivos_en_archivo(dispositivos_lista) # <<< GUARDAR DATOS
        mostrar_mensaje(f"Dispositivo '{nombre}' agregado exitosamente!", "exito")
        mostrar_barra_progreso(1, "Guardando datos del dispositivo...", sufijo="¡Dispositivo guardado!")
    else:
        mostrar_mensaje("No se pudo agregar el dispositivo debido a errores previos.", "error"); sleep(2)

    pop_menu_history()();


def formatear_dispositivo_para_mostrar(disp_data, numero=None):
    partes = []
    if numero:
        partes.append(f"{Color.YELLOW}{numero}.{Color.END}")

    partes.append(f"{Color.CYAN}🔧 TIPO:{Color.END} {disp_data.get('TIPO', 'N/A')}")
    partes.append(f"{Color.CYAN}🏷️ NOMBRE:{Color.END} {disp_data.get('NOMBRE', 'N/A')}")
    partes.append(f"{Color.CYAN}🌍 IP:{Color.END} {disp_data.get('IP', 'N/A')}")
    partes.append(f"{Color.CYAN}📍 UBICACIÓN/CAPA:{Color.END} {disp_data.get('UBICACION', 'N/A')}") # Cambiado 'CAPA' a 'UBICACION'

    servicios_lista = disp_data.get('SERVICIOS', [])
    servicios_str = ", ".join(servicios_lista) if servicios_lista else "Ninguno"
    partes.append(f"{Color.CYAN}🛠️ SERVICIOS:{Color.END} {servicios_str}")

    vlans_lista = disp_data.get('VLANS', [])
    vlans_str = ", ".join(map(str, vlans_lista)) if vlans_lista else "Ninguna"
    partes.append(f"{Color.CYAN}🔗 VLANs:{Color.END} {vlans_str}")

    text_parts_for_width = []
    if numero: text_parts_for_width.append(f"{numero}.")
    text_parts_for_width.extend([
        f" TIPO: {disp_data.get('TIPO', 'N/A')}",
        f" NOMBRE: {disp_data.get('NOMBRE', 'N/A')}",
        f" IP: {disp_data.get('IP', 'N/A')}",
        f" UBICACIÓN/CAPA: {disp_data.get('UBICACION', 'N/A')}", # Cambiado
        f" SERVICIOS: {servicios_str}",
        f" VLANs: {vlans_str}"
    ])
    separador_ancho = max(70, max(len(p) for p in text_parts_for_width) + 4 if text_parts_for_width else 70)
    separador = f"{Color.BLUE}{'─' * separador_ancho}{Color.END}"
    return f"\n{separador}\n" + "\n".join(partes) + f"\n{separador}"


def mostrar_dispositivos(dispositivos_lista, titulo_menu="📜 MOSTRAR TODOS LOS DISPOSITIVOS"):
    current_menu_func = lambda: mostrar_dispositivos(dispositivos_lista, titulo_menu)
    push_menu_history(current_menu_func)
    mostrar_titulo(titulo_menu)
    if not dispositivos_lista:
        mostrar_mensaje("No hay dispositivos para mostrar.", "advertencia", esperar_enter=True)
        pop_menu_history()(); return

    for i, disp_data in enumerate(dispositivos_lista, 1):
        print(formatear_dispositivo_para_mostrar(disp_data, i))

    print(f"\n{Color.GREEN}Presione Enter o seleccione una opción de navegación para volver...{Color.END}")
    opcion = mostrar_opciones_navegacion(current_menu_func)
    if opcion is None: return
    elif opcion == "" or opcion.lower() == "enter":
        pop_menu_history()()
        return
    else:
        mostrar_mensaje("Volviendo al menú anterior...", "info"); sleep(1)
        pop_menu_history()()


def buscar_dispositivo(dispositivos_lista):
    current_menu_func = lambda: buscar_dispositivo(dispositivos_lista)
    push_menu_history(current_menu_func)
    mostrar_titulo("🔍 BUSCAR DISPOSITIVO")

    if not dispositivos_lista:
        mostrar_mensaje("No hay dispositivos para buscar.", "advertencia", esperar_enter=True)
        pop_menu_history()(); return

    nombre_buscar = input(f"{Color.GREEN}↳ Ingrese el nombre (o parte del nombre) a buscar (Enter para cancelar): {Color.END}").strip()
    if not nombre_buscar:
        mostrar_mensaje("Búsqueda cancelada.", "info"); sleep(1)
        pop_menu_history()(); return

    nombre_buscar_lower = nombre_buscar.lower()
    encontrados = [d for d in dispositivos_lista if nombre_buscar_lower in d.get("NOMBRE", "").lower()]

    if encontrados:
        mostrar_barra_progreso(0.5, "Buscando dispositivos...")
        # Llamar a una función que no reinicie el historial para la sub-vista de resultados
        _mostrar_resultados_busqueda(encontrados, f"✨ RESULTADOS DE BÚSQUEDA PARA '{nombre_buscar}'", current_menu_func)
    else:
        mostrar_mensaje(f"No se encontraron dispositivos con el nombre '{nombre_buscar}'.", "advertencia", esperar_enter=True)
        pop_menu_history()();

def _mostrar_resultados_busqueda(dispositivos_encontrados, titulo, menu_anterior_func):
    """Función auxiliar para mostrar resultados sin afectar tanto el historial principal."""
    mostrar_titulo(titulo)
    if not dispositivos_encontrados: # doble chequeo
        mostrar_mensaje("No hay dispositivos para mostrar.", "advertencia", esperar_enter=True)
        menu_anterior_func(); return # Vuelve al menú de búsqueda

    for i, disp_data in enumerate(dispositivos_encontrados, 1):
        print(formatear_dispositivo_para_mostrar(disp_data, i))

    print(f"\n{Color.GREEN}Presione Enter para volver a la búsqueda o 'm' para Menú Principal...{Color.END}")
    while True:
        opcion = input(f"{Color.GREEN}↳ Opción: {Color.END}").strip().lower()
        if opcion == "":
            menu_anterior_func(); return
        elif opcion == "m":
            ir_a_menu_principal(); return
        else:
            mostrar_mensaje("Opción inválida.", "error")


# <<< NUEVA FUNCIÓN PARA MODIFICAR DISPOSITIVO >>>
def modificar_dispositivo_interactivo(dispositivos_lista):
    current_menu_func = lambda: modificar_dispositivo_interactivo(dispositivos_lista)
    push_menu_history(current_menu_func)
    mostrar_titulo("✏️ MODIFICAR DISPOSITIVO")

    if not dispositivos_lista:
        mostrar_mensaje("No hay dispositivos para modificar.", "advertencia", esperar_enter=True)
        pop_menu_history()(); return

    print(f"{Color.BOLD}Seleccione el dispositivo a modificar:{Color.END}\n")
    for i, d in enumerate(dispositivos_lista, 1):
        print(f"{Color.YELLOW}{i}.{Color.END} {d.get('NOMBRE')} ({d.get('TIPO')})")
    print(f"{Color.YELLOW}0.{Color.END} Cancelar / Volver")

    try:
        num_in = input(f"\n{Color.GREEN}↳ Seleccione el número del dispositivo (0-{len(dispositivos_lista)}): {Color.END}").strip()
        if num_in == "0":
            mostrar_mensaje("Modificación cancelada.", "info"); sleep(1)
            pop_menu_history()(); return

        idx_sel = int(num_in) - 1
        if not (0 <= idx_sel < len(dispositivos_lista)):
            mostrar_mensaje("Número de dispositivo inválido.", "error"); sleep(2)
            # No salir del menú de modificar, permitir reintentar la selección del dispositivo
            # modificar_dispositivo_interactivo(dispositivos_lista) # Esto crea recursión, mejor bucle o re-llamar desde el menú principal
            return # Volverá a llamar al menú de modificar desde el bucle principal si es necesario

        disp_a_modificar = dispositivos_lista[idx_sel]
        nombre_original = disp_a_modificar.get("NOMBRE")
        modificado = False

        while True: # Bucle para modificar múltiples atributos del mismo dispositivo
            mostrar_titulo(f"✏️ MODIFICANDO: {nombre_original}")
            print(formatear_dispositivo_para_mostrar(disp_a_modificar))
            print(f"\n{Color.BOLD}¿Qué desea modificar?{Color.END}")
            print(f"{Color.YELLOW}1.{Color.END} Nombre")
            print(f"{Color.YELLOW}2.{Color.END} Dirección IP")
            print(f"{Color.YELLOW}3.{Color.END} Tipo de Dispositivo")
            print(f"{Color.YELLOW}4.{Color.END} Ubicación/Capa de Red")
            print(f"{Color.YELLOW}5.{Color.END} Servicios (Agregar/Eliminar)") # Combinar con agregar_servicio_a_dispositivo
            print(f"{Color.YELLOW}6.{Color.END} VLANs (Agregar/Eliminar)")
            print(f"{Color.YELLOW}0.{Color.END} Finalizar Modificación de este Dispositivo")

            op_mod = input(f"\n{Color.GREEN}↳ Seleccione una opción (0-6): {Color.END}").strip()

            if op_mod == "0":
                break # Salir del bucle de modificación de atributos

            elif op_mod == "1": # Modificar Nombre
                nuevo_nombre = ""
                while not nuevo_nombre:
                    temp_nombre = input(f"{Color.GREEN}↳ Nuevo nombre (Actual: {disp_a_modificar.get('NOMBRE', 'N/A')}, Enter para mantener): {Color.END}").strip()
                    if not temp_nombre: # Mantener actual
                        nuevo_nombre = disp_a_modificar.get('NOMBRE')
                        break
                    try:
                        validar_nombre(temp_nombre)
                        if temp_nombre.lower() != disp_a_modificar.get('NOMBRE','').lower() and \
                           any(d.get("NOMBRE","").lower() == temp_nombre.lower() for d in dispositivos_lista if d is not disp_a_modificar):
                            mostrar_mensaje(f"El nombre '{temp_nombre}' ya existe para otro dispositivo.", "advertencia")
                        else:
                            nuevo_nombre = temp_nombre
                            break
                    except ValueError as e:
                        mostrar_mensaje(str(e), "error")
                if nuevo_nombre != disp_a_modificar.get('NOMBRE'):
                    disp_a_modificar["NOMBRE"] = nuevo_nombre
                    modificado = True
                    nombre_original = nuevo_nombre # Actualizar para el título

            elif op_mod == "2": # Modificar IP
                nueva_ip = ingresar_ip_interactivo(dispositivos_lista, dispositivo_actual=disp_a_modificar)
                if nueva_ip is not None and nueva_ip != disp_a_modificar.get('IP'):
                    disp_a_modificar["IP"] = nueva_ip
                    modificado = True

            elif op_mod == "3": # Modificar Tipo
                nuevo_tipo = seleccionar_opcion_menu(TIPOS_DISPOSITIVO, "Seleccione el nuevo tipo:", "Tipo", permitir_cancelar=True, valor_actual=disp_a_modificar.get('TIPO'))
                if nuevo_tipo and nuevo_tipo != disp_a_modificar.get('TIPO'):
                    disp_a_modificar["TIPO"] = nuevo_tipo
                    modificado = True
                    # Podría ser necesario re-evaluar campos dependientes del tipo (ej. Servicios, Ubicación)
                    mostrar_mensaje("El tipo ha cambiado. Considere revisar Servicios y Ubicación/Capa.", "info")


            elif op_mod == "4": # Modificar Ubicación/Capa
                nueva_ubicacion = seleccionar_opcion_menu(CAPAS_RED, "Seleccione la nueva ubicación/capa:", "Ubicación/Capa", permitir_cancelar=True, valor_actual=disp_a_modificar.get('UBICACION'))
                if nueva_ubicacion is not None and nueva_ubicacion != disp_a_modificar.get('UBICACION'): # Si es None, usuario canceló
                     disp_a_modificar["UBICACION"] = nueva_ubicacion if nueva_ubicacion else "N/A" # Si cancela, puede querer N/A o mantener
                     modificado = True
                elif nueva_ubicacion is None and input(f"{Color.YELLOW}¿Desea establecer la ubicación como 'N/A'? (s/n, Enter para cancelar cambio): {Color.END}").lower() == 's':
                    disp_a_modificar["UBICACION"] = "N/A"
                    modificado = True


            elif op_mod == "5": # Modificar Servicios
                _modificar_servicios_para_dispositivo(disp_a_modificar, dispositivos_lista) # Llama a función auxiliar
                # La función auxiliar ya guarda si hay cambios
                modificado = True # Asumimos que pudo haber modificación

            elif op_mod == "6": # Modificar VLANs
                _modificar_vlans_para_dispositivo(disp_a_modificar, dispositivos_lista) # Llama a función auxiliar
                # La función auxiliar ya guarda si hay cambios
                modificado = True # Asumimos que pudo haber modificación

            else:
                mostrar_mensaje("Opción de modificación inválida.", "error"); sleep(1)

            if modificado: # Guardar después de cada cambio de atributo si se confirma el cambio
                guardar_dispositivos_en_archivo(dispositivos_lista)
                mostrar_mensaje(f"Atributo del dispositivo '{disp_a_modificar.get('NOMBRE')}' actualizado.", "exito")
                sleep(1) # Pequeña pausa para ver el mensaje
                # modificado = False # Resetear para la siguiente iteración del bucle de atributos

        if modificado: # Si hubo alguna modificación general al dispositivo.
            mostrar_barra_progreso(0.5, "Guardando cambios finales del dispositivo...")
            # El guardado ya se hizo dentro del bucle por atributo. Este es más un mensaje final.
            mostrar_mensaje(f"Dispositivo '{disp_a_modificar.get('NOMBRE')}' modificado exitosamente.", "exito")
        else:
            mostrar_mensaje("No se realizaron cambios en el dispositivo.", "info")
        sleep(1)

    except ValueError:
        mostrar_mensaje("Entrada numérica inválida para seleccionar dispositivo.", "error"); sleep(2)
    except Exception as e:
        mostrar_mensaje(f"Error inesperado durante la modificación: {e}", "error", esperar_enter=True)

    pop_menu_history()();
# <<< FIN NUEVA FUNCIÓN PARA MODIFICAR DISPOSITIVO >>>


def _modificar_servicios_para_dispositivo(disp_mod, dispositivos_lista_global):
    """Función auxiliar para gestionar servicios de un dispositivo específico."""
    tipo_key = next((k for k,v in TIPOS_DISPOSITIVO.items() if v == disp_mod.get("TIPO")), None)
    if tipo_key not in ['SERVIDOR', 'ROUTER', 'FIREWALL']:
        mostrar_mensaje(f"Los servicios no suelen aplicar directamente al tipo '{disp_mod.get('TIPO')}'.", "advertencia", esperar_enter=True)
        return False # No hubo cambios

    servicios_actuales = disp_mod.get("SERVICIOS", [])
    hubo_cambios = False

    while True:
        mostrar_titulo(f"MODIFICAR SERVICIOS DE: {disp_mod.get('NOMBRE')}")
        print(f"{Color.DARKCYAN}Servicios actuales: {', '.join(servicios_actuales) or 'Ninguno'}{Color.END}")
        print(f"{Color.YELLOW}1.{Color.END} Agregar servicio(s)")
        print(f"{Color.YELLOW}2.{Color.END} Eliminar servicio(s)")
        print(f"{Color.YELLOW}0.{Color.END} Finalizar modificación de servicios")
        op_serv = input(f"\n{Color.GREEN}↳ Opción: {Color.END}").strip()

        if op_serv == "0": break

        elif op_serv == "1": # Agregar
            print(f"\n{Color.BOLD}🛠️  Agregar nuevos servicios a '{disp_mod.get('NOMBRE')}':{Color.END}")
            servicios_opciones_list = list(SERVICIOS_VALIDOS.items())
            servicios_disponibles_para_agregar = {k:v for k,v in SERVICIOS_VALIDOS.items() if v not in servicios_actuales}

            if not servicios_disponibles_para_agregar:
                mostrar_mensaje("Todos los servicios válidos ya están asignados o no hay servicios definidos.", "info", esperar_enter=True)
                continue

            for i, (_, valor_mostrado) in enumerate(servicios_opciones_list, 1): # Mostrar todos para referencia
                 estado = f"{Color.GREEN}(Ya asignado){Color.END}" if SERVICIOS_VALIDOS.get(valor_mostrado.split(' ')[1].upper(), valor_mostrado) in servicios_actuales else "" # un poco complejo para sacar la key
                 # Mejor mostrar solo los que se pueden agregar
                 # print(f"{Color.YELLOW}{i}.{Color.END} {valor_mostrado} {estado}")

            print(f"{Color.BOLD}Servicios disponibles para agregar:{Color.END}")
            opciones_agregar_display = {k: v for k, v in SERVICIOS_VALIDOS.items() if v not in servicios_actuales}
            if not opciones_agregar_display:
                mostrar_mensaje("No hay más servicios disponibles para agregar.", "info", esperar_enter=True); continue

            idx = 1
            opciones_agregar_numeradas = {}
            for k_serv, v_serv in opciones_agregar_display.items():
                print(f"{Color.YELLOW}{idx}.{Color.END} {v_serv}")
                opciones_agregar_numeradas[str(idx)] = v_serv
                idx +=1

            servicios_input = input(f"{Color.GREEN}↳ Ingrese números de servicios a agregar (separados por coma, o Enter para cancelar): {Color.END}").strip()
            if not servicios_input: continue

            nuevos_servicios_temp = []
            numeros_servicios_str = servicios_input.split(',')
            valido = True
            for num_str in numeros_servicios_str:
                num_str = num_str.strip()
                if not num_str.isdigit() or num_str not in opciones_agregar_numeradas:
                    mostrar_mensaje(f"'{num_str}' no es un número de opción válido.", "error"); valido = False; break
                servicio_elegido_valor = opciones_agregar_numeradas[num_str]
                if servicio_elegido_valor not in servicios_actuales and servicio_elegido_valor not in nuevos_servicios_temp:
                    nuevos_servicios_temp.append(servicio_elegido_valor)
                else:
                    mostrar_mensaje(f"Servicio '{servicio_elegido_valor}' ya existe o ya fue agregado.", "advertencia")

            if valido and nuevos_servicios_temp:
                servicios_actuales.extend(nuevos_servicios_temp)
                disp_mod["SERVICIOS"] = sorted(list(set(servicios_actuales)))
                hubo_cambios = True
                mostrar_mensaje(f"Servicios {', '.join(nuevos_servicios_temp)} agregados.", "exito")

        elif op_serv == "2": # Eliminar
            if not servicios_actuales:
                mostrar_mensaje("No hay servicios asignados para eliminar.", "info", esperar_enter=True)
                continue

            print(f"\n{Color.BOLD}🗑️  Eliminar servicios de '{disp_mod.get('NOMBRE')}':{Color.END}")
            for i, serv in enumerate(servicios_actuales, 1):
                print(f"{Color.YELLOW}{i}.{Color.END} {serv}")

            servicios_input_del = input(f"{Color.GREEN}↳ Ingrese números de servicios a eliminar (separados por coma, o Enter para cancelar): {Color.END}").strip()
            if not servicios_input_del: continue

            servicios_a_eliminar_idx = []
            numeros_servicios_del_str = servicios_input_del.split(',')
            valido_del = True
            for num_str_del in numeros_servicios_del_str:
                num_str_del = num_str_del.strip()
                if not num_str_del.isdigit():
                    mostrar_mensaje(f"'{num_str_del}' no es un número válido.", "error"); valido_del = False; break
                idx_del = int(num_str_del) - 1
                if not (0 <= idx_del < len(servicios_actuales)):
                    mostrar_mensaje(f"Número de servicio '{num_str_del}' fuera de rango.", "error"); valido_del = False; break
                if idx_del not in servicios_a_eliminar_idx:
                    servicios_a_eliminar_idx.append(idx_del)

            if valido_del and servicios_a_eliminar_idx:
                servicios_eliminados_nombres = []
                # Eliminar en orden inverso de índice para no afectar los índices restantes
                for idx_to_remove in sorted(servicios_a_eliminar_idx, reverse=True):
                    servicios_eliminados_nombres.append(servicios_actuales.pop(idx_to_remove))
                disp_mod["SERVICIOS"] = sorted(list(set(servicios_actuales))) # Asegurar orden y unicidad
                hubo_cambios = True
                mostrar_mensaje(f"Servicios {', '.join(reversed(servicios_eliminados_nombres))} eliminados.", "exito")
        else:
            mostrar_mensaje("Opción inválida.", "error")

        if hubo_cambios:
            guardar_dispositivos_en_archivo(dispositivos_lista_global)
            sleep(1)
    return hubo_cambios


def _modificar_vlans_para_dispositivo(disp_mod, dispositivos_lista_global):
    """Función auxiliar para gestionar VLANs de un dispositivo específico."""
    vlans_actuales = disp_mod.get("VLANS", [])
    hubo_cambios_vlan = False

    while True:
        mostrar_titulo(f"MODIFICAR VLANS DE: {disp_mod.get('NOMBRE')}")
        print(f"{Color.DARKCYAN}VLANs actuales: {', '.join(map(str, vlans_actuales)) or 'Ninguna'}{Color.END}")
        print(f"{Color.YELLOW}1.{Color.END} Agregar VLAN(s)")
        print(f"{Color.YELLOW}2.{Color.END} Eliminar VLAN(s)")
        print(f"{Color.YELLOW}0.{Color.END} Finalizar modificación de VLANs")
        op_vlan = input(f"\n{Color.GREEN}↳ Opción: {Color.END}").strip()

        if op_vlan == "0": break

        elif op_vlan == "1": # Agregar VLANs
            print(f"\n{Color.BOLD}🔗 Agregar VLANs a '{disp_mod.get('NOMBRE')}':{Color.END}")
            print(f"{Color.DARKCYAN}Puede ingresar varias VLANs separadas por comas (ej: 10,20,30).{Color.END}")
            while True:
                vlans_input_str = input(f"{Color.GREEN}↳ Ingrese VLANs a agregar (1-4094, sep. por coma, Enter para cancelar): {Color.END}").strip()
                if not vlans_input_str: break
                try:
                    nuevas_vlans_list = validar_vlans_input(vlans_input_str) # Valida y convierte a int
                    vlans_realmente_nuevas = [v for v in nuevas_vlans_list if v not in vlans_actuales]

                    if vlans_realmente_nuevas:
                        vlans_actuales.extend(vlans_realmente_nuevas)
                        disp_mod["VLANS"] = sorted(list(set(vlans_actuales))) # Asegurar orden y unicidad
                        hubo_cambios_vlan = True
                        mostrar_mensaje(f"VLANs {', '.join(map(str, vlans_realmente_nuevas))} agregadas.", "exito")
                    elif nuevas_vlans_list: # Si ingresó VLANs pero ya existían todas
                        mostrar_mensaje("Todas las VLANs ingresadas ya están asignadas.", "info")
                    else: # Si no ingresó nada válido
                        mostrar_mensaje("No se ingresaron VLANs válidas para agregar.", "advertencia")
                    break # Salir del bucle de input de VLANs
                except ValueError as e:
                    mostrar_mensaje(str(e), "error") # Mostrar error de validación de VLANs

        elif op_vlan == "2": # Eliminar VLANs
            if not vlans_actuales:
                mostrar_mensaje("No hay VLANs asignadas para eliminar.", "info", esperar_enter=True)
                continue

            print(f"\n{Color.BOLD}🗑️  Eliminar VLANs de '{disp_mod.get('NOMBRE')}':{Color.END}")
            # Mostrar VLANs actuales con un número para facilitar la selección
            for i, vlan_val in enumerate(vlans_actuales, 1):
                print(f"{Color.YELLOW}{i}.{Color.END} VLAN {vlan_val}")

            vlans_input_del_str = input(f"{Color.GREEN}↳ Ingrese números de VLANs a eliminar (de la lista de arriba, sep. por coma, Enter para cancelar): {Color.END}").strip()
            if not vlans_input_del_str: continue

            indices_a_eliminar = []
            numeros_vlans_del_str = vlans_input_del_str.split(',')
            valido_del_vlan = True
            for num_str_del_vlan in numeros_vlans_del_str:
                num_str_del_vlan = num_str_del_vlan.strip()
                if not num_str_del_vlan.isdigit():
                    mostrar_mensaje(f"'{num_str_del_vlan}' no es un número de opción válido.", "error"); valido_del_vlan = False; break
                idx_vlan_del_opcion = int(num_str_del_vlan) - 1 # El usuario ingresa base 1
                if not (0 <= idx_vlan_del_opcion < len(vlans_actuales)):
                    mostrar_mensaje(f"Número de opción '{num_str_del_vlan}' fuera de rango.", "error"); valido_del_vlan = False; break
                # Convertir el índice de opción al valor real de la VLAN a eliminar
                vlan_a_remover = vlans_actuales[idx_vlan_del_opcion]
                if vlan_a_remover not in indices_a_eliminar: # Almacenar el valor de la VLAN, no el índice de opción
                    indices_a_eliminar.append(vlan_a_remover)


            if valido_del_vlan and indices_a_eliminar:
                vlans_original_copia = list(vlans_actuales) # Copia para iterar mientras se modifica la original
                vlans_eliminadas_nombres = []
                for vlan_val_to_remove in indices_a_eliminar: # Iterar sobre los valores de VLAN a remover
                    if vlan_val_to_remove in vlans_actuales:
                        vlans_actuales.remove(vlan_val_to_remove)
                        vlans_eliminadas_nombres.append(str(vlan_val_to_remove))

                if vlans_eliminadas_nombres:
                    disp_mod["VLANS"] = sorted(list(set(vlans_actuales))) # Asegurar orden y unicidad
                    hubo_cambios_vlan = True
                    mostrar_mensaje(f"VLANs {', '.join(vlans_eliminadas_nombres)} eliminadas.", "exito")
                else:
                    mostrar_mensaje("No se eliminaron VLANs (posiblemente ya no existían).", "info")
        else:
            mostrar_mensaje("Opción inválida.", "error")

        if hubo_cambios_vlan:
            guardar_dispositivos_en_archivo(dispositivos_lista_global)
            sleep(1)
    return hubo_cambios_vlan


def agregar_servicio_a_dispositivo(dispositivos_lista): # Esta función puede ser integrada o reemplazada por la de modificar
    # Por ahora la mantendré como la solicitó el script original, pero la nueva función modificar_dispositivo
    # ya incluye manejo de servicios. Esta función se vuelve un poco redundante.
    # Se podría llamar a _modificar_servicios_para_dispositivo desde aquí o refactorizar.

    current_menu_func = lambda: agregar_servicio_a_dispositivo(dispositivos_lista)
    push_menu_history(current_menu_func)
    mostrar_titulo("➕ AGREGAR/MODIFICAR SERVICIOS A DISPOSITIVO") # Título actualizado

    if not dispositivos_lista:
        mostrar_mensaje("No hay dispositivos para modificar.", "advertencia", esperar_enter=True)
        pop_menu_history()(); return

    modificables = []
    print(f"{Color.BOLD}Seleccione un dispositivo para gestionar sus servicios:{Color.END}\n")
    idx_display = 1
    for d in dispositivos_lista:
        tipo_key = next((k for k,v in TIPOS_DISPOSITIVO.items() if v == d.get("TIPO")), None)
        if tipo_key in ['SERVIDOR', 'ROUTER', 'FIREWALL']: # Solo estos son elegibles
            modificables.append(d)
            print(f"{Color.YELLOW}{idx_display}.{Color.END} {d.get('NOMBRE')} ({d.get('TIPO')}) - Servicios: {', '.join(d.get('SERVICIOS',[])) or 'Ninguno'}")
            idx_display += 1

    if not modificables:
        mostrar_mensaje("No hay dispositivos elegibles (Servidor, Router, Firewall) para gestionar servicios.", "advertencia", esperar_enter=True)
        pop_menu_history()(); return

    print(f"{Color.YELLOW}0.{Color.END} Cancelar / Volver")

    try:
        num_in = input(f"\n{Color.GREEN}↳ Seleccione el número del dispositivo (0-{len(modificables)}): {Color.END}").strip()
        if num_in == "0":
            mostrar_mensaje("Operación cancelada.", "info"); sleep(1)
            pop_menu_history()(); return

        idx_sel_mod_lista = int(num_in) - 1

        if 0 <= idx_sel_mod_lista < len(modificables):
            disp_mod_original = modificables[idx_sel_mod_lista]
            # Encontrar el índice original en la lista global para asegurar que se modifica el objeto correcto
            idx_orig_global = -1
            for i, original_disp_global in enumerate(dispositivos_lista):
                if original_disp_global is disp_mod_original: # Comparar por identidad de objeto
                    idx_orig_global = i
                    break
            
            if idx_orig_global == -1:
                mostrar_mensaje("Error interno: no se encontró el dispositivo original en la lista global.", "error", esperar_enter=True);
                pop_menu_history()(); return

            disp_a_gestionar_servicios = dispositivos_lista[idx_orig_global]

            if _modificar_servicios_para_dispositivo(disp_a_gestionar_servicios, dispositivos_lista):
                # _modificar_servicios_para_dispositivo ya guarda el archivo
                mostrar_mensaje(f"Gestión de servicios para '{disp_a_gestionar_servicios.get('NOMBRE')}' completada.", "exito")
            else:
                mostrar_mensaje(f"No se realizaron cambios en los servicios de '{disp_a_gestionar_servicios.get('NOMBRE')}'.", "info")
            sleep(1)

        else:
            mostrar_mensaje("Número de dispositivo inválido.", "error"); sleep(2)
    except ValueError:
        mostrar_mensaje("Entrada numérica inválida para seleccionar dispositivo.", "error"); sleep(2)
    except Exception as e:
        mostrar_mensaje(f"Error inesperado gestionando servicios: {e}", "error", esperar_enter=True)

    pop_menu_history()();


def eliminar_dispositivo(dispositivos_lista):
    current_menu_func = lambda: eliminar_dispositivo(dispositivos_lista)
    push_menu_history(current_menu_func)
    mostrar_titulo("❌ ELIMINAR DISPOSITIVO")

    if not dispositivos_lista:
        mostrar_mensaje("No hay dispositivos para eliminar.", "advertencia", esperar_enter=True)
        pop_menu_history()(); return

    for i, d in enumerate(dispositivos_lista, 1):
        print(f"{Color.YELLOW}{i}.{Color.END} {d.get('NOMBRE')} ({d.get('TIPO')})")
    print(f"{Color.YELLOW}0.{Color.END} Cancelar / Volver")

    try:
        num_in = input(f"\n{Color.GREEN}↳ Seleccione el número del dispositivo a eliminar (0-{len(dispositivos_lista)}): {Color.END}").strip()
        if num_in == "0":
            mostrar_mensaje("Eliminación cancelada.", "info"); sleep(1)
            pop_menu_history()(); return

        idx_sel = int(num_in) - 1
        if 0 <= idx_sel < len(dispositivos_lista):
            disp_elim = dispositivos_lista[idx_sel]
            nombre_elim = disp_elim.get("NOMBRE", "Desconocido")
            print(f"\n{Color.RED}{'⚠' * 30} ¡ADVERTENCIA! {'⚠' * 30}{Color.END}")
            confirmar = input(f"{Color.RED}{Color.BOLD}❓ ¿Está ABSOLUTAMENTE SEGURO de que desea eliminar el dispositivo '{nombre_elim}'? Esta acción es irreversible. (s/n): {Color.END}").lower()
            print(f"{Color.RED}{'⚠' * 70}{Color.END}")

            if confirmar == 's':
                del dispositivos_lista[idx_sel]
                guardar_dispositivos_en_archivo(dispositivos_lista) # <<< GUARDAR DATOS
                mostrar_mensaje(f"Dispositivo '{nombre_elim}' eliminado exitosamente.", "exito")
                mostrar_barra_progreso(1, "Eliminando dispositivo y guardando cambios...")
            elif confirmar == 'n':
                mostrar_mensaje("Eliminación cancelada por el usuario.", "info")
            else:
                mostrar_mensaje("Opción de confirmación inválida. Eliminación cancelada.", "advertencia")
        else:
            mostrar_mensaje(f"Número de dispositivo inválido. Debe ser entre 1 y {len(dispositivos_lista)} o 0.", "error")
    except ValueError:
        mostrar_mensaje("Entrada numérica inválida para seleccionar dispositivo.", "error")

    sleep(1)
    pop_menu_history()();


def generar_reporte_estadistico(dispositivos_lista):
    current_menu_func = lambda: generar_reporte_estadistico(dispositivos_lista)
    push_menu_history(current_menu_func)
    mostrar_titulo("📊 REPORTE ESTADÍSTICO DETALLADO")

    if not dispositivos_lista:
        mostrar_mensaje("⚠️ No hay dispositivos para generar un reporte.", "advertencia", True)
        pop_menu_history()(); return

    print(f"\n{Color.BOLD}{Color.PURPLE}📌 RESUMEN GENERAL{Color.END}")
    print(f"{Color.CYAN}Total dispositivos:{Color.END} {len(dispositivos_lista)}")
    print(f"{Color.CYAN}Reporte generado por:{Color.END} {current_user}")
    print(f"{Color.CYAN}Fecha y Hora:{Color.END} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    print(f"\n{Color.BOLD}{Color.PURPLE}🔢 DISTRIBUCIÓN POR TIPO DE DISPOSITIVO:{Color.END}")
    tipos_count = {}
    for d in dispositivos_lista:
        tipo = d.get("TIPO","N/A")
        tipos_count[tipo] = tipos_count.get(tipo,0)+1
    for tipo, cant in sorted(tipos_count.items(), key=lambda x:x[1], reverse=True):
        print(f"  {Color.YELLOW}{tipo}:{Color.END} {cant}")

    print(f"\n{Color.BOLD}{Color.PURPLE}📍 DISTRIBUCIÓN POR UBICACIÓN/CAPA DE RED:{Color.END}") # Cambiado
    ubicacion_count = {}
    for d in dispositivos_lista:
        ubicacion = d.get("UBICACION","N/A") # Cambiado
        if ubicacion != "N/A":
            ubicacion_count[ubicacion] = ubicacion_count.get(ubicacion,0)+1
    if ubicacion_count:
        for ubicacion_val, cant in sorted(ubicacion_count.items(), key=lambda x:x[1], reverse=True):
            print(f"  {Color.YELLOW}{ubicacion_val}:{Color.END} {cant}")
    else:
        print(f"  {Color.DARKCYAN}Ningún dispositivo tiene una ubicación/capa de red asignada.{Color.END}")


    print(f"\n{Color.BOLD}{Color.PURPLE}🛠️ SERVICIOS MÁS UTILIZADOS EN LA RED:{Color.END}")
    serv_count = {}
    for d in dispositivos_lista:
        servicios_lista_disp = d.get("SERVICIOS",[])
        if servicios_lista_disp:
            for s_tag in servicios_lista_disp:
                serv_count[s_tag] = serv_count.get(s_tag,0)+1

    if serv_count:
        for serv, cant in sorted(serv_count.items(), key=lambda x:x[1], reverse=True):
            print(f"  {Color.YELLOW}{serv}:{Color.END} {cant} dispositivos")
    else:
        print(f"  {Color.DARKCYAN}No hay servicios configurados en ningún dispositivo.{Color.END}")

    print(f"\n{Color.BOLD}{Color.PURPLE}🔗 USO DE VLANs EN LA RED:{Color.END}")
    vlan_usage_count = {}
    dispositivos_con_vlans = 0
    total_vlans_configuradas = 0
    for d in dispositivos_lista:
        vlans_lista_disp = d.get("VLANS", [])
        if vlans_lista_disp:
            dispositivos_con_vlans +=1
            total_vlans_configuradas += len(vlans_lista_disp)
            for vlan in vlans_lista_disp:
                vlan_usage_count[vlan] = vlan_usage_count.get(vlan, 0) + 1

    if vlan_usage_count:
        print(f"  {Color.CYAN}Total de dispositivos con VLANs configuradas:{Color.END} {dispositivos_con_vlans}")
        print(f"  {Color.CYAN}Número total de configuraciones de VLAN (instancias):{Color.END} {total_vlans_configuradas}")
        print(f"  {Color.CYAN}VLANs específicas más utilizadas (veces que aparece cada VLAN):{Color.END}")
        for vlan, cant in sorted(vlan_usage_count.items(), key=lambda x: (x[1], x[0]), reverse=True):
            print(f"    {Color.YELLOW}VLAN {vlan}:{Color.END} {cant} veces")
    else:
        print(f"  {Color.DARKCYAN}No hay VLANs configuradas en ningún dispositivo de la red.{Color.END}")

    print(f"\n{Color.BLUE}{'═' * 70}{Color.END}")
    input(f"{Color.GREEN}Presione Enter para volver al menú anterior...{Color.END}")
    pop_menu_history()();

def exportar_reporte_a_archivo(dispositivos_lista):
    current_menu_func = lambda: exportar_reporte_a_archivo(dispositivos_lista)
    push_menu_history(current_menu_func)
    mostrar_titulo("📁 EXPORTAR REPORTE A ARCHIVO")

    if not dispositivos_lista:
        mostrar_mensaje("⚠️ No hay dispositivos para exportar.", "advertencia", True)
        pop_menu_history()(); return

    directorio_reportes = "reportes"
    try:
        os.makedirs(directorio_reportes, exist_ok=True)
    except OSError as e:
        mostrar_mensaje(f"Error al crear el directorio '{directorio_reportes}': {e}", "error", True)
        pop_menu_history()(); return

    nombre_archivo = datetime.now().strftime("reporte_dispositivos_%Y-%m-%d_%H-%M-%S.txt")
    ruta_completa_archivo = os.path.join(directorio_reportes, nombre_archivo)

    try:
        with open(ruta_completa_archivo, 'w', encoding='utf-8') as f:
            f.write("═════════════════════════════════════════════════════════════════════════════\n")
            f.write(f"                REPORTE DE DISPOSITIVOS DE RED ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})\n")
            f.write(f"                Generado por: {current_user}\n")
            f.write("═════════════════════════════════════════════════════════════════════════════\n\n")

            if not dispositivos_lista:
                f.write("No hay dispositivos para reportar.\n")
            else:
                for i, disp in enumerate(dispositivos_lista, 1):
                    f.write(f"Dispositivo #{i}\n")
                    f.write(f"  Nombre: {disp.get('NOMBRE', 'N/A')}\n")
                    f.write(f"  IP: {disp.get('IP', 'N/A')}\n")
                    f.write(f"  Tipo: {disp.get('TIPO', 'N/A')}\n")
                    f.write(f"  Ubicación/Capa: {disp.get('UBICACION', 'N/A')}\n") # Cambiado 'CAPA' a 'UBICACION'

                    servicios_lista = disp.get('SERVICIOS', [])
                    servicios_str = ", ".join(servicios_lista) if servicios_lista else "Ninguno"
                    f.write(f"  Servicios: {servicios_str}\n")

                    vlans_lista = disp.get('VLANS', [])
                    vlans_str = ", ".join(map(str, vlans_lista)) if vlans_lista else "Ninguna"
                    f.write(f"  VLANs: {vlans_str}\n")
                    f.write("-------------------------------------------------------------------------------\n\n")

            f.write(f"\nTotal de dispositivos en el reporte: {len(dispositivos_lista)}\n")
            f.write("═════════════════════════════ FIN DEL REPORTE ═════════════════════════════\n")

        mostrar_mensaje(f"Reporte exportado exitosamente como '{ruta_completa_archivo}'", "exito", True)
    except IOError as e:
        mostrar_mensaje(f"Error al escribir el archivo de reporte '{ruta_completa_archivo}': {e}", "error", True)

    pop_menu_history()();


# 🎛️ Función principal y bucle de menú
def mostrar_menu_principal_opciones(dispositivos_lista):
    current_menu_func = lambda: mostrar_menu_principal_opciones(dispositivos_lista)
    mostrar_titulo("🚀 SISTEMA DE GESTIÓN DE DISPOSITIVOS DE RED 🚀")
    print(f"{Color.BOLD}{Color.YELLOW}1.{Color.END} 📱 Agregar Nuevo Dispositivo")
    print(f"{Color.BOLD}{Color.YELLOW}2.{Color.END} 📜 Mostrar Todos los Dispositivos")
    print(f"{Color.BOLD}{Color.YELLOW}3.{Color.END} 🔍 Buscar Dispositivo por Nombre")
    print(f"{Color.BOLD}{Color.YELLOW}4.{Color.END} ✏️ Modificar Dispositivo Existente") # <<< NUEVA OPCIÓN
    print(f"{Color.BOLD}{Color.YELLOW}5.{Color.END} ➕ Gestionar Servicios de Dispositivo") # Cambiado de "Agregar Servicio"
    print(f"{Color.BOLD}{Color.YELLOW}6.{Color.END} ❌ Eliminar Dispositivo")
    print(f"{Color.BOLD}{Color.YELLOW}7.{Color.END} 📊 Generar Reporte Estadístico Detallado")
    print(f"{Color.BOLD}{Color.YELLOW}8.{Color.END} 🌐 Probar Conectividad (Ping a Dispositivo)")
    print(f"{Color.BOLD}{Color.YELLOW}9.{Color.END} 📁 Exportar Listado de Dispositivos a Archivo") # Cambiado número
    print(f"{Color.BOLD}{Color.YELLOW}0.{Color.END} 🚪 Salir del Programa")


    opcion_elegida = mostrar_opciones_navegacion(current_menu_func, es_menu_principal=True)
    if opcion_elegida is None: return


    if opcion_elegida == "0": salir_del_programa()
    elif opcion_elegida == "1": mostrar_barra_progreso(0.5,"Cargando Agregar Dispositivo..."); agregar_dispositivo_interactivo(dispositivos_lista)
    elif opcion_elegida == "2": mostrar_barra_progreso(0.5,"Cargando Vista de Dispositivos..."); mostrar_dispositivos(dispositivos_lista)
    elif opcion_elegida == "3": mostrar_barra_progreso(0.5,"Iniciando Búsqueda..."); buscar_dispositivo(dispositivos_lista)
    elif opcion_elegida == "4": mostrar_barra_progreso(0.5,"Cargando Modificación de Dispositivo..."); modificar_dispositivo_interactivo(dispositivos_lista) # <<< LLAMADA A NUEVA FUNCIÓN
    elif opcion_elegida == "5": mostrar_barra_progreso(0.5,"Cargando Gestión de Servicios..."); agregar_servicio_a_dispositivo(dispositivos_lista) # Mantiene la función original, aunque redundante
    elif opcion_elegida == "6": mostrar_barra_progreso(0.5,"Cargando Eliminación de Dispositivo..."); eliminar_dispositivo(dispositivos_lista)
    elif opcion_elegida == "7": mostrar_barra_progreso(1,"Generando Reporte Estadístico..."); generar_reporte_estadistico(dispositivos_lista)
    elif opcion_elegida == "8": mostrar_barra_progreso(0.5,"Cargando Herramienta de Ping..."); menu_ping_dispositivo(dispositivos_lista)
    elif opcion_elegida == "9": mostrar_barra_progreso(0.5,"Exportando Reporte..."); exportar_reporte_a_archivo(dispositivos_lista)
    else:
        mostrar_mensaje(f"Opción '{opcion_elegida}' no válida. Seleccione entre 0-9 o una opción de navegación.", "error"); sleep(2)
        # No es necesario llamar recursivamente aquí, el bucle en main se encargará.
        # mostrar_menu_principal_opciones(dispositivos_lista) # Evitar recursión directa

def main():
    global menu_history
    # dispositivos = [] # <<< MODIFICADO: Cargar desde archivo
    dispositivos = cargar_dispositivos_desde_archivo() # <<< MODIFICADO
    sleep(1) # Pausa para ver mensaje de carga de datos

    limpiar_pantalla()
    print(f"\n{Color.BLUE}{'═' * 70}{Color.END}")
    print(f"{Color.BOLD}{Color.PURPLE}{'🛡️ BIENVENIDO AL SISTEMA AVANZADO DE GESTIÓN DE REDES 🛡️'.center(70)}{Color.END}")
    print(f"{Color.BLUE}{'═' * 70}{Color.END}")
    mostrar_barra_progreso(1.5, "Iniciando el sistema de gestión...", sufijo="¡Sistema listo para operar!")

    if not iniciar_sesion():
        return

    menu_principal_lambda = lambda: mostrar_menu_principal_opciones(dispositivos)
    menu_history = [menu_principal_lambda]

    while True:
        if menu_history:
            menu_actual = menu_history[-1]
            try:
                menu_actual()
            except Exception as e_menu: # Captura errores dentro de una función de menú
                mostrar_mensaje(f"Error inesperado en la función del menú: {e_menu}", "error", esperar_enter=True)
                import traceback
                with open("error_log_menu.txt", "a", encoding='utf-8') as f_error_menu:
                    f_error_menu.write(f"\n--- Error en Menú: {datetime.now()} ---\n")
                    f_error_menu.write(f"Menu function: {menu_actual.__name__ if hasattr(menu_actual, '__name__') else 'lambda'}\n")
                    traceback.print_exc(file=f_error_menu)
                # Volver al menú principal en caso de error grave en un submenú
                if menu_actual is not menu_principal_lambda: # Evitar bucle si el error es en el principal
                    ir_a_menu_principal()
                else: # Si el error es en el propio menú principal, intentar recargarlo
                     menu_principal_lambda()


        else: # Esto no debería ocurrir con la lógica actual
            mostrar_mensaje("Error crítico de navegación: historial de menú vacío. Reiniciando al menú principal.", "error", True)
            menu_history = [menu_principal_lambda]
            menu_principal_lambda()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        limpiar_pantalla()
        print(f"\n{Color.YELLOW}Interrupción por teclado detectada. Cerrando el programa...{Color.END}")
        sleep(1)
        mostrar_barra_progreso(0.5, "Finalizando...", sufijo="¡Programa cerrado de forma segura!")
        limpiar_pantalla()
        sys.exit(0)
    except Exception as e: # Captura errores no esperados a nivel global
        limpiar_pantalla()
        print(f"\n{Color.RED}{Color.BOLD}💥 ERROR INESPERADO Y CRÍTICO 💥{Color.END}")
        print(f"{Color.RED}Ha ocurrido un error no controlado que ha forzado la detención del programa.{Color.END}")
        print(f"{Color.RED}Detalles del error: {type(e).__name__} - {str(e)}{Color.END}")
        print(f"{Color.YELLOW}Por favor, reporte este error al desarrollador.{Color.END}")
        import traceback
        # Guardar log de errores
        error_log_filename = "error_log_global.txt"
        try:
            with open(error_log_filename, "a", encoding='utf-8') as f_error:
                f_error.write(f"\n--- Error Global: {datetime.now()} ---\n")
                traceback.print_exc(file=f_error)
            print(f"{Color.DARKCYAN}Se ha guardado un registro del error en '{error_log_filename}'.{Color.END}")
        except Exception as log_e:
            print(f"{Color.RED}No se pudo escribir en el archivo de log de errores '{error_log_filename}': {log_e}{Color.END}")

        input(f"\n{Color.GREEN}Presione Enter para salir...{Color.END}")
        sys.exit(1)
