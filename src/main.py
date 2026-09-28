# ==========================================
# MÓDULO PRINCIPAL: main.py
# Controlador central del flujo de ejecución
# ==========================================
from utils import cargar_datos, salir
from ui import (
    mostrar_menu,
    ctrl_c,
    pausar,
    mostrar_despedida,
    vista_crear_registro, 
    vista_leer_registros, 
    vista_actualizar_registro, 
    vista_eliminar_registro
)

def menu():
    registros = cargar_datos()
    
    while True:
        try:
            opcion = mostrar_menu()
            print()
            
            match opcion:
                case "1": vista_crear_registro(registros)
                case "2": vista_leer_registros(registros)
                case "3": vista_actualizar_registro(registros)
                case "4": vista_eliminar_registro(registros)
                case "0": break
                case _:   continue

            pausar()

        except KeyboardInterrupt:
            ctrl_c()
            pausar()
            continue

    mostrar_despedida()
    salir()

# Punto de entrada oficial de la aplicación en Python
if __name__ == "__main__":
    menu()