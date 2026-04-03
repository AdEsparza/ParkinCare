from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

import sqlite3

from app.database import crear_db
from app.models import PacienteRegistro, PSRegistro, RegistroSintoma

app = FastAPI(title="ParkinCare API")
templates = Jinja2Templates(directory="templates")

# Permitir conexión frontend (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar base de datos
crear_db()

# Servir archivos estáticos (CSS, JS, imágenes)
app.mount("/static", StaticFiles(directory="static"), name="static")

# ---------------------------------------------------------
# ENDPOINTS (RUTAS) DEL SISTEMA
# ---------------------------------------------------------

# --- RUTAS DE NAVEGACIÓN (FRONT-END) ---

# Ruta para la página de inicio de sesión (Flujo 1 y 9)
@app.get("/")
def home():
    return FileResponse("templates/index.html")

# Ruta para la página de registro (Flujo 2)
@app.get("/vista-registro")
def vista_registro():
    return FileResponse("templates/registro.html")

# Rutas para los dashboards
@app.get("/dashboard-paciente")
def dashboard_paciente():
    return FileResponse("templates/dashboard_pac.html")

@app.get("/dashboard-ps")
def dashboard_ps():
    return FileResponse("templates/dashboard_ps.html")

@app.get("/vista-sintomas")
async def vista_sintomas(request: Request):
    return templates.TemplateResponse(request=request, name="sintomas.html")


# --- RUTAS DE API (BACK-END PARA RECIBIR DATOS) ---

# Ruta para recibir los datos del formulario de Paciente
@app.post("/registro/paciente")
async def registrar_paciente(datos: dict):
    # Por ahora solo imprimimos los datos en la terminal para que veas que llegan
    print("Datos recibidos del paciente:", datos)
    
    # Simulamos que se guardó en la base de datos y devolvemos éxito
    return {
        "mensaje": "Paciente registrado correctamente", 
        "id": 101 # ID simulado
    }

# Ruta para recibir los datos del formulario de Personal de Salud
@app.post("/registro/ps")
async def registrar_ps(datos: dict):
    print("Datos recibidos del PS:", datos)
    
    return {
        "mensaje": "Personal de salud registrado correctamente", 
        "id": 201 # ID simulado
    }

# Contadores globales para simular el autoincremento de la base de datos
contador_pacientes = 0
contador_ps = 0

@app.post("/registro/paciente")
async def registrar_paciente(datos: dict):
    global contador_pacientes
    
    # Aumentamos el contador en 1 cada vez que alguien se registra
    contador_pacientes += 1
    
    # Formateamos el número para que siempre tenga 3 dígitos (ej. 1 -> "001")
    id_formateado = f"{contador_pacientes:03d}"
    
    print(f"Nuevo Paciente registrado con ID: {id_formateado} | Datos: {datos}")
    
    return {
        "mensaje": "Paciente registrado correctamente", 
        "id": id_formateado
    }

@app.post("/registro/ps")
async def registrar_ps(datos: dict):
    global contador_ps
    
    contador_ps += 1
    id_formateado = f"{contador_ps:03d}"
    
    print(f"Nuevo PS registrado con ID: {id_formateado} | Datos: {datos}")
    
    return {
        "mensaje": "Personal de salud registrado correctamente", 
        "id": id_formateado
    }

# Para guardar evaluación
@app.post("/guardar_evaluacion")
async def guardar_evaluacion(request: Request):
    form_data = await request.form()
    
    # Extraemos y sumamos los puntos de cada bloque
    try:
        b1 = int(form_data.get("sentimiento_general", 0))
        b2 = sum([int(form_data.get(f"motor_{i}", 0)) for i in range(1, 6)])
        b3 = sum([int(form_data.get(f"nomotor_{i}", 0)) for i in range(1, 6)])
        b4 = int(form_data.get("independencia", 0))
        b5 = sum([int(form_data.get(f"cognitivo_{i}", 0)) for i in range(1, 5)])
        
        score_total = b1 + b2 + b3 + b4 + b5

        print(f"Evaluación recibida. Score total del paciente: {score_total}")
        
        return RedirectResponse(url=f"/dashboard-paciente?score={score_total}", status_code=303)
        
    except Exception as e:
        return {"error": str(e)}
    
# --- RUTAS DE HISTORIA CLÍNICA ---

# 1. Ruta para mostrar la página (traducir el Jinja2)
@app.get("/vista-historial")
async def vista_historial(request: Request):
    return templates.TemplateResponse(request=request, name="historia_clinica.html")

# 2. Ruta para recibir los datos por JSON desde JavaScript
@app.post("/guardar_historia")
async def guardar_historia(datos: dict):
    # Aquí en el futuro guardarás esto en SQLite
    print("📋 Nueva Historia Clínica recibida:")
    print(datos)
    
    # Respondemos con éxito a JavaScript para que haga la redirección
    return {"mensaje": "Historia clínica procesada correctamente"}