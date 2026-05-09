# app/routers/profesional.py
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from app.database import get_db_connection
from datetime import datetime, date
import sqlite3

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# --- RUTAS DE NAVEGACIÓN ---

@router.get("/dashboard-ps")
async def dashboard_ps(request: Request):
    return templates.TemplateResponse(
        request=request, 
        name="profesional/dashboard_ps.html",
        context={"mostrar_cerrar_sesion": True}
    )

@router.get("/profesional/paciente_evaluaciones/{paciente_id}")
async def obtener_evaluaciones_paciente_ps(paciente_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Buscamos todas las evaluaciones de este paciente, ordenadas por ID 
    cursor.execute("SELECT nombre, fecha_nacimiento FROM pacientes WHERE id = ?", (paciente_id,))
    paciente_info = cursor.fetchone()
    
    if not paciente_info:
        conn.close()
        raise HTTPException(status_code=404, detail="Paciente no encontrado en el sistema.")
        
    nombre_paciente = paciente_info["nombre"]
    fecha_nac_str = paciente_info["fecha_nacimiento"]
    
    # Calculamos la edad a partir de la fecha de nacimiento
    edad_paciente = "--"
    if fecha_nac_str:
        try:
            # Convertimos el texto a un formato de fecha de Python
            fecha_nac = datetime.strptime(fecha_nac_str, "%Y-%m-%d").date()
            hoy = datetime.today().date()
            # Restamos los años y ajustamos si aún no cumple años en el año actual
            edad_paciente = hoy.year - fecha_nac.year - ((hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day))
        except ValueError:
            # Si por alguna razón el texto no viene en ese formato, evitamos que se rompa
            edad_paciente = "ND"

    # Evaluaciones en la tabla 'sintomas'
    cursor.execute("""
        SELECT fecha, puntuacion_total, detalle_respuestas 
        FROM sintomas 
        WHERE paciente_id = ? 
        ORDER BY id ASC
    """, (paciente_id,))
    
    resultados = cursor.fetchall()
    conn.close()

    # Preparamos las listas
    fechas = []
    puntuaciones = []
    ultimo_detalle = None

    for fila in resultados:
        fechas.append(fila["fecha"])
        puntuaciones.append(fila["puntuacion_total"])
        ultimo_detalle = fila["detalle_respuestas"]

    # 3. Enviamos TODO al HTML
    return {
        "nombre": nombre_paciente,
        "edad": edad_paciente,
        "fechas": fechas,
        "puntuaciones": puntuaciones,
        "ultimo_detalle": ultimo_detalle
    }

# RUTA VISUAL: Solo entrega el archivo HTML al navegador
@router.get("/asignar-ejercicios")
async def vista_asignar_ejercicios(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="profesional/asignar_ejercicios.html",
        context={"mostrar_cerrar_sesion": False}
    )

# RUTA DE DATOS (API): Le da la lista de ejercicios al HTML
@router.get("/api/lista_ejercicios")
async def obtener_lista_ejercicios():
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre FROM ejercicios")
    resultados = cursor.fetchall()
    conn.close()
    
    return [{"id": fila["id"], "nombre": fila["nombre"]} for fila in resultados]

# RUTA DE SELECCIÓN: Sirve para que el HTML sepa qué casillas "palomear"
@router.get("/api/ejercicios_asignados/{paciente_id}")
async def obtener_ejercicios_asignados(paciente_id: str):
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT ejercicio_id FROM asignaciones_ejercicios WHERE paciente_id = ?", (paciente_id,))
    resultados = cursor.fetchall()
    conn.close()
    
    # Esto devuelve una lista simple de los IDs guardados, ej: [1, 3]
    return [fila["ejercicio_id"] for fila in resultados]

# RUTA DE GUARDADO (API): Recibe el plan del médico y lo guarda en la base de datos
@router.post("/api/guardar_plan")
async def guardar_plan(datos: dict):
    paciente_id = datos.get("paciente_id")
    ejercicios_ids = datos.get("ejercicios") # Lista de IDs que marcó el médico
    hoy = date.today().isoformat()
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # Limpia las asignaciones viejas de este paciente para no duplicar
        cursor.execute("DELETE FROM asignaciones_ejercicios WHERE paciente_id = ?", (paciente_id,))
        
        # Inserta los nuevos ejercicios marcados
        for ej_id in ejercicios_ids:
            cursor.execute("""
                INSERT INTO asignaciones_ejercicios (paciente_id, ejercicio_id, fecha_asignacion)
                VALUES (?, ?, ?)
            """, (paciente_id, ej_id, hoy))
        
        # Guarda los cambios
        conn.commit()
        return {"status": "ok", "mensaje": "Plan actualizado"}
        
    finally:
        conn.close()

# RUTA Muestra la historia clínica al médico
@router.get("/profesional/historia-clinica/{paciente_id}")
async def vista_historial_medico(request: Request, paciente_id: str):
    return templates.TemplateResponse(
        request=request, 
        name="paciente/historia_clinica.html", 
        context={"paciente_id_medico": paciente_id, "modo_medico": True}
    )