"""Aplicación web del sistema de control de asistencia."""
from datetime import datetime

from flask import Flask, flash, redirect, render_template, request, url_for

from gestor import actualizar_fichaje, buscar_registro, eliminar_fichaje, registrar_fichaje
from utils import calcular_horas, cargar_datos, formatear_horas


def crear_app(config=None):
    app = Flask(__name__)
    app.config.update(SECRET_KEY="control-asistencia-desarrollo")
    if config:
        app.config.update(config)

    @app.context_processor
    def utilidades_plantillas():
        return {"calcular_horas": calcular_horas, "formatear_horas": formatear_horas}

    @app.get("/")
    def inicio():
        datos = cargar_datos()
        hoy = datetime.now().strftime("%d/%m/%Y")
        horas = sum(calcular_horas(r["hora_entrada"], r["hora_salida"])
                    for r in datos if r.get("hora_salida"))
        recientes = sorted(datos, key=lambda r: datetime.strptime(r["fecha"], "%d/%m/%Y"), reverse=True)[:5]
        return render_template("inicio.html", total=len(datos),
            hoy=sum(r["fecha"] == hoy for r in datos),
            empleados=len({r["id_empleado"] for r in datos}),
            pendientes=sum(not r.get("hora_salida") for r in datos),
            horas=formatear_horas(horas), recientes=recientes)

    @app.route("/registrar", methods=["GET", "POST"])
    def registrar():
        if request.method == "POST":
            datos = cargar_datos()
            empleado = normalizar_empleado(request.form.get("empleado", ""))
            fecha_iso = request.form.get("fecha", "")
            entrada = request.form.get("hora_entrada", "")
            salida = request.form.get("hora_salida", "") or None
            error = validar_formulario(empleado, fecha_iso, entrada, salida)
            fecha = fecha_iso_a_local(fecha_iso) if not error else ""
            existente = buscar_registro(datos, empleado, fecha) if not error else None
            if existente and existente.get("hora_salida"):
                error = "Ese empleado ya tiene una jornada completa en la fecha indicada."
            if error:
                flash(error, "error")
            else:
                registrar_fichaje(datos, empleado, fecha, entrada, salida)
                flash("Asistencia registrada correctamente.", "exito")
                return redirect(url_for("consultar"))
        return render_template("registrar.html", hoy=datetime.now().strftime("%Y-%m-%d"))

    @app.get("/registros")
    def consultar():
        empleado = request.args.get("empleado", "").strip().upper()
        desde, hasta, estado = (request.args.get(k, "") for k in ("desde", "hasta", "estado"))
        resultado = cargar_datos()
        if empleado:
            resultado = [r for r in resultado if empleado in r["id_empleado"]]
        if desde:
            limite = datetime.strptime(desde, "%Y-%m-%d")
            resultado = [r for r in resultado if datetime.strptime(r["fecha"], "%d/%m/%Y") >= limite]
        if hasta:
            limite = datetime.strptime(hasta, "%Y-%m-%d")
            resultado = [r for r in resultado if datetime.strptime(r["fecha"], "%d/%m/%Y") <= limite]
        if estado in ("completado", "pendiente"):
            resultado = [r for r in resultado if bool(r.get("hora_salida")) == (estado == "completado")]
        resultado.sort(key=lambda r: (datetime.strptime(r["fecha"], "%d/%m/%Y"), r["id_empleado"]), reverse=True)
        return render_template("registros.html", registros=resultado)

    @app.route("/registros/<empleado>/<path:fecha>/editar", methods=["GET", "POST"])
    def editar(empleado, fecha):
        datos = cargar_datos()
        registro = buscar_registro(datos, empleado, fecha)
        if not registro:
            flash("El registro solicitado no existe.", "error")
            return redirect(url_for("consultar"))
        if request.method == "POST":
            entrada, salida = request.form.get("hora_entrada", ""), request.form.get("hora_salida", "")
            error = validar_hora(entrada) or validar_hora(salida, opcional=True)
            if error:
                flash(error, "error")
            else:
                actualizar_fichaje(datos, empleado, fecha, entrada, salida or None)
                flash("Registro actualizado correctamente.", "exito")
                return redirect(url_for("consultar"))
        return render_template("editar.html", registro=registro)

    @app.post("/registros/<empleado>/<path:fecha>/eliminar")
    def eliminar(empleado, fecha):
        datos = cargar_datos()
        eliminado = eliminar_fichaje(datos, empleado, fecha)
        flash("Registro eliminado correctamente." if eliminado
              else "El registro solicitado no existe.", "exito" if eliminado else "error")
        return redirect(url_for("consultar"))

    return app


def normalizar_empleado(valor):
    valor = valor.strip().upper().removeprefix("EMP")
    return f"EMP{valor.zfill(3)}" if valor.isdigit() and 1 <= int(valor) <= 999 else ""


def fecha_iso_a_local(valor):
    return datetime.strptime(valor, "%Y-%m-%d").strftime("%d/%m/%Y")


def validar_hora(valor, opcional=False):
    if opcional and not valor:
        return None
    try:
        datetime.strptime(valor, "%H:%M")
        return None
    except ValueError:
        return "Introduce una hora válida en formato HH:MM."


def validar_formulario(empleado, fecha, entrada, salida):
    if not empleado:
        return "El número de empleado debe estar entre 1 y 999."
    try:
        datetime.strptime(fecha, "%Y-%m-%d")
    except ValueError:
        return "Introduce una fecha válida."
    return validar_hora(entrada) or validar_hora(salida, opcional=True)


app = crear_app()

if __name__ == "__main__":
    app.run(debug=True)
