from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Optional
import json
import sqlite3

# Importación de funciones desde database.py
from app.database import get_db_connection, generar_id_usuario

router = APIRouter()

templates = Jinja2Templates(directory="templates")

# --- MODELOS DE DATOS ---
class LoginData(BaseModel):
    correo: str
    password: str

class RegistroPaciente(BaseModel):
    nombre: str
    fecha_nacimiento: str
    correo: str
    password: str

class RegistroPS(BaseModel):
    nombre: str
    correo: str
    cedula: str
    password: str

class HistoriaClinicaModel(BaseModel):
    paciente_id: str
    edad: int
    sexo: str
    peso: float
    altura: float
    estudios: Optional[str] = ""
    ocupacion: Optional[str] = ""
    toma_alcohol: bool
    fuma: bool
    ejercicio: bool
    actividades_ludicas: Optional[str] = ""
    antecedentes_familiares: List[str]
    antecedentes_personales: List[str]


# --- RUTAS DE NAVEGACIÓN ---
@router.get("/", response_class=HTMLResponse)
async def mostrar_login(request: Request):
    return templates.TemplateResponse(
        request=request, 
        name="auth/login.html",
        context={"mostrar_cerrar_sesion": False}
    )

@router.get("/vista-registro", response_class=HTMLResponse)
async def vista_registro(request: Request):
    return templates.TemplateResponse(
        request=request, 
        name="auth/registro.html",
        context={"mostrar_cerrar_sesion": False}
    )


# --- RUTAS DE API (BACK-END) ---

# 1. REGISTRO DE PACIENTE
@router.post("/registro/paciente")
async def registrar_paciente(datos: RegistroPaciente):
    nuevo_id = generar_id_usuario("paciente")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO pacientes (id, nombre, fecha_nacimiento, correo, password) VALUES (?, ?, ?, ?, ?)",
            (nuevo_id, datos.nombre, datos.fecha_nacimiento, datos.correo, datos.password)
        )
        conn.commit()
        conn.close()
        return {"mensaje": "Paciente registrado correctamente", "id": nuevo_id}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Este correo ya está registrado.")

# 2. REGISTRO DE PROFESIONAL
@router.post("/registro/ps")
async def registrar_ps(datos: RegistroPS):
    nuevo_id = generar_id_usuario("profesional")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO personal_salud (id, nombre, correo, cedula, password) VALUES (?, ?, ?, ?, ?)",
            (nuevo_id, datos.nombre, datos.correo, datos.cedula, datos.password)
        )
        conn.commit()
        conn.close()
        return {"mensaje": "Profesional registrado correctamente", "id": nuevo_id}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Este correo ya está registrado.")

# 3. INICIO DE SESIÓN
@router.post("/login")
async def iniciar_sesion(datos: LoginData):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Intento 1: Buscar en la tabla de pacientes
    cursor.execute(
        "SELECT id, nombre FROM pacientes WHERE correo = ? AND password = ?", 
        (datos.correo, datos.password)
    )
    usuario = cursor.fetchone()
    
    if usuario:
        conn.close()
        return {
            "mensaje": "Inicio de sesión exitoso",
            "id": usuario["id"],
            "nombre": usuario["nombre"],
            "tipo": "paciente" # Le decimos al Frontend que es paciente
        }
        
    # Intento 2: Buscar en la tabla de personal de salud
    cursor.execute(
        "SELECT id, nombre FROM personal_salud WHERE correo = ? AND password = ?", 
        (datos.correo, datos.password)
    )
    usuario = cursor.fetchone()
    conn.close()
    
    if usuario:
        return {
            "mensaje": "Inicio de sesión exitoso",
            "id": usuario["id"],
            "nombre": usuario["nombre"],
            "tipo": "profesional" 
        }
        
    # Intento 3: Si no está en ninguna tabla, las credenciales son incorrectas
    raise HTTPException(status_code=401, detail="Correo o contraseña incorrectos")


# 4. ELIMINAR CUENTA
@router.delete("/eliminar_cuenta/{usuario_id}")
async def eliminar_cuenta(usuario_id: str):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if usuario_id.endswith("A"):
            # Si es paciente, primero borramos su historia clínica para no dejar basura
            cursor.execute("DELETE FROM historia_clinica WHERE paciente_id = ?", (usuario_id,))
            # Luego borramos al paciente
            cursor.execute("DELETE FROM pacientes WHERE id = ?", (usuario_id,))
        else:
            # Si es profesional de la salud
            cursor.execute("DELETE FROM personal_salud WHERE id = ?", (usuario_id,))
        
        conn.commit()
        conn.close()
        return {"mensaje": "Cuenta y datos eliminados correctamente"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en el servidor: {str(e)}")