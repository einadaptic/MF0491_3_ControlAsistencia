import sys, json
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, request, Response, redirect, url_for, flash

sys.path.append(str(Path(__file__).resolve().parent / "src"))

from utils import cargar_datos
from gestor import registrar_fichaje, buscar_registro, actualizar_fichaje, eliminar_fichaje

app = Flask(__name__)
app.secret_key = "clave_secreta_control_asistencia"

@app.route("/")
def index():
    registros = cargar_datos()
    
    # Capta el término introducido en la barra de búsqueda
    busqueda = request.args.get("q", "").strip().lower()
    
    # Filtra por ID de empleado o por fecha si hay algo escrito
    if busqueda:
        registros = [
            r for r in registros 
            if busqueda in r["id_empleado"].lower() or busqueda in r["fecha"].lower()
        ]

    # Datos para el modo edición si se ha pulsado 'Editar'
    emp_editar = request.args.get("emp", "")
    fecha_editar = request.args.get("fecha", "")
    reg_editar = None
    if emp_editar and fecha_editar:
        reg_editar = buscar_registro(cargar_datos(), emp_editar, fecha_editar)

    return render_template(
        "index.html", 
        registros=registros, 
        fecha=datetime.now().strftime("%d/%m/%Y"),
        reg_editar=reg_editar,
        busqueda=busqueda
    )

@app.route("/fichar", methods=["POST"])
def fichar():
    num_emp = request.form.get("num_emp")
    id_empleado = f"EMP{num_emp.zfill(3)}"
    fecha = request.form.get("fecha") or datetime.now().strftime("%d/%m/%Y")
    
    hora_entrada = request.form.get("entrada")
    hora_salida = request.form.get("salida") or None
    es_edicion = request.form.get("es_edicion") == "true"

    registros = cargar_datos()

    if es_edicion:
        actualizar_fichaje(registros, id_empleado, fecha, hora_entrada, hora_salida)
        flash(f"✔ Registro de {id_empleado} ({fecha}) actualizado correctamente.", "exito")
        return redirect(url_for("index"))

    registro_existente = buscar_registro(registros, id_empleado, fecha)

    if registro_existente and registro_existente["hora_salida"] is not None:
        flash(f"⚠️ El empleado {id_empleado} ya ha completado su jornada de hoy ({fecha}).", "error")
    elif registro_existente and registro_existente["hora_salida"] is None:
        if not hora_salida:
            flash(f"⚠️ {id_empleado} ya tiene entrada. Introduce la hora de salida para completar jornada.", "warning")
            return redirect(url_for("index"))
        registrar_fichaje(registros, id_empleado, fecha, registro_existente["hora_entrada"], hora_salida)
        flash(f"✔ Salida registrada para {id_empleado}.", "exito")
    else:
        registrar_fichaje(registros, id_empleado, fecha, hora_entrada, hora_salida)
        flash(f"✔ Fichaje registrado para {id_empleado}.", "exito")

    return redirect(url_for("index"))

@app.route("/eliminar", methods=["POST"])
def eliminar():
    id_empleado = request.form.get("id_empleado")
    fecha = request.form.get("fecha")
    
    registros = cargar_datos()
    if eliminar_fichaje(registros, id_empleado, fecha):
        flash(f"✔ Registro de {id_empleado} del {fecha} eliminado.", "exito")
    else:
        flash("❌ No se pudo eliminar el registro.", "error")
        
    return redirect(url_for("index"))

@app.route("/descargar")
def descargar():
    return Response(
        json.dumps(cargar_datos(), indent=4, ensure_ascii=False),
        mimetype="application/json",
        headers={"Content-Disposition": "attachment; filename=asistencia.json"}
    )

if __name__ == "__main__":
    app.run(debug=True)