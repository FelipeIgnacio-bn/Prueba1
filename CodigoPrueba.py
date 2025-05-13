import re
import os
import sys
import platform
import subprocess
from time import sleep
from datetime import datetime
import json # <<< NUEVO: Para guardar y cargar datos

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
DATA_FILE = "datos_red.json" # <<< NUEVO: Nombre del archivo para persistencia
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

# -------------------- PERSISTENCIA DE DATOS (NUEVO) --------------------
def cargar_datos():
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            datos = json.load(f)
            mostrar_mensaje(f"Datos cargados exitosamente desde '{DATA_FILE}'.", "info")
            return datos
    except FileNotFoundError:
        mostrar_mensaje(f"Archivo '{DATA_FILE}' no encontrado. Se iniciará con una lista vacía y se creará al guardar.", "advertencia")
        return []
    except json.JSONDecodeError:
        mostrar_mensaje(f"Error al leer '{DATA_FILE}'. El archivo podría estar corrupto. Se iniciará con una lista vacía.", "error")
        # Opcional: hacer una copia de seguridad del archivo corrupto
        # import shutil
        # shutil.copyfile(DATA_FILE, f"{DATA_FILE}.corrupt_{datetime.now().strftime('%Y%m%d%H%M%S')}")
        return []
    except Exception as e:
        mostrar_mensaje(f"Error inesperado al cargar datos: {e}", "error")
        return []

def guardar_datos(dispositivos_lista):
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(dispositivos_lista, f, indent=4, ensure_ascii=False)
        mostrar_mensaje(f"Datos guardados exitosamente en '{DATA_FILE}'.", "exito")
    except IOError as e:
        mostrar_mensaje(f"Error al guardar datos en '{DATA_FILE}': {e}", "error")
    except Exception as e:
        mostrar_mensaje(f"Error inesperado al guardar datos: {e}", "error")

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
CAPAS_RED = {'NUCLEO': '💎 Núcleo (Core)', 'DISTRIBUCION': '📦 Distribución', 'ACCESO': '🔌 Acceso'}

def validar_ip(ip):
    if not ip: return True
    if not re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', ip): raise ValueError("Formato incorrecto. Debe ser X.X.X.X")
    octetos = ip.split('.')
    if len(octetos) != 4: raise ValueError("La IP debe tener 4 octetos.")
    for octeto_str in octetos:
        if not (0 <= int(octeto_str) <= 255): raise ValueError(f"Octeto '{octeto_str}' fuera de rango (0-255).")
    if int(octetos[0]) == 0: raise ValueError("El primer octeto no puede ser 0.")
    if int(octetos[0]) == 127: raise ValueError("IP 127.x.x.x reservada para loopback.")
    if 224 <= int(octetos[0]) <= 239: raise ValueError("IPs 224.x.x.x a 239.x.x.x reservadas para multicast.")
    if int(octetos[0]) >= 240: raise ValueError("IPs 240.x.x.x y superiores reservadas.")
    if ip == "255.255.255.255": raise ValueError("IP 255.255.255.255 reservada para broadcast.")
    return True

def validar_nombre(nombre):
    if not re.match(r'^[a-zA-Z0-9\-\.\s_]+$', nombre): raise ValueError("Nombre con caracteres inválidos.")
    if not 3 <= len(nombre.strip()) <= 50: raise ValueError("Nombre debe tener entre 3 y 50 caracteres.")
    return True

def validar_servicios_lista(servicios_lista):
    for servicio in servicios_lista:
        if servicio not in SERVICIOS_VALIDOS.values(): raise ValueError(f"Servicio inválido: {servicio}")
    return True

def validar_vlans_input(vlans_str):
    if not vlans_str.strip(): return []
    vlan_list_str = vlans_str.split(',')
    vlans_int = []
    for v_str in vlan_list_str:
        v_str = v_str.strip()
        if not v_str.isdigit(): raise ValueError(f"VLAN '{v_str}' no es un número.")
        v_int = int(v_str)
        if not (1 <= v_int <= 4094): raise ValueError(f"VLAN '{v_int}' fuera de rango (1-4094).")
        if v_int not in vlans_int: vlans_int.append(v_int)
        else: mostrar_mensaje(f"VLAN '{v_int}' duplicada, se omitirá.", "advertencia")
    return sorted(list(set(vlans_int)))

def crear_dispositivo(tipo, nombre, ip=None, capa=None, servicios=None, vlans=None):
    try:
        validar_nombre(nombre)
        if ip and ip != "N/A": validar_ip(ip)
        if servicios: validar_servicios_lista(servicios)
        return {"TIPO": tipo, "NOMBRE": nombre, "IP": ip or "N/A", "CAPA": capa or "N/A", "SERVICIOS": servicios or [], "VLANS": vlans or []}
    except ValueError as e:
        mostrar_mensaje(f"Error al definir datos: {e}", "error"); return None

# ---------------- FUNCIONES DE MENÚ Y NAVEGACIÓN ----------------
def push_menu_history(menu_function): menu_history.append(menu_function)
def pop_menu_history():
    if len(menu_history) > 1: menu_history.pop()
    return menu_history[-1] if menu_history else None

def ir_a_menu_principal():
    global menu_history
    if menu_history:
        menu_principal_func = menu_history[0]
        menu_history = [menu_principal_func]
        mostrar_barra_progreso(0.5, "Volviendo al Menú Principal...")
        menu_principal_func()
    else: main()

def salir_del_programa():
    mostrar_titulo("SALIR DEL PROGRAMA")
    if input(f"{Color.YELLOW}❓ ¿Está seguro (s/n)?: {Color.END}").lower() == 's':
        mostrar_barra_progreso(1, "Cerrando...", sufijo="¡Hasta pronto! 👋")
        limpiar_pantalla(); sys.exit()
    else:
        mostrar_mensaje("Operación cancelada.", "info"); sleep(1)
        if menu_history: menu_history[-1]()
        else: main()

def mostrar_opciones_navegacion(menu_actual_func, es_menu_principal=False):
    print(f"\n{Color.BLUE}{'─' * 70}{Color.END}")
    opciones_nav_display = []
    if not es_menu_principal and len(menu_history) > 1:
        opciones_nav_display.append(f"{Color.YELLOW}b. ⬅️ Volver Menú Anterior{Color.END}")
    if not es_menu_principal:
        opciones_nav_display.append(f"{Color.YELLOW}m. 🏠 Menú Principal{Color.END}")
    opciones_nav_display.append(f"{Color.YELLOW}s. 🚪 Salir{Color.END}")

    for texto in opciones_nav_display: print(texto)
    print(f"{Color.BLUE}{'─' * 70}{Color.END}")

    prompt_texto = "↳ Seleccione opción del menú"
    if opciones_nav_display: prompt_texto += f" o navegación ({', '.join(k[0] for k in opciones_nav_display if k.startswith(Color.YELLOW)).replace(Color.YELLOW, '').replace(Color.END, '').replace('. ', '').split(' ')[0]})"
    
    opcion_input = input(f"{Color.GREEN}{prompt_texto}: {Color.END}").strip().lower()

    if opcion_input == 'b' and not es_menu_principal and len(menu_history) > 1:
        dest = pop_menu_history()
        if dest: mostrar_barra_progreso(0.5, "Volviendo..."); dest(); return None
    elif opcion_input == 'm' and not es_menu_principal:
        ir_a_menu_principal(); return None
    elif opcion_input == 's':
        salir_del_programa(); return None
    return opcion_input

# ------------------- FUNCIONALIDAD DE PING (MEJORADA) -------------------
def hacer_ping(ip_address):
    if not ip_address or ip_address == "N/A":
        mostrar_mensaje("Este dispositivo no tiene una IP asignada para hacer ping.", "advertencia", esperar_enter=True)
        return
    param_conteo = '-n' if platform.system().lower() == 'windows' else '-c'
    comando = ['ping', param_conteo, '4', ip_address]
    mostrar_titulo(f"PING A {ip_address}")
    print(f"{Color.CYAN}Ejecutando: {' '.join(comando)}{Color.END}\n{Color.YELLOW}Enviando paquetes (timeout 10s)...{Color.END}\n")
    try:
        resultado_proceso = subprocess.run(comando, capture_output=True, text=True, timeout=10, check=False, errors='replace')
        print(f"{Color.BLUE}{'-'*30} INICIO SALIDA PING {'-'*30}{Color.END}")
        if resultado_proceso.stdout: print(f"{Color.DARKCYAN}Salida Estándar:{Color.END}\n{resultado_proceso.stdout}")
        if resultado_proceso.stderr: print(f"{Color.RED}Salida de Error:{Color.END}\n{resultado_proceso.stderr}")
        print(f"{Color.BLUE}{'-'*31} FIN SALIDA PING {'-'*31}{Color.END}\n")
        if resultado_proceso.returncode == 0:
            fallo_logico = False
            if platform.system().lower() != 'windows':
                if "0 received" in resultado_proceso.stdout or "100% packet loss" in resultado_proceso.stdout.lower(): fallo_logico = True
            elif 'ttl=' not in resultado_proceso.stdout.lower(): # Heurística para Windows si no hay TTL
                if any(err_msg in resultado_proceso.stdout.lower() for err_msg in ["inaccesible", "unreachable", "timed out", "tiempo de espera agotado"]) or \
                   re.search(r"(perdidos|Lost)\s*=\s*4\s*\(100%\s*(pérdida|loss)\)", resultado_proceso.stdout):
                    fallo_logico = True
            if fallo_logico: mostrar_mensaje(f"⚠️ PING a {ip_address} PARECE HABER FALLADO (sin respuesta o pérdida total).", "advertencia")
            else: mostrar_mensaje(f"✅ PING a {ip_address} EXITOSO.", "exito")
        else: mostrar_mensaje(f"❌ PING a {ip_address} FALLIDO (código de error del sistema: {resultado_proceso.returncode}).", "error")
    except subprocess.TimeoutExpired: mostrar_mensaje(f"❌ PING a {ip_address} FALLIDO: Tiempo de espera agotado.", "error")
    except FileNotFoundError: mostrar_mensaje("❌ Error Crítico: Comando 'ping' no encontrado.", "error")
    except Exception as e: mostrar_mensaje(f"❌ Error inesperado en ping: {e}", "error")
    input(f"{Color.GREEN}Presione Enter para continuar...{Color.END}")

def menu_ping_dispositivo(dispositivos_lista):
    current_menu_func = lambda: menu_ping_dispositivo(dispositivos_lista)
    push_menu_history(current_menu_func)
    while True:
        mostrar_titulo("🌐 PROBAR CONECTIVIDAD (PING)")
        dispositivos_con_ip = [d for d in dispositivos_lista if d.get("IP") and d.get("IP") != "N/A"]
        if not dispositivos_con_ip:
            mostrar_mensaje("No hay dispositivos con IPs para hacer ping.", "advertencia", True); pop_menu_history()(); return
        print(f"{Color.BOLD}Seleccione un dispositivo para PING:{Color.END}")
        for i, d in enumerate(dispositivos_con_ip, 1): print(f"{Color.YELLOW}{i}.{Color.END} {d.get('NOMBRE')} ({d.get('IP')})")
        opcion = mostrar_opciones_navegacion(current_menu_func)
        if opcion is None: return
        try:
            opcion_num = int(opcion)
            if 1 <= opcion_num <= len(dispositivos_con_ip): hacer_ping(dispositivos_con_ip[opcion_num - 1].get("IP"))
            else: mostrar_mensaje("Opción inválida.", "error"); sleep(2)
        except ValueError: mostrar_mensaje("Entrada inválida.", "error"); sleep(2)

# ---------------- FUNCIONES DE GESTIÓN DE DISPOSITIVOS ----------------
def seleccionar_opcion_menu(opciones_dict, titulo_seleccion, prompt_usuario, permitir_cancelar=False):
    print(f"\n{Color.BOLD}{titulo_seleccion}{Color.END}")
    opciones_list = list(opciones_dict.items())
    for i, (_, valor_mostrado) in enumerate(opciones_list, 1): print(f"{Color.YELLOW}{i}.{Color.END} {valor_mostrado}")
    if permitir_cancelar: print(f"{Color.YELLOW}0.{Color.END} Cancelar / Volver")
    while True:
        try:
            op_input = input(f"\n{Color.GREEN}↳ {prompt_usuario} (1-{len(opciones_list)}{', 0' if permitir_cancelar else ''}): {Color.END}").strip()
            if permitir_cancelar and op_input == "0": return None
            op_num = int(op_input)
            if 1 <= op_num <= len(opciones_list): return opciones_list[op_num-1][1]
            else: mostrar_mensaje(f"Opción fuera de rango.", "error")
        except ValueError: mostrar_mensaje("Entrada numérica inválida.", "error")

def ingresar_ip_interactivo(dispositivos_lista, dispositivo_actual=None):
    while True:
        ip = input(f"{Color.GREEN}↳ IP del dispositivo (Enter si no aplica): {Color.END}").strip()
        if not ip: return "N/A"
        try:
            validar_ip(ip)
            # Verificar duplicados, excluyendo el dispositivo actual si se está editando
            for disp in dispositivos_lista:
                if disp is dispositivo_actual: continue # No comparar consigo mismo
                if disp.get("IP") == ip and ip != "N/A":
                    raise ValueError(f"IP '{ip}' ya asignada a '{disp.get('NOMBRE')}'.")
            return ip
        except ValueError as e:
            mostrar_mensaje(str(e), "error")
            if "Formato" in str(e) or "Octeto" in str(e): print(f"{Color.YELLOW}💡 Ej: 192.168.1.10{Color.END}")

def agregar_dispositivo_interactivo(dispositivos_lista):
    current_menu_func = lambda: agregar_dispositivo_interactivo(dispositivos_lista)
    push_menu_history(current_menu_func)
    mostrar_titulo("📱 AGREGAR NUEVO DISPOSITIVO")
    tipo = seleccionar_opcion_menu(TIPOS_DISPOSITIVO, "Tipo de dispositivo:", "Tipo", True)
    if tipo is None: pop_menu_history()(); return
    nombre = ""
    while not nombre:
        temp_nombre = input(f"{Color.GREEN}↳ Nombre (3-50 caract.): {Color.END}").strip()
        try:
            validar_nombre(temp_nombre)
            if any(d.get("NOMBRE","").lower() == temp_nombre.lower() for d in dispositivos_lista):
                mostrar_mensaje(f"Nombre '{temp_nombre}' ya existe.", "advertencia")
            else: nombre = temp_nombre
        except ValueError as e: mostrar_mensaje(str(e), "error")
    ip_asignada = "N/A"
    tipo_key = next((k for k, v in TIPOS_DISPOSITIVO.items() if v == tipo), None)
    if tipo_key in ['SERVIDOR', 'ROUTER', 'FIREWALL', 'PC', 'IMPRESORA']:
        ip_asignada = ingresar_ip_interactivo(dispositivos_lista)
        if ip_asignada is None: pop_menu_history()(); return
    capa = "N/A"
    if tipo_key in ['ROUTER', 'SWITCH']:
        capa_sel = seleccionar_opcion_menu(CAPAS_RED, "Capa de red:", "Capa", True)
        if capa_sel is None: mostrar_mensaje("Capa no asignada.", "info"); sleep(1)
        else: capa = capa_sel
    servicios_sel_list = []
    if tipo_key in ['SERVIDOR', 'ROUTER', 'FIREWALL']:
        print(f"\n{Color.BOLD}🛠️ Servicios para '{nombre}':{Color.END} (ej: 1,3 o Enter para omitir)")
        for i, (_, v) in enumerate(list(SERVICIOS_VALIDOS.items()), 1): print(f"{Color.YELLOW}{i}.{Color.END} {v}")
        while True:
            s_input = input(f"{Color.GREEN}↳ Números de servicios: {Color.END}").strip()
            if not s_input: break
            s_temp = []; valido = True
            for num_str in s_input.split(','):
                try:
                    num_int = int(num_str.strip())
                    if 1 <= num_int <= len(SERVICIOS_VALIDOS):
                        s_val = list(SERVICIOS_VALIDOS.values())[num_int - 1]
                        if s_val not in s_temp: s_temp.append(s_val)
                        else: mostrar_mensaje(f"Servicio '{s_val}' duplicado.", "advertencia")
                    else: raise ValueError("Número fuera de rango.")
                except ValueError: mostrar_mensaje(f"'{num_str}' no es válido.", "error"); valido = False; break
            if valido: servicios_sel_list = sorted(list(set(s_temp))); mostrar_mensaje(f"Servicios: {', '.join(servicios_sel_list) or 'Ninguno'}", "exito"); break
            else: servicios_sel_list = []
    vlans_list = []
    print(f"\n{Color.BOLD}🔗 VLANs para '{nombre}':{Color.END} (ej: 10,20 o Enter para omitir)")
    while True:
        v_input = input(f"{Color.GREEN}↳ VLANs (1-4094): {Color.END}").strip()
        if not v_input: break
        try: vlans_list = validar_vlans_input(v_input); mostrar_mensaje(f"VLANs: {', '.join(map(str, vlans_list)) or 'Ninguna'}", "exito"); break
        except ValueError as e: mostrar_mensaje(str(e), "error"); vlans_list = []
    nuevo_disp = crear_dispositivo(tipo, nombre, ip_asignada, capa, servicios_sel_list, vlans_list)
    if nuevo_disp:
        dispositivos_lista.append(nuevo_disp)
        guardar_datos(dispositivos_lista) # <<< GUARDAR DATOS
        mostrar_mensaje(f"Dispositivo '{nombre}' agregado.", "exito")
        mostrar_barra_progreso(1, "Guardando...", sufijo="¡Guardado!")
    else: mostrar_mensaje("No se agregó el dispositivo.", "error"); sleep(2)
    pop_menu_history()();

def formatear_dispositivo_para_mostrar(disp_data, numero=None):
    partes = []
    if numero: partes.append(f"{Color.YELLOW}{numero}.{Color.END}")
    partes.append(f"{Color.CYAN}🔧 TIPO:{Color.END} {disp_data.get('TIPO', 'N/A')}")
    partes.append(f"{Color.CYAN}🏷️ NOMBRE:{Color.END} {disp_data.get('NOMBRE', 'N/A')}")
    partes.append(f"{Color.CYAN}🌍 IP:{Color.END} {disp_data.get('IP', 'N/A')}")
    partes.append(f"{Color.CYAN}📊 CAPA:{Color.END} {disp_data.get('CAPA', 'N/A')}")
    s_str = ", ".join(disp_data.get('SERVICIOS', [])) or "Ninguno"
    partes.append(f"{Color.CYAN}🛠️ SERVICIOS:{Color.END} {s_str}")
    v_str = ", ".join(map(str, disp_data.get('VLANS', []))) or "Ninguna"
    partes.append(f"{Color.CYAN}🔗 VLANs:{Color.END} {v_str}")
    clean_parts = [re.sub(r'\033\[.*?m', '', p) for p in partes]
    s_ancho = max(70, max(len(p) for p in clean_parts) + 4 if clean_parts else 70)
    sep = f"{Color.BLUE}{'─' * s_ancho}{Color.END}"
    return f"\n{sep}\n" + "\n".join(partes) + f"\n{sep}"

def mostrar_dispositivos(dispositivos_lista, titulo_menu="📜 MOSTRAR TODOS LOS DISPOSITIVOS"):
    current_menu_func = lambda: mostrar_dispositivos(dispositivos_lista, titulo_menu)
    push_menu_history(current_menu_func)
    mostrar_titulo(titulo_menu)
    if not dispositivos_lista:
        mostrar_mensaje("No hay dispositivos para mostrar.", "advertencia", True); pop_menu_history()(); return
    for i, disp_data in enumerate(dispositivos_lista, 1): print(formatear_dispositivo_para_mostrar(disp_data, i))
    print(f"\n{Color.GREEN}Enter o navegación para volver...{Color.END}")
    opcion = mostrar_opciones_navegacion(current_menu_func)
    if opcion is None or opcion == "" or opcion.lower() == "enter": pop_menu_history()(); return
    else: mostrar_mensaje("Volviendo...", "info"); sleep(1); pop_menu_history()()

def buscar_dispositivo(dispositivos_lista):
    current_menu_func = lambda: buscar_dispositivo(dispositivos_lista)
    push_menu_history(current_menu_func)
    mostrar_titulo("🔍 BUSCAR DISPOSITIVO")
    if not dispositivos_lista:
        mostrar_mensaje("No hay dispositivos para buscar.", "advertencia", True); pop_menu_history()(); return
    nombre_buscar = input(f"{Color.GREEN}↳ Nombre a buscar (Enter cancela): {Color.END}").strip()
    if not nombre_buscar: mostrar_mensaje("Búsqueda cancelada.", "info"); sleep(1); pop_menu_history()(); return
    encontrados = [d for d in dispositivos_lista if nombre_buscar.lower() in d.get("NOMBRE", "").lower()]
    if encontrados:
        mostrar_barra_progreso(0.5, "Buscando...")
        mostrar_dispositivos(encontrados, f"✨ RESULTADOS PARA '{nombre_buscar}'")
    else:
        mostrar_mensaje(f"No se encontraron dispositivos con '{nombre_buscar}'.", "advertencia", True)
        pop_menu_history()();

def agregar_servicio_a_dispositivo(dispositivos_lista):
    current_menu_func = lambda: agregar_servicio_a_dispositivo(dispositivos_lista)
    push_menu_history(current_menu_func)
    mostrar_titulo("➕ AGREGAR SERVICIO A DISPOSITIVO")
    if not dispositivos_lista:
        mostrar_mensaje("No hay dispositivos.", "advertencia", True); pop_menu_history()(); return
    modificables = [d for d in dispositivos_lista if d.get("TIPO") in [TIPOS_DISPOSITIVO['SERVIDOR'], TIPOS_DISPOSITIVO['ROUTER'], TIPOS_DISPOSITIVO['FIREWALL']]]
    if not modificables:
        mostrar_mensaje("No hay dispositivos elegibles (Servidor, Router, Firewall).", "advertencia", True); pop_menu_history()(); return
    print(f"{Color.BOLD}Seleccione dispositivo a modificar:{Color.END}\n")
    for i, d in enumerate(modificables, 1): print(f"{Color.YELLOW}{i}.{Color.END} {d.get('NOMBRE')} ({d.get('TIPO')}) - Servicios: {', '.join(d.get('SERVICIOS',[])) or 'Ninguno'}")
    print(f"{Color.YELLOW}0.{Color.END} Cancelar")
    try:
        num_in = input(f"\n{Color.GREEN}↳ Dispositivo (0-{len(modificables)}): {Color.END}").strip()
        if num_in == "0": mostrar_mensaje("Cancelado.", "info"); sleep(1); pop_menu_history()(); return
        idx_sel_mod = int(num_in) - 1
        if 0 <= idx_sel_mod < len(modificables):
            disp_mod = modificables[idx_sel_mod]
            idx_orig = dispositivos_lista.index(disp_mod) # Encontrar índice en la lista original
            mostrar_mensaje(f"Modificando: {Color.BOLD}{disp_mod.get('NOMBRE')}{Color.END}", "info")
            print(f"\n{Color.BOLD}🛠️ Agregar servicios a '{disp_mod.get('NOMBRE')}':{Color.END} (ej: 1,3 o Enter para finalizar)")
            s_actuales = disp_mod.get('SERVICIOS', [])
            print(f"{Color.DARKCYAN}Actuales: {', '.join(s_actuales) or 'Ninguno'}{Color.END}")
            s_opts = list(SERVICIOS_VALIDOS.items())
            for i, (_, v) in enumerate(s_opts, 1): print(f"{Color.YELLOW}{i}.{Color.END} {v}")
            while True:
                s_input = input(f"{Color.GREEN}↳ Servicios a agregar: {Color.END}").strip()
                if not s_input: break
                nuevos_s_temp = [] ; valido = True
                for num_str in s_input.split(','):
                    try:
                        num_int = int(num_str.strip())
                        if not (1 <= num_int <= len(s_opts)): raise ValueError("Fuera de rango.")
                        s_val = s_opts[num_int-1][1]
                        if s_val not in s_actuales and s_val not in nuevos_s_temp: nuevos_s_temp.append(s_val)
                        else: mostrar_mensaje(f"Servicio '{s_val}' ya existe o duplicado.", "advertencia")
                    except ValueError: mostrar_mensaje(f"'{num_str}' no es válido.", "error"); valido = False; break
                if valido and nuevos_s_temp:
                    dispositivos_lista[idx_orig]["SERVICIOS"].extend(nuevos_s_temp)
                    dispositivos_lista[idx_orig]["SERVICIOS"] = sorted(list(set(dispositivos_lista[idx_orig]["SERVICIOS"])))
                    guardar_datos(dispositivos_lista) # <<< GUARDAR DATOS
                    mostrar_mensaje(f"Servicios agregados a '{disp_mod.get('NOMBRE')}'.", "exito")
                    mostrar_barra_progreso(0.5, "Actualizando...")
                    s_actuales = dispositivos_lista[idx_orig]["SERVICIOS"] # Actualizar para próxima iteración
                    if input(f"{Color.GREEN}¿Agregar más a este dispositivo? (s/n): {Color.END}").lower() != 's': break
                elif valido and not nuevos_s_temp: mostrar_mensaje("No se seleccionaron servicios nuevos.", "info")
        else: mostrar_mensaje("Número inválido.", "error"); sleep(2)
    except ValueError: mostrar_mensaje("Entrada numérica inválida.", "error"); sleep(2)
    pop_menu_history()();

def eliminar_dispositivo(dispositivos_lista):
    current_menu_func = lambda: eliminar_dispositivo(dispositivos_lista)
    push_menu_history(current_menu_func)
    mostrar_titulo("❌ ELIMINAR DISPOSITIVO")
    if not dispositivos_lista:
        mostrar_mensaje("No hay dispositivos para eliminar.", "advertencia", True); pop_menu_history()(); return
    for i, d in enumerate(dispositivos_lista, 1): print(f"{Color.YELLOW}{i}.{Color.END} {d.get('NOMBRE')} ({d.get('TIPO')})")
    print(f"{Color.YELLOW}0.{Color.END} Cancelar")
    try:
        num_in = input(f"\n{Color.GREEN}↳ Dispositivo a eliminar (0-{len(dispositivos_lista)}): {Color.END}").strip()
        if num_in == "0": mostrar_mensaje("Cancelado.", "info"); sleep(1); pop_menu_history()(); return
        idx_sel = int(num_in) - 1
        if 0 <= idx_sel < len(dispositivos_lista):
            nombre_elim = dispositivos_lista[idx_sel].get("NOMBRE", "Desconocido")
            print(f"\n{Color.RED}{'⚠' * 30} ¡ADVERTENCIA! {'⚠' * 30}{Color.END}")
            if input(f"{Color.RED}{Color.BOLD}❓ ¿Seguro que desea eliminar '{nombre_elim}'? (s/n): {Color.END}").lower() == 's':
                print(f"{Color.RED}{'⚠' * 70}{Color.END}")
                del dispositivos_lista[idx_sel]
                guardar_datos(dispositivos_lista) # <<< GUARDAR DATOS
                mostrar_mensaje(f"Dispositivo '{nombre_elim}' eliminado.", "exito")
                mostrar_barra_progreso(1, "Eliminando...")
            else: mostrar_mensaje("Eliminación cancelada.", "info")
        else: mostrar_mensaje("Número inválido.", "error")
    except ValueError: mostrar_mensaje("Entrada numérica inválida.", "error")
    sleep(1); pop_menu_history()();

def generar_reporte_estadistico(dispositivos_lista):
    current_menu_func = lambda: generar_reporte_estadistico(dispositivos_lista)
    push_menu_history(current_menu_func)
    mostrar_titulo("📊 REPORTE ESTADÍSTICO DETALLADO")
    if not dispositivos_lista:
        mostrar_mensaje("⚠️ No hay dispositivos para generar reporte.", "advertencia", True); pop_menu_history()(); return
    print(f"\n{Color.BOLD}{Color.PURPLE}📌 RESUMEN GENERAL{Color.END}")
    print(f"{Color.CYAN}Total dispositivos:{Color.END} {len(dispositivos_lista)}")
    print(f"{Color.CYAN}Reporte generado por:{Color.END} {current_user}")
    print(f"{Color.CYAN}Fecha y Hora:{Color.END} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    tipos_count = {}
    for d in dispositivos_lista: t = d.get("TIPO","N/A"); tipos_count[t] = tipos_count.get(t,0)+1
    print(f"\n{Color.BOLD}{Color.PURPLE}🔢 POR TIPO DE DISPOSITIVO:{Color.END}")
    for t, c in sorted(tipos_count.items(), key=lambda x:x[1], reverse=True): print(f"  {Color.YELLOW}{t}:{Color.END} {c}")
    capas_count = {}
    for d in dispositivos_lista: c = d.get("CAPA","N/A"); if c != "N/A": capas_count[c] = capas_count.get(c,0)+1
    print(f"\n{Color.BOLD}{Color.PURPLE}📡 POR CAPA DE RED:{Color.END}")
    if capas_count:
        for c, ct in sorted(capas_count.items(), key=lambda x:x[1], reverse=True): print(f"  {Color.YELLOW}{c}:{Color.END} {ct}")
    else: print(f"  {Color.DARKCYAN}Ningún dispositivo con capa asignada.{Color.END}")
    serv_count = {}
    for d in dispositivos_lista:
        for s_tag in d.get("SERVICIOS",[]): serv_count[s_tag] = serv_count.get(s_tag,0)+1
    print(f"\n{Color.BOLD}{Color.PURPLE}🛠️ SERVICIOS MÁS UTILIZADOS:{Color.END}")
    if serv_count:
        for s, ct in sorted(serv_count.items(), key=lambda x:x[1], reverse=True): print(f"  {Color.YELLOW}{s}:{Color.END} {ct} dispositivos")
    else: print(f"  {Color.DARKCYAN}No hay servicios configurados.{Color.END}")
    vlan_usage = {}; d_con_v = 0; total_v_conf = 0
    for d in dispositivos_lista:
        vl = d.get("VLANS", [])
        if vl: d_con_v +=1; total_v_conf += len(vl)
        for v_id in vl: vlan_usage[v_id] = vlan_usage.get(v_id, 0) + 1
    print(f"\n{Color.BOLD}{Color.PURPLE}🔗 USO DE VLANs:{Color.END}")
    if vlan_usage:
        print(f"  {Color.CYAN}Dispositivos con VLANs:{Color.END} {d_con_v}")
        print(f"  {Color.CYAN}Total configuraciones VLAN:{Color.END} {total_v_conf}")
        print(f"  {Color.CYAN}VLANs más usadas:{Color.END}")
        for v_id, ct in sorted(vlan_usage.items(), key=lambda x: (x[1], x[0]), reverse=True): print(f"    {Color.YELLOW}VLAN {v_id}:{Color.END} {ct} veces")
    else: print(f"  {Color.DARKCYAN}No hay VLANs configuradas.{Color.END}")
    print(f"\n{Color.BLUE}{'═' * 70}{Color.END}")
    input(f"{Color.GREEN}Presione Enter para volver...{Color.END}"); pop_menu_history()();

def exportar_reporte_a_archivo(dispositivos_lista):
    current_menu_func = lambda: exportar_reporte_a_archivo(dispositivos_lista)
    push_menu_history(current_menu_func)
    mostrar_titulo("📁 EXPORTAR REPORTE A ARCHIVO")
    if not dispositivos_lista:
        mostrar_mensaje("⚠️ No hay dispositivos para exportar.", "advertencia", True); pop_menu_history()(); return
    directorio_reportes = "reportes"
    try: os.makedirs(directorio_reportes, exist_ok=True)
    except OSError as e: mostrar_mensaje(f"Error al crear dir '{directorio_reportes}': {e}", "error", True); pop_menu_history()(); return
    nombre_archivo = datetime.now().strftime("reporte_%Y-%m-%d_%H-%M-%S.txt")
    ruta_completa = os.path.join(directorio_reportes, nombre_archivo)
    try:
        with open(ruta_completa, 'w', encoding='utf-8') as f:
            f.write(f"REPORTE DE DISPOSITIVOS ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})\n")
            f.write(f"Generado por: {current_user}\n{'═'*70}\n\n")
            for i, d in enumerate(dispositivos_lista, 1):
                f.write(f"Dispositivo #{i}\n")
                f.write(f"  Nombre: {d.get('NOMBRE', 'N/A')}\n  IP: {d.get('IP', 'N/A')}\n")
                f.write(f"  Tipo: {d.get('TIPO', 'N/A')}\n  Ubicación/Capa: {d.get('CAPA', 'N/A')}\n")
                s_str = ", ".join(d.get('SERVICIOS', [])) or "Ninguno"
                v_str = ", ".join(map(str, d.get('VLANS', []))) or "Ninguna"
                f.write(f"  Servicios: {s_str}\n  VLANs: {v_str}\n{'-'*70}\n\n")
            f.write(f"Total dispositivos: {len(dispositivos_lista)}\nFIN DEL REPORTE\n")
        mostrar_mensaje(f"Reporte exportado como '{ruta_completa}'", "exito", True)
    except IOError as e: mostrar_mensaje(f"Error al escribir archivo: {e}", "error", True)
    pop_menu_history()();

# 🎛️ Función principal y bucle de menú
def mostrar_menu_principal_opciones(dispositivos_lista):
    current_menu_func = lambda: mostrar_menu_principal_opciones(dispositivos_lista)
    mostrar_titulo("🚀 SISTEMA DE GESTIÓN DE DISPOSITIVOS DE RED 🚀")
    opciones = {
        "1": "📱 Agregar Nuevo Dispositivo", "2": "📜 Mostrar Todos los Dispositivos",
        "3": "🔍 Buscar Dispositivo", "4": "➕ Agregar Servicio a Dispositivo",
        "5": "❌ Eliminar Dispositivo", "6": "📊 Generar Reporte Estadístico",
        "7": "🌐 Probar Conectividad (Ping)", "8": "📁 Exportar Reporte a Archivo",
        "0": "🚪 Salir del Programa"
    }
    for k, v in opciones.items(): print(f"{Color.BOLD}{Color.YELLOW}{k}.{Color.END} {v}")
    
    opcion_elegida = mostrar_opciones_navegacion(current_menu_func, es_menu_principal=True)
    if opcion_elegida is None: return

    if   opcion_elegida == "1": mostrar_barra_progreso(0.5,"Cargando..."); agregar_dispositivo_interactivo(dispositivos_lista)
    elif opcion_elegida == "2": mostrar_barra_progreso(0.5,"Cargando..."); mostrar_dispositivos(dispositivos_lista)
    elif opcion_elegida == "3": mostrar_barra_progreso(0.5,"Iniciando..."); buscar_dispositivo(dispositivos_lista)
    elif opcion_elegida == "4": mostrar_barra_progreso(0.5,"Cargando..."); agregar_servicio_a_dispositivo(dispositivos_lista)
    elif opcion_elegida == "5": mostrar_barra_progreso(0.5,"Cargando..."); eliminar_dispositivo(dispositivos_lista)
    elif opcion_elegida == "6": mostrar_barra_progreso(1,"Generando..."); generar_reporte_estadistico(dispositivos_lista)
    elif opcion_elegida == "7": mostrar_barra_progreso(0.5,"Cargando..."); menu_ping_dispositivo(dispositivos_lista)
    elif opcion_elegida == "8": mostrar_barra_progreso(0.5,"Exportando..."); exportar_reporte_a_archivo(dispositivos_lista)
    elif opcion_elegida == "0": salir_del_programa()
    else:
        mostrar_mensaje(f"Opción '{opcion_elegida}' no válida.", "error"); sleep(2)
        mostrar_menu_principal_opciones(dispositivos_lista)

def main():
    global menu_history, current_user # Asegurar que current_user sea global si se modifica en iniciar_sesion
    
    # Cargar datos al inicio
    # La variable 'dispositivos' aquí será la lista principal de datos.
    dispositivos = cargar_datos() 
    # Pasamos esta lista a las funciones de menú.

    limpiar_pantalla()
    print(f"\n{Color.BLUE}{'═' * 70}{Color.END}")
    print(f"{Color.BOLD}{Color.PURPLE}{'🛡️ BIENVENIDO AL SISTEMA AVANZADO DE GESTIÓN DE REDES 🛡️'.center(70)}{Color.END}")
    print(f"{Color.BLUE}{'═' * 70}{Color.END}")
    mostrar_barra_progreso(1.5, "Iniciando sistema...", sufijo="¡Sistema listo!")

    if not iniciar_sesion():
        return

    menu_principal_lambda = lambda: mostrar_menu_principal_opciones(dispositivos)
    menu_history = [menu_principal_lambda]

    while True:
        if menu_history:
            menu_actual = menu_history[-1]
            menu_actual()
        else:
            mostrar_mensaje("Error crítico: historial de menú vacío. Reiniciando.", "error", True)
            menu_history = [menu_principal_lambda]
            menu_principal_lambda()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        limpiar_pantalla()
        print(f"\n{Color.YELLOW}Interrupción detectada. Cerrando...{Color.END}")
        sleep(1); mostrar_barra_progreso(0.5, "Finalizando...", sufijo="¡Cerrado de forma segura!"); limpiar_pantalla(); sys.exit(0)
    except Exception as e:
        limpiar_pantalla()
        print(f"\n{Color.RED}{Color.BOLD}💥 ERROR INESPERADO Y CRÍTICO 💥{Color.END}")
        print(f"{Color.RED}Error: {type(e).__name__} - {str(e)}{Color.END}")
        print(f"{Color.YELLOW}Reporte este error.{Color.END}")
        import traceback
        with open("error_log.txt", "a", encoding='utf-8') as f_error:
            f_error.write(f"\n--- {datetime.now()} ---\n")
            traceback.print_exc(file=f_error)
        print(f"{Color.DARKCYAN}Registro de error guardado en 'error_log.txt'.{Color.END}")
        input(f"\n{Color.GREEN}Presione Enter para salir...{Color.END}"); sys.exit(1)
