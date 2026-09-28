# ==========================================
# MÓDULO DE LÓGICA DE NEGOCIO: gestor.py
# Operaciones CRUD sobre la estructura de datos en memoria
# ==========================================
from utils import guardar_datos

def buscar_registro(registros, emp_id, fecha):
    """
    Busca de forma secuencial un fichaje en la lista de registros en memoria RAM.
    
    Parámetros:
        registros (list): Lista de diccionarios con el historial de fichajes.
        emp_id (str)   : ID formateado del empleado (ej. 'EMP001').
        fecha (str)    : Fecha del fichaje en formato 'DD/MM/AAAA'.
        
    Devuelve:
        dict: El diccionario del registro coincidente si existe.
        None: Si no se encuentra ninguna coincidencia.
    """
    # Iteramos cada diccionario 'r' de la lista de registros
    for r in registros:
        # Evaluamos coincidencia exacta de ID y Fecha (clave primaria compuesta)
        if r["id_empleado"] == emp_id and r["fecha"] == fecha:
            return r  # Retorna la referencia directa al diccionario en memoria
    return None  # Finaliza el bucle sin coincidencias



def registrar_fichaje(registros, emp_id, fecha, hora_entrada, hora_salida=None):
    """
    Crea un nuevo fichaje o completa la hora de salida de una jornada no cerrada.
    
    Parámetros:
        registros (list)   : Lista de diccionarios de fichajes.
        emp_id (str)      : ID formateado del empleado.
        fecha (str)       : Fecha del fichaje.
        hora_entrada (str): Hora de entrada obligatoria (HH:MM).
        hora_salida (str) : Hora de salida optativa (HH:MM o None).
        
    Devuelve:
        dict: El registro creado o actualizado.
    """
    # Comprobamos si el empleado ya tiene un fichaje iniciado en la fecha dada
    registro = buscar_registro(registros, emp_id, fecha)
    
    # CASO 1: El registro existe pero tenía la salida pendiente (None)
    if registro and registro["hora_salida"] is None:
        registro["hora_salida"] = hora_salida  # Actualizamos la hora de salida para cerrar jornada
    
    # CASO 2: No existe registro previo para hoy (Jornada nueva)
    else:
        registro = {
            "id_empleado": emp_id,
            "fecha": fecha,
            "hora_entrada": hora_entrada,
            "hora_salida": hora_salida
        }
        registros.append(registro)  # Añadimos el nuevo diccionario a la lista global

    # Sincronizamos los cambios inmediatamente en el archivo JSON
    guardar_datos(registros)
    return registro



def actualizar_fichaje(registros, emp_id, fecha, nueva_entrada=None, nueva_salida=None):
    """
    Modifica las horas de entrada y/o salida de un registro existente.
    
    Parámetros:
        registros (list)    : Lista de diccionarios de fichajes.
        emp_id (str)       : ID formateado del empleado.
        fecha (str)        : Fecha del fichaje a modificar.
        nueva_entrada (str): Nueva hora de entrada (si se deja vacía, se ignora).
        nueva_salida (str) : Nueva hora de salida (si se deja vacía, se ignora).
        
    Devuelve:
        bool: True si la actualización fue exitosa, False si el registro no existía.
    """
    # Localizamos el registro objetivo en memoria
    registro = buscar_registro(registros, emp_id, fecha)
    if not registro:
        return False  # Cancela la operación si el registro no existe
        
    # Asignamos los nuevos valores solo si fueron proporcionados (si no presiono ENTER)
    if nueva_entrada:
        registro["hora_entrada"] = nueva_entrada
    if nueva_salida:
        registro["hora_salida"] = nueva_salida

    # Guardamos los cambios en el disco
    guardar_datos(registros)
    return True



def eliminar_fichaje(registros, emp_id, fecha):
    """
    Elimina permanentemente un registro de la lista y actualiza el almacenamiento.
    
    Parámetros:
        registros (list): Lista de diccionarios de fichajes.
        emp_id (str)   : ID formateado del empleado.
        fecha (str)    : Fecha del fichaje a eliminar.
        
    Devuelve:
        bool: True si el registro se eliminó correctamente, False si no existía.
    """
    # Buscamos la referencia del registro a borrar
    registro = buscar_registro(registros, emp_id, fecha)
    if registro:
        registros.remove(registro)  # Eliminamos el diccionario de la lista en RAM
        guardar_datos(registros)    # Reescribimos el JSON sin el elemento borrado
        return True
    return False