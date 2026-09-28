import sys, json
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, request, Response, redirect, url_for, flash

sys.path.append(str(Path(__file__).resolve().parent / "src"))

from utils import cargar_datos, calcular_horas, formatear_horas
from gestor import registrar_fichaje, buscar_registro

app = Flask(__name__)
# Necesario para poder usar mensajes emergentes (flash) en el navegador
app.secret_key = "clave_secreta_control_asistencia"

@app.route("/")
def index():
    registros = cargar_datos()
    return render_template("index.html", registros=registros, fecha=datetime.now().strftime("%d/%m/%Y"))

@app.route("/fichar", methods=["POST"])
def fichar():
    num_emp = request.form.get("num_emp")
    id_empleado = f"EMP{num_emp.zfill(3)}"
    fecha_hoy = datetime.now().strftime("%d/%m/%Y")
    
    hora_entrada = request.form.get("entrada")
    hora_salida = request.form.get("salida") or None

    registros = cargar_datos()
    registro_existente = buscar_registro(registros, id_empleado, fecha_hoy)

    # CASO 1: El empleado ya tiene entrada y salida registradas hoy (DUPLICADO)
    if registro_existente and registro_existente["hora_salida"] is not None:
        flash(f"⚠️ El empleado {id_empleado} ya ha completado su jornada de hoy ({fecha_hoy}).", "error")
        return redirect(url_for("index"))

    # CASO 2: Tenía la entrada pero le faltaba la salida
    elif registro_existente and registro_existente["hora_salida"] is None:
        if not hora_salida:
            flash(f"⚠️ {id_empleado} ya tiene hora de entrada ({registro_existente['hora_entrada']}). Introduce la hora de salida para completar la jornada.", "warning")
            return redirect(url_for("index"))
            
        registrar_fichaje(registros, id_empleado, fecha_hoy, registro_existente["hora_entrada"], hora_salida)
        flash(f"✔ Salida registrada correctamente para {id_empleado}.", "exito")

    # CASO 3: Registro nuevo
    else:
        registrar_fichaje(registros, id_empleado, fecha_hoy, hora_entrada, hora_salida)
        flash(f"✔ Fichaje registrado correctamente para {id_empleado}.", "exito")

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