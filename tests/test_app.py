import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import utils
from app import crear_app


def cliente(tmp_path, monkeypatch):
    monkeypatch.setattr(utils, "ARCHIVO_DATOS", tmp_path / "asistencia.json")
    return crear_app({"TESTING": True, "SECRET_KEY": "test"}).test_client()


def test_inicio_vacio(tmp_path, monkeypatch):
    respuesta = cliente(tmp_path, monkeypatch).get("/")
    assert respuesta.status_code == 200
    assert "Todavía no hay registros" in respuesta.get_data(as_text=True)


def test_crud_web(tmp_path, monkeypatch):
    web = cliente(tmp_path, monkeypatch)
    respuesta = web.post("/registrar", data={"empleado": "7", "fecha": "2026-09-28", "hora_entrada": "08:00", "hora_salida": "16:30"}, follow_redirects=True)
    assert "EMP007" in respuesta.get_data(as_text=True)
    assert "08h 30m" in respuesta.get_data(as_text=True)
    respuesta = web.post("/registros/EMP007/28/09/2026/editar", data={"hora_entrada": "09:00", "hora_salida": "17:00"}, follow_redirects=True)
    assert "09:00" in respuesta.get_data(as_text=True)
    respuesta = web.post("/registros/EMP007/28/09/2026/eliminar", follow_redirects=True)
    assert "0 registros" in respuesta.get_data(as_text=True)


def test_rechaza_duplicado_completo(tmp_path, monkeypatch):
    web = cliente(tmp_path, monkeypatch)
    datos = {"empleado": "1", "fecha": "2026-09-28", "hora_entrada": "08:00", "hora_salida": "16:00"}
    web.post("/registrar", data=datos)
    respuesta = web.post("/registrar", data=datos, follow_redirects=True)
    assert "ya tiene una jornada completa" in respuesta.get_data(as_text=True)
