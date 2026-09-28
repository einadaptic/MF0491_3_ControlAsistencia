# ==========================================
# MÓDULO DE INTERFAZ DE USUARIO: ui.py
# Vistas de consola y elementos de Rich
# ==========================================
import platform, subprocess, re, time
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.panel import ROUNDED
from rich.align import Align
from rich.table import Table

from utils import calcular_horas, formatear_horas
from gestor import buscar_registro, registrar_fichaje, actualizar_fichaje, eliminar_fichaje

# Configuración visual de consola exclusiva de la UI
console      = Console()
_ES_WINDOWS  = platform.system() == "Windows"
_CMD_LIMPIAR = ["cls"] if _ES_WINDOWS else ["clear"]


# ==========================================
# FUNCIONES AUXILIARES DE CONSOLA
# ==========================================

def limpiar_pantalla():
    """
    Ejecuta el comando de terminal correspondiente según el sistema operativo
    ('cls' en Windows o 'clear' en Unix/Linux/macOS) para refrescar la consola.
    """
    subprocess.run(_CMD_LIMPIAR, shell=_ES_WINDOWS)


def mostrar_menu():
    """
    Limpia la consola, dibuja la interfaz principal del menú desplegando las 
    opciones disponibles mediante la librería Rich y captura la elección del usuario.
    
    Returns:
        str: Cadena de texto con la opción seleccionada (ej. '1', '2', ...).
    """
    limpiar_pantalla()

    texto_cabecera = (
        "[bold white]🕒 CONTROL DE ASISTENCIA[/bold white]\n"
        "[dim white] Sistema de Fichaje v1.0[/dim white]"
    )
    cabecera = Panel(texto_cabecera, style="white", box=ROUNDED, padding=(1, 6))
    console.print(Align.left(cabecera))
    
    print("\n1. Crear registro............ (Create)")
    print("2. Leer Registros............ (Read)")
    print("3. Actualizar Registro....... (Update)")
    print("4. Eliminar Registro......... (Delete)")
    print("\n0. Salir..................... (Exit)")

    return console.input('\nSelecciona una opción (0-5) > ')


def ctrl_c():
    """
    Mensaje de excepción KeyboardInterrupt.
    """
    console.print("\n\n⚠️  Operación cancelada por el usuario.")
    return

def pausar():
    """
    Detiene temporalmente la ejecución del programa requiriendo la pulsación de [ENTER].
    Permite al usuario revisar la información de pantalla antes de refrescar e ir al menú.
    """
    try:
        console.input('\n[cyan][ENTER][/cyan] para volver al menú > ')
    except KeyboardInterrupt:
        pass


def pedir_entrada(prompt, formato, msg_error="❌ ERROR", trans=lambda x: x.strip()):
    """
    Solicita una entrada por teclado de forma iterativa y la evalúa contra una Regex.
    
    Aplica mecanismos de limpieza de terminal (\033[F\033[K) a partir del tercer intento
    fallido para evitar saturar la consola con mensajes de error repetidos.
    
    Args:
        prompt (str): Texto a mostrar en la solicitud.
        formato (str): Patrón de expresión regular para validar la respuesta.
        msg_error (str): Mensaje por defecto en caso de fallo de validación.
        trans (function): Transformación opcional previa a la validación (limpieza de espacios por defecto).
        
    Returns:
        str: Entrada del usuario debidamente validada.
    """
    intentos = 0
    while True:
        respuesta = trans(console.input(prompt))
        if re.fullmatch(formato, respuesta): 
            return respuesta

        intentos += 1
        if intentos == 1:
            prompt = f"[yellow]{msg_error}: [/yellow]"
        elif intentos == 2:
            prompt = f"[red]Por favor, fíjate bien e inténtalo de nuevo: [/red]"
        else:
            print("\033[F\033[K", end="")
            prompt = f"[red]Por favor, fíjate bien e inténtalo de nuevo: [/red]"


def mostrar_despedida():
    """
    Imprime el mensaje gráfico final de agradecimiento al salir de la aplicación.
    """
    #console.print(f"\n\n[cyan]👋 ¡Gracias por usar la aplicación! Hasta pronto.[/cyan]\n")
    for char in "\nSee you later,🐊 alligator...\n\n":
        console.print(char, style="bold green", end="", highlight=False)
        time.sleep(0.04)


# ===========================================
# VISTAS
# ===========================================

def vista_crear_registro(registros):
    """
    Gestiona la toma de fichajes de la jornada diaria.
    
    Evalúa tres posibles escenarios del empleado en el día actual:
      1. Jornada completada: Avisa que no se pueden añadir más marcas.
      2. Salida pendiente: Solicita únicamente la hora de salida para cerrar la jornada.
      3. Nuevo registro: Pide entrada y opcionalmente salida para crear la ficha.
      
    Args:
        registros (list): Lista global de diccionarios con los fichajes en memoria.
    """
    panel = Panel(
        f"Pulsa [cyan][CTRL]+[C][/cyan] para cancelar este proceso y volver al menú",
        title=f"[bold white]📌 Crear registro[/bold white]"
    )
    console.print(panel, justify="left")
    print()
    # ==============================================================================
    # EXPRESIÓN REGULAR: Código del empleado (Número entre 1 a 999)
    # PATRÓN: r"^[1-9]\d{0,2}$"
    # ==============================================================================
    #
    # r""        -> Raw string (cadena en crudo): evita que Python interprete las
    #               barras invertidas (\) como caracteres de escape especiales.
    # ^          -> Ancla de inicio: exige que la coincidencia empiece al principio
    #               mismo del texto ingresado.
    # [1-9]      -> Conjunto / Rango de caracteres: obliga a que el PRIMER dígito
    #               sea un número entre 1 y 9. Impide que un ID empiece por 0 (ej: 01).
    # \d         -> Dígito numérico: equivale a [0-9]. Coincide con cualquier dígito.
    # {0,2}      -> Cuantificador de rango: indica que el patrón anterior (\d) se
    #               puede repetir entre 0 y 2 veces más.
    #               - Si se repite 0 veces -> número de 1 dígito (1 - 9)
    #               - Si se repite 1 vez   -> número de 2 dígitos (10 - 99)
    #               - Si se repite 2 veces -> número de 3 dígitos (100 - 999)
    # $          -> Ancla de fin: exige que el texto termine inmediatamente después.
    #               Evita que se introduzcan caracteres o números de más (ej: 1000).
    # ==============================================================================
    patron_empleado = r"^[1-9]\d{0,2}$"    

    num_str = pedir_entrada("[orange3]Número de empleado (1-999):[/orange3] ", patron_empleado, "❌ ERROR - Introduce un número válido entre 1 y 999")
    id_empleado = f"EMP{num_str.zfill(3)}"
    console.print(f"ID seleccionado: [green]{id_empleado}[/green]\n")

    fecha = datetime.now().strftime("%d/%m/%Y")
    registro_existente = buscar_registro(registros, id_empleado, fecha)

    # ==============================================================================
    # EXPRESIÓN REGULAR: Validación Opcional de Fecha (DD/MM/AAAA)
    # PATRÓN: r"^((0[1-9]|[12]\d|3[01])/(0[1-9]|1[0-2])/\d{4})?$"
    # ==============================================================================
    #
    # ESTRUCTURA GENERAL:
    # ^          : Inicio absoluto de la cadena.
    # ( ... )?   : Grupo de captura principal marcado como OPCIONAL con '?'.
    #              Permite que la entrada esté vacía (al pulsar [ENTER]).
    # $          : Fin absoluto de la cadena.
    #
    # COMPONENTES INTERNOS DEL GRUPO PRINCIPAL:
    #
    # 1. DÍA -> (0[1-9]|[12]\d|3[01])
    #    Evalúa los días válidos del mes (01 al 31) mediante tres alternativas:
    #    - 0[1-9] : Días del '01' al '09'.
    #    - [12]\d : Días del '10' al '29'. 
    #               Nota sobre '\d': Metacarácter equivalente a [0-9] (cualquier dígito).
    #               Por tanto, '[12]\d' coincide con un '1' o '2' seguido de cualquier dígito.
    #    - 3[01]  : Días '30' y '31'.
    #
    # 2. SEPARADOR DE FECHA -> /
    #    Exige la barra diagonal literal entre el día y el mes.
    #
    # 3. MES -> (0[1-9]|1[0-2])
    #    Evalúa los meses válidos del año (01 al 12) mediante dos alternativas:
    #    - 0[1-9] : Meses del '01' al '09' (Enero a Septiembre).
    #    - 1[0-2] : Meses '10', '11' y '12' (Octubre, Noviembre y Diciembre).
    #
    # 4. SEPARADOR DE FECHA -> /
    #    Exige la segunda barra diagonal literal entre el mes y el año.
    #
    # 5. AÑO -> \d{4}
    #    Exige exactamente 4 dígitos numéricos consecutivos (ej. 2026).
    #    '\d' representa cualquier dígito numérico (0-9) y '{4}' fija la cantidad exacta.
    # ==============================================================================
    patron_hora_obligatoria = r"^(?:[01]\d|2[0-3]):[0-5]\d$"
    
    # ==============================================================================
    # EXPRESIÓN REGULAR PARA HORA OPCIONAL (Formato HH:MM en 24 Horas)
    # PATRÓN: r"^((?:[01]\d|2[0-3]):[0-5]\d)?$"
    # ==============================================================================
    #
    # Descripción detallada de los metacaracteres y estructuras:
    #
    #  r"..."      : Raw string (cadena en bruto) de Python. Evita que las barras 
    #                invertidas '\' se interpreten como escapes de texto.
    #  ^           : Inicio de la cadena. Obliga a que la coincidencia empiece desde
    #                el primer carácter introducido.
    #  ( ... )?    : Grupo de captura opcional (modificador '?'). Hace que TODO lo que
    #                está entre paréntesis sea optativo (permite validar si el usuario
    #                presiona [ENTER] y deja la entrada vacía: "").
    #  (?: ... )   : Grupo NO capturador. Agrupa las opciones de las horas para aplicar
    #                el operador '|' (OR) sin almacenar una memoria extra en Regex.
    #  [01]\d      : Valida horas desde '00' hasta '19':
    #                - [01] : Coincide exactamente con el dígito '0' o el dígito '1'.
    #                - \d   : Coincide con cualquier dígito numérico del '0' al '9' 
    #                         (equivalente al conjunto de caracteres [0-9]).
    #  |           : Operador Lógico 'OR' (O alternativo). Separa los rangos válidos.
    #  2[0-3]      : Valida horas desde '20' hasta '23':
    #                - '2'  : Exige de forma literal el primer dígito '2'.
    #                - [0-3]: Coincide con un solo dígito comprendido entre el '0' y el '3'.
    #  :           : Carácter literal de dos puntos. Separa de forma obligatoria
    #                las horas de los minutos.
    #  [0-5]\d     : Valida minutos desde '00' hasta '59':
    #                - [0-5]: Coincide con la primera cifra de los minutos (de '0' a '5').
    #                - \d   : Coincide con cualquier dígito numérico ('0' al '9') para
    #                         el segundo dígito de los minutos.
    #  $           : Fin de la cadena. Asegura que no haya ningún carácter adicional
    #                después de la hora ingresada.
    # ==============================================================================
    patron_salida_opcional  = r"^((?:[01]\d|2[0-3]):[0-5]\d)?$"

    # CASO A: Ya completó jornada
    if registro_existente and registro_existente["hora_salida"] is not None:
        console.print(f"[red]⚠️  El empleado {id_empleado} ya ha registrado su jornada de hoy {fecha}.[/red]")
        return

    # CASO B: Registrar SALIDA
    elif registro_existente and registro_existente["hora_salida"] is None:
        console.print(f"[cyan]Entrada registrada previa a las {registro_existente['hora_entrada']}. Completando salida...[/cyan]")
        hora_salida = pedir_entrada("[orange3]Hora de salida (HH:MM):[/orange3] ", patron_hora_obligatoria, "❌ ERROR - Formato de hora inválido")
        registro = registrar_fichaje(registros, id_empleado, fecha, registro_existente["hora_entrada"], hora_salida)

    # CASO C: Registrar ENTRADA
    else:
        hora_entrada = pedir_entrada("[orange3]Hora de entrada (HH:MM):[/orange3] ", patron_hora_obligatoria, "❌ ERROR - Formato de hora inválido")
        hora_salida  = pedir_entrada("[orange3]Hora de salida (HH:MM, o [ENTER] si queda pendiente):[/orange3] ", patron_salida_opcional, "❌ ERROR - Formato de hora inválido")
        hora_salida  = hora_salida if hora_salida else None
        registro = registrar_fichaje(registros, id_empleado, fecha, hora_entrada, hora_salida)

    # Presentación
    horas_trabajo       = calcular_horas(registro["hora_entrada"], registro["hora_salida"]) if registro["hora_salida"] else None
    duracion_formateada = formatear_horas(horas_trabajo)

    print()
    panel = Panel(
        f"\n[bold white]Usuario:[/bold white] [green]{registro['id_empleado']}[/green] | "
        f"[bold white]Fecha:[/bold white] [green]{registro['fecha']}[/green] | "
        f"[bold white]Entrada:[/bold white] [green]{registro['hora_entrada']}[/green] | "
        f"[bold white]Salida:[/bold white] [green]{registro['hora_salida'] or 'PENDIENTE'}[/green] | "
        f"[bold white]Total:[/bold white] [green]{duracion_formateada}[/green]\n",
        title="[bold white]Nuevo registro completado[/bold white]"
    )
    console.print(panel, justify="left")


def vista_leer_registros(registros):
    """
    Construye y proyecta la consulta de fichajes del sistema.
    
    Ordena la colección de datos cronológicamente (priorizando ID de empleado y 
    fecha convertible a datetime) y renderiza una tabla con formato Rich, incluyendo
    numeración de filas, marcas de 'PENDIENTE' y horas computadas.
    
    Args:
        registros (list): Lista global de diccionarios con los fichajes almacenados.
    """
    panel = Panel(
        f"¿A que no tienes tiempo de pulsar [cyan][CTRL]+[C][/cyan] para cancelar antes de que acabe?",
        title=f"[bold white]📌 Leer registros[/bold white]"
    )
    console.print(panel, justify="left")
    print()
    if not registros:
        console.print("\n[yellow]📋 No hay ningún registro guardado en el sistema.[/yellow]\n")
        return

    registros_ordenados = sorted(
        registros, 
        key=lambda r: (r["id_empleado"], datetime.strptime(r["fecha"], "%d/%m/%Y"))
    )

    tabla = Table(
        title="[not italic][bold white]📋 HISTORIAL DE ASISTENCIA[/bold white] (ordenado por empleado y fecha)", 
        expand=False,
        show_lines=True
    )
    tabla.add_column("#", justify="center", style="dim white")
    tabla.add_column("Empleado", justify="center", style="green")
    tabla.add_column("Fecha", justify="center", style="green")
    tabla.add_column("Entrada", justify="center", style="green")
    tabla.add_column("Salida", justify="center", style="green")
    tabla.add_column("Total Horas", justify="center", style="bold green")

    # 2. Usamos enumerate() para obtener el índice de la fila (empezando en 1)
    for idx, registro in enumerate(registros_ordenados, 1):
        id_empleado         = registro["id_empleado"]
        fecha               = registro["fecha"]
        entrada             = registro["hora_entrada"]
        salida              = registro["hora_salida"] or "[red]PENDIENTE[/red]"
        duracion_formateada = formatear_horas(calcular_horas(entrada, registro["hora_salida"])) if registro["hora_salida"] else "-"
        
        # Pasamos el número de fila convertido a str
        tabla.add_row(str(idx), id_empleado, fecha, entrada, salida, duracion_formateada)

    print()
    console.print(tabla)
    print()


def vista_actualizar_registro(registros):
    """
    Permite la modificación manual de horas de entrada/salida de un fichaje existente.
    
    Solicita la clave primaria (ID + Fecha), valida los datos y permite al usuario
    ingresar nuevas horas o presionar [ENTER] para conservar los valores originales.
    
    Args:
        registros (list): Lista global de diccionarios con los fichajes almacenados.
    """
    panel = Panel(
        f"Pulsa [cyan][CTRL]+[C][/cyan] para cancelar este proceso y volver al menú",
        title=f"[bold white]📌 Actualizar registro[/bold white]"
    )
    console.print(panel, justify="left")
    print()
    if not registros:
        console.print("\n[bold yellow]📋 No hay registros en el sistema para actualizar.[/bold yellow]\n")
        return

    patron_empleado = r"^[1-9]\d{0,2}$"
    num_str = pedir_entrada("[orange3]Número de empleado a actualizar (1-999):[/orange3] ", patron_empleado, "❌ ERROR - Introduce un número válido entre 1 y 999")
    id_empleado = f"EMP{num_str.zfill(3)}"

    fecha_hoy = datetime.now().strftime("%d/%m/%Y")
    
    patron_fecha_opcional = r"^((0[1-9]|[12]\d|3[01])/(0[1-9]|1[0-2])/\d{4})?$"
    fecha_input = pedir_entrada(f"[orange3]Fecha DD/MM/AAAA (o [ENTER] para hoy {fecha_hoy}):[/orange3] ", patron_fecha_opcional, "❌ ERROR - Formato de fecha inválido")
    fecha = fecha_input if fecha_input else fecha_hoy

    registro = buscar_registro(registros, id_empleado, fecha)
    if not registro:
        console.print(f"\n[red]⚠️  No se encontró ningún registro para {id_empleado} en la fecha {fecha}.[/red]\n")
        return

    console.print(f"\n[cyan]Modificando registro de {id_empleado} ({fecha}):[/cyan]")
    console.print(f"Valores actuales -> Entrada: [green]{registro['hora_entrada']}[/green] | Salida: [green]{registro['hora_salida'] or 'PENDIENTE'}[/green]\n")

    patron_hora_opcional = r"^((?:[01]\d|2[0-3]):[0-5]\d)?$"
    nueva_entrada = pedir_entrada(f"[orange3]Nueva hora de entrada (HH:MM, o [ENTER] para conservar {registro['hora_entrada']}):[/orange3] ", patron_hora_opcional, "❌ ERROR - Formato de hora inválido")
    salida_texto = registro['hora_salida'] or 'PENDIENTE'
    nueva_salida = pedir_entrada(f"[orange3]Nueva hora de salida (HH:MM, o [ENTER] para conservar {salida_texto}):[/orange3] ", patron_hora_opcional, "❌ ERROR - Formato de hora inválido")

    actualizar_fichaje(registros, id_empleado, fecha, nueva_entrada, nueva_salida)
    
    # Obtenemos el total de horas actualizado
    horas_trabajo       = calcular_horas(registro["hora_entrada"], registro["hora_salida"]) if registro["hora_salida"] else None
    duracion_formateada = formatear_horas(horas_trabajo)

    print()
    panel = Panel(
        f"\n[bold white]Usuario:[/bold white] [green]{registro['id_empleado']}[/green] | "
        f"[bold white]Fecha:[/bold white] [green]{registro['fecha']}[/green] | "
        f"[bold white]Entrada:[/bold white] [green]{registro['hora_entrada']}[/green] | "
        f"[bold white]Salida:[/bold white] [green]{registro['hora_salida'] or 'PENDIENTE'}[/green] | "
        f"[bold white]Total:[/bold white] [green]{duracion_formateada}[/green]\n",
        title="[bold white]Registro actualizado[/bold white]"
    )
    console.print(panel, justify="left")


def vista_eliminar_registro(registros):
    """
    Gestiona la eliminación permanente de un registro de fichaje.
    
    Busca la ficha por ID de empleado y Fecha, proyecta un resumen informativo
    y solicita confirmación explícita ('s'/'n') antes de llamar a la eliminación.
    
    Args:
        registros (list): Lista global de diccionarios con los fichajes almacenados.
    """
    panel = Panel(
        f"Pulsa [cyan][CTRL]+[C][/cyan] para cancelar este proceso y volver al menú",
        title=f"[bold white]📌 Eliminar registro[/bold white]"
    )
    console.print(panel, justify="left")
    print()
    if not registros:
        console.print("\n[bold yellow]📋 No hay registros en el sistema para eliminar.[/bold yellow]\n")
        return

    patron_empleado = r"^[1-9]\d{0,2}$"
    num_str = pedir_entrada("[orange3]Número de empleado a eliminar (1-999):[/orange3] ", patron_empleado, "❌ ERROR - Introduce un número válido entre 1 y 999")
    id_empleado = f"EMP{num_str.zfill(3)}"

    fecha_hoy = datetime.now().strftime("%d/%m/%Y")
    patron_fecha_opcional = r"^((0[1-9]|[12]\d|3[01])/(0[1-9]|1[0-2])/\d{4})?$"
    fecha_input = pedir_entrada(f"[orange3]Fecha DD/MM/AAAA (o [ENTER] para hoy {fecha_hoy}):[/orange3] ", patron_fecha_opcional, "❌ ERROR - Formato de fecha inválido")
    fecha = fecha_input if fecha_input else fecha_hoy

    registro = buscar_registro(registros, id_empleado, fecha)
    if not registro:
        console.print(f"\n[red]⚠️  No se encontró ningún registro para {id_empleado} en la fecha {fecha}.[/red]")
        return

    console.print(f"\n[cyan]Registro localizado:[/cyan] [green]{id_empleado}[/green] | Fecha: {fecha} | Entrada: {registro['hora_entrada']} | Salida: {registro['hora_salida'] or 'PENDIENTE'}\n")

    # ==============================================================================
    # EXPRESIÓN REGULAR PARA CONFIRMACIÓN (Formato s/n)
    # PATRÓN: r"^[sSnN]$"
    # ==============================================================================
    #
    # ^       : Inicio de la cadena. Asegura que no haya caracteres antes.
    # [sSnN]  : Clase de caracteres (conjunto permitido). Acepta EXACTAMENTE una letra
    #           que sea 's' minúscula, 'S' mayúscula, 'n' minúscula o 'N' mayúscula.
    # $       : Fin de la cadena. Asegura que no haya caracteres después.
    #
    # Comportamiento: Valida únicamente entradas de un solo carácter para confirmar (sí/no),
    #                 rechazando espacios, números o palabras completas (ej. "si", "no").
    # ==============================================================================
    patron_s_n = r"^[sSnN]$"
    confirmacion = pedir_entrada("➡️  ¿Confirmas la eliminación de este registro? [cyan](s/n)[/cyan]: ", patron_s_n, "❌ Introduce 's' para sí o 'n' para no")

    if confirmacion.lower() == "s":
        eliminar_fichaje(registros, id_empleado, fecha)
        console.print(f"\n[green]✔ El registro de {id_empleado} para el {fecha} ha sido eliminado correctamente.[/green]")
    else:
        console.print("\n[yellow]Operación cancelada. El registro se mantiene igual.[/yellow]")