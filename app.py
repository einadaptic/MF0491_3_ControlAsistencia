import sys, json
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, request, Response, redirect, url_for

# Añadimos la carpeta 'src' al path
sys.path.append(str(Path(__file__).resolve().parent / "src"))

from utils import cargar_datos, calcular_horas, formatear_horas
from gestor import registrar_fichaje

app = Flask(__name__)

@app.route("/")
def index():
    registros = cargar_datos()
    return render_template("index.html", registros=registros, fecha=datetime.now().strftime("%d/%m/%Y"))

@app.route("/fichar", methods=["POST"])
def fichar():
    num_emp = request.form.get("num_emp")
    id_empleado = f"EMP{num_emp.zfill(3)}"
    fecha = datetime.now().strftime("%d/%m/%Y")
    
    # Reutilizamos tu lógica de fichaje
    registrar_fichaje(
        cargar_datos(),
        id_empleado,
        fecha,
        request.form.get("entrada"),
        request.form.get("salida") or None
    )
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