import sys, json
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, request, Response, redirect, url_for, flash

sys.path.append(str(Path(__file__).resolve().parent / "src"))

from utils import cargar_datos, calcular_horas, formatear_horas
from gestor import registrar_fichaje, buscar_registro, actualizar_fichaje, eliminar_fichaje

app = Flask(__name__)
app.secret_key = "clave_secreta_control_asistencia"

# Helper para procesar registros con horas
def obtener_registros_procesados():
    registros = cargar_datos()
    procesados = []
    for r in registros:
        reg = dict(r)
        if reg.get("hora_salida"):
            duracion = calcular_horas(reg["hora_entrada"], reg["hora_salida"])
            reg["horas_decimal"] = duracion
            reg["total_horas"] = formatear_horas(duracion)
        else:
            reg["horas_decimal"] = 0
            reg["total_horas"] = "-"
        procesados.append(reg)
    return procesados

# --- PÁGINA PRINCIPAL (GESTIÓN DE FICHAJES) ---
@app.route("/")
def index():
    registros = obtener_registros_procesados()
    busqueda = request.args.get("q", "").strip().lower()
    
    if busqueda:
        registros = [
            r for r in registros 
            if busqueda in r["id_empleado"].lower() or busqueda in r["fecha"].lower()
        ]

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

# --- PÁGINA 1: DASHBOARD / MÉTRICAS ---
@app.route("/dashboard")
def dashboard():
    registros = obtener_registros_procesados()
    fecha_hoy = datetime.now().strftime("%d/%m/%Y")
    
    total_fichajes = len(registros)
    fichajes_hoy = [r for r in registros if r["fecha"] == fecha_hoy]
    empleados_unicos = len(set(r["id_empleado"] for r in registros))
    pendientes = sum(1 for r in registros if r["hora_salida"] is None)
    
    total_horas_decimal = sum(r["horas_decimal"] for r in registros)
    total_horas_formateadas = formatear_horas(total_horas_decimal)

    return render_template(
        "dashboard.html",
        total_fichajes=total_fichajes,
        fichajes_hoy=len(fichajes_hoy),
        empleados_unicos=empleados_unicos,
        pendientes=pendientes,
        total_horas=total_horas_formateadas
    )

# --- PÁGINA 2: INFORME POR EMPLEADO ---
@app.route("/empleado/<id_emp>")
def detalle_empleado(id_emp):
    registros = obtener_registros_procesados()
    fichajes_emp = [r for r in registros if r["id_empleado"] == id_emp]
    
    horas_totales = sum(r["horas_decimal"] for r in fichajes_emp)
    
    return render_template(
        "empleado.html",
        id_emp=id_emp,
        fichajes=fichajes_emp,
        total_horas=formatear_horas(horas_totales)
    )

# --- PÁGINA 3: VISOR JSON ---
@app.route("/visor-json")
def visor_json():
    datos = cargar_datos()
    json_formateado = json.dumps(datos, indent=4, ensure_ascii=False)
    return render_template("visor_json.html", json_raw=json_formateado)

# --- ACCIONES API EXISTENTES ---
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