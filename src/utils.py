# ==========================================
# MÓDULO DE PERSISTENCIA Y AUXILIARES: utils.py
# Funciones de lectura/escritura JSON y cálculos de tiempo
# ==========================================
import sys, json
from pathlib import Path
from datetime import datetime, timedelta
from pathlib import Path

# Define la ruta base
BASE_DIR = Path(__file__).resolve().parent
# Ruta completa al archivo JSON dentro de la carpeta "data"
ARCHIVO_DATOS = BASE_DIR / "data" / "asistencia.json"
# Crea la carpeta "data" automáticamente si no existe todavía
ARCHIVO_DATOS.parent.mkdir(parents=True, exist_ok=True)

def cargar_datos():
    """
    Carga y devuelve la lista de fichajes guardados en el archivo JSON.
    Si el archivo no existe o ocurre algún error de lectura/corrupción,
    devuelve una lista vacía para evitar que la aplicación falle.
    """
    if not ARCHIVO_DATOS.exists():
        return []
    try:
        # Abre el archivo en modo lectura con codificación UTF-8
        with open(ARCHIVO_DATOS, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        # Captura silenciosa de errores (JSON corrupto, permisos, etc.)
        return []


def guardar_datos(registros):
    """
    Guarda la lista completa de registros en el archivo JSON local.
    Aplica sangría de 4 espacios y mantiene caracteres especiales UTF-8.
    """
    with open(ARCHIVO_DATOS, "w", encoding="utf-8") as f:
        json.dump(registros, f, indent=4, ensure_ascii=False)


def calcular_horas(entrada_str, salida_str):
    """
    Calcula la diferencia de tiempo entre la hora de entrada y la de salida.
    Soporta turnos nocturnos sumando 1 día si la hora de salida es menor que la de entrada.
    Devuelve la duración total expresada en horas decimales (float).
    """
    formato = "%H:%M"
    # Convierte las cadenas HH:MM a objetos datetime para realizar operaciones matemáticas
    t_entrada = datetime.strptime(entrada_str, formato)
    t_salida = datetime.strptime(salida_str, formato)
    
    # Manejo de jornada nocturna (ej. entrada 22:00, salida 06:00)
    if t_salida < t_entrada: 
        t_salida += timedelta(days=1)
        
    # Convierte la diferencia de tiempo a segundos y la transforma a horas
    return (t_salida - t_entrada).total_seconds() / 3600


def formatear_horas(horas_decimal):
    """
    Convierte una cifra de horas en formato decimal a una cadena legible (ej. '08h 30m').
    Si no hay un valor de horas (jornada pendiente), devuelve un guion '-'.
    """
    if horas_decimal is None:
        return "-"
        
    # Redondea y calcula las horas y minutos enteros
    total_minutos = int(round(horas_decimal * 60))
    horas = total_minutos // 60
    minutos = total_minutos % 60
    
    # Formatea con relleno de ceros a la izquierda para mantener un ancho fijo de 2 dígitos
    return f"{str(horas).zfill(2)}h {str(minutos).zfill(2)}m"


def salir():
    """Finaliza el proceso del sistema de forma limpia enviando el código de salida 0."""
    sys.exit(0)