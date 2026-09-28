# 🕒 Control de Asistencia Web

Aplicación web ligera desarrollada con Python y Flask para la gestión, registro e inspección de jornadas laborales de empleados. Los datos se almacenan en un archivo `asistencia.json` persistente en el servidor.

---

## 🚀 Características Principales

* 📝 **Fichajes y Validaciones:** Registro de entrada y salida con prevención automática de duplicados por día.
* ✏️ **Edición y Borrado:** Modificación y eliminación directa de fichajes desde la interfaz web.
* 📊 **Dashboard con KPIs:** Tarjetas métricas globales que muestran fichajes totales, jornadas del día, empleados únicos, fichajes pendientes y horas totales computadas.
* 👤 **Informe por Empleado:** Vista individualizada para consultar el historial y el sumatorio de horas trabajadas por cada trabajador.
* 🔍 **Buscador:** Filtro en tiempo real por ID de empleado o fecha.
* 🔍 **Visor JSON integrador:** Inspección gráfica del estado real del archivo `asistencia.json` y opción de descarga directa.
* 🎨 **Estilos Centralizados:** Diseño uniforme en todas las pantallas cargado desde `static/styles.css` e icono del sitio `static/favicon.svg`.

---

## 📁 Estructura del Proyecto

```text
control-asistencia/
├── app.py                  # Servidor principal Flask y definición de rutas
├── static/
│   ├── styles.css          # Hoja de estilos CSS centralizada
│   └── favicon.svg         # Icono de la aplicación web
├── templates/
│   ├── nav.html            # Menú de navegación común
│   ├── index.html          # Página principal (Formulario + Tabla de fichajes)
│   ├── dashboard.html      # Métricas y estadísticas globales
│   ├── empleado.html       # Ficha de historial por empleado
│   └── visor_json.html     # Visor e inspección de datos raw
└── src/
    ├── gestor.py           # Lógica de negocio (registrar, buscar, actualizar, borrar)
    ├── utils.py            # Utilidades de persistencia (cargado/guardado JSON) y cálculo de horas
    └── data/
        └── asistencia.json # Base de datos en formato JSON
```

---

## 🛠️ Requisitos Previos

* Python 3.8 o superior.
* Entorno virtual de Python (recomendado).

---

## ⚙️ Instalación y Configuración

1. Clonar o descargar el proyecto en tu equipo local.

2. Crear y activar un entorno virtual (opcional pero recomendable):

   * En **Windows**:
     ```bash
     python -m venv venv
     venv\Scripts\activate
     ```

   * En **macOS / Linux**:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. Instalar Flask:
   ```bash
   pip install flask
   ```

---

## 🏃‍♂️ Cómo Ejecutar la Aplicación

1. Inicia el servidor desde la raíz del proyecto ejecutando:
   ```bash
   python app.py
   ```

2. Abre tu navegador web e ingresa a la siguiente dirección:
   `http://127.0.0.1:5000`

---

## 🌐 Rutas de la Aplicación

| Ruta | Descripción |
| :--- | :--- |
| `/` | Vista principal con el formulario de fichaje, tabla general, edición, eliminación y buscador. |
| `/dashboard` | Resumen ejecutivo con las métricas globales del sistema. |
| `/empleado/<id_emp>` | Historial y horas totales acumuladas por un empleado específico. |
| `/visor-json` | Vista del contenido en código crudo de `asistencia.json`. |
| `/descargar` | Endpoint para descargar una copia local del archivo `asistencia.json`. |