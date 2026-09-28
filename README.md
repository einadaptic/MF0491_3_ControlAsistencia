# Control de asistencia

Aplicación web en Flask para registrar, consultar, filtrar, actualizar y eliminar fichajes. También conserva la interfaz de consola original.

## Instalación y ejecución

```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python src/app.py
```

Abre `http://127.0.0.1:5000`. Los datos se guardan en `src/data/asistencia.json`. La versión de consola se ejecuta con `python src/main.py`.

## Pruebas

```bash
pytest -q
```

## Reparto del trabajo

| Integrante | Responsabilidad | Archivos principales |
|---|---|---|
| 1 | Inicio y estadísticas | `templates/inicio.html`, ruta `/` |
| 2 | Registro de asistencias | `templates/registrar.html`, ruta `/registrar` |
| 3 | Consulta y filtros | `templates/registros.html`, ruta `/registros` |
| 4 | Actualización y eliminación | `templates/editar.html`, rutas de editar/eliminar |
| 5 | Backend Python y conexión con HTML | `app.py`, `gestor.py`, `utils.py` |
| 6 | Diseño común y adaptación móvil | `base.html`, `static/css`, `static/js` |
| 7 | Pruebas, integración y documentación | `tests/`, `README.md`, `requirements.txt` |
