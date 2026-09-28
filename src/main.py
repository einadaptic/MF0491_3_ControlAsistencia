# ==========================================
# MÓDULO PRINCIPAL: main.py
# Controlador central del flujo de ejecución
# ==========================================
from utils import cargar_datos, salir
from ui import (
    mostrar_menu,
    pausar,
    mostrar_despedida,
    vista_crear_registro, 
    vista_leer_registros, 
    vista_actualizar_registro, 
    vista_eliminar_registro
)

def menu():
    """
    Función principal que orquesta el ciclo de vida de la aplicación.
    Carga los datos iniciales, presenta el menú en bucle, deriva las opciones 
    a las vistas correspondientes y gestiona la salida controlada.
    """
    try:
        # Carga la lista de registros desde asistencia.json al arrancar la app
        registros = cargar_datos()
        
        # Bucle principal de interacción con el usuario
        while True:
            # Dibuja el menú en consola y captura la opción elegida (cadena "1" a "5")

            opcion = mostrar_menu()
            print()
            
            match opcion:
                case "1": vista_crear_registro(registros)
                case "2": vista_leer_registros(registros)
                case "3": vista_actualizar_registro(registros)
                case "4": vista_eliminar_registro(registros)
                case "5": break
                case _:   continue

            # Congela la pantalla hasta que el usuario pulsa ENTER antes de limpiar el menú
            pausar()

    except KeyboardInterrupt:
        # Captura la interrupción global por teclado (CTRL+C) a nivel de menú principal
        pass
        
    # Muestra el mensaje visual de cierre de sesión
    mostrar_despedida()
    
    # Ejecuta la finalización limpia del proceso del sistema (sys.exit)
    salir()

# Punto de entrada oficial de la aplicación en Python
if __name__ == "__main__":
    menu()