# app/main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.database import crear_db

crear_db() # Inicialización de la base de datos

try:
    from app.routers import auth, paciente, profesional
except ImportError:
    from app.routers import auth, paciente, profesional

app = FastAPI(title="ParkinCare API")

# 1. CONFIGURACIÓN DE ARCHIVOS ESTÁTICOS
app.mount("/static", StaticFiles(directory="static"), name="static")


# 2. CONEXIÓN DE MÓDULOS (ROUTERS)
# Prefijo 'tags' ayuda a organizar la documentación automática (/docs)
app.include_router(auth.router, tags=["Autenticación"])
app.include_router(paciente.router, tags=["Pacientes"])
app.include_router(profesional.router, tags=["Personal de Salud"])


# 3. RUTA DE PRUEBA
@app.get("/health")
def check_health():
    return {"status": "ok", "message": "Servidor ParkinCare funcionando correctamente"}