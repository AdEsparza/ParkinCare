from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import FileResponse, RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from app.database import get_db_connection
import sqlite3
from app.models import HistoriaClinica
from datetime import date
import json

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/dashboard-paciente")
async def dashboard_paciente(request: Request):
    return templates.TemplateResponse(
        request=request, 
        name="paciente/dashboard_pac.html",
        context={"mostrar_cerrar_sesion": True}
    )

@router.get("/vista-sintomas")
async def vista_sintomas(request: Request):
    return templates.TemplateResponse(request=request, name="paciente/sintomas.html")

@router.get("/historia-clinica")
async def vista_historial(request: Request):
    return templates.TemplateResponse(request=request, name="paciente/historia_clinica.html")

@router.post("/guardar_historia")
async def guardar_historia(datos: HistoriaClinica):
    print(f"📢 Intentando guardar historia para el ID: '{datos.paciente_id}'")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Convertir las listas a texto para SQLite
        ant_fam_str = ",".join(datos.antecedentes_familiares)
        ant_pers_str = ",".join(datos.antecedentes_personales)
        
        cursor.execute("""
            REPLACE INTO historia_clinica (
                paciente_id, edad, sexo, peso, altura, estudios, ocupacion, 
                toma_alcohol, fuma, ejercicio, actividades_ludicas, 
                antecedentes_familiares, antecedentes_personales
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datos.paciente_id, datos.edad, datos.sexo, datos.peso, datos.altura,
            datos.estudios, datos.ocupacion, datos.toma_alcohol, datos.fuma,
            datos.ejercicio, datos.actividades_ludicas, ant_fam_str, ant_pers_str
        ))
        
        conn.commit()
        conn.close()
        return {"mensaje": "Historia clínica guardada correctamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en el servidor: {str(e)}")

@router.get("/obtener_historia/{paciente_id}")
async def obtener_historia(paciente_id: str):
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    fila = cursor.execute("SELECT * FROM historia_clinica WHERE paciente_id = ?", (paciente_id,)).fetchone()
    conn.close()
    
    if fila:
        datos = dict(fila)
        # Texto de vuelta a listas para que el HTML las entienda
        datos["antecedentes_familiares"] = datos["antecedentes_familiares"].split(",") if datos["antecedentes_familiares"] else []
        datos["antecedentes_personales"] = datos["antecedentes_personales"].split(",") if datos["antecedentes_personales"] else []
        datos["toma_alcohol"] = bool(datos.get("toma_alcohol", False))
        datos["fuma"] = bool(datos.get("fuma", False))
        datos["ejercicio"] = bool(datos.get("ejercicio", False))
        return datos
    
    return {"error": "No se encontró historia"}

@router.post("/guardar_evaluacion")
async def guardar_evaluacion(request: Request):
    form_data = await request.form()
    paciente_id = form_data.get("paciente_id")

    score_total = 0
    respuestas_individuales = {}

    for campo, valor in form_data.items():
        if campo != "paciente_id":
            # Guardamos la respuesta (ej. "motor_1": 2)
            respuestas_individuales[campo] = int(valor) if valor.isdigit() else valor
            
        if valor.isdigit():
            score_total += int(valor)
            
    print(f"Puntuación calculada: {score_total}")

    # Respuestas en formato texto (JSON) para la base de datos
    detalle_json = json.dumps(respuestas_individuales)

    hoy = date.today()
    meses = {
        1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
        5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
        9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
    }
    fecha_sencilla = f"{hoy.day} de {meses[hoy.month]} {hoy.year}"

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO sintomas (paciente_id, fecha, detalle_respuestas, puntuacion_total) VALUES (?, ?, ?, ?)",
        (paciente_id, fecha_sencilla, detalle_json, score_total)
    )
    conn.commit()
    conn.close()
    
    return RedirectResponse(url=f"/dashboard-paciente?score={score_total}", status_code=303)

# RUTA PARA ALIMENTAR LA GRÁFICA DEL DASHBOARD
@router.get("/obtener_evaluaciones/{paciente_id}")
async def obtener_evaluaciones(paciente_id: str):
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row 
    cursor = conn.cursor()
    
    # Evaluaciones del paciente, ordenadas por ID
    registros = cursor.execute("""
        SELECT fecha, puntuacion_total 
        FROM sintomas 
        WHERE paciente_id = ? 
        ORDER BY id ASC
    """, (paciente_id,)).fetchall()
    
    conn.close()
    
    # Si no hay registros, se envian listas vacías
    if not registros:
        return {"fechas": [], "puntuaciones": []}
        
    # Se separan los datos en dos listas para que Chart.js las entienda
    fechas = [dict(row)["fecha"] for row in registros]
    puntuaciones = [dict(row)["puntuacion_total"] for row in registros]
    
    return {"fechas": fechas, "puntuaciones": puntuaciones}

@router.get("/vista-ejercicios")
async def vista_ejercicios(request: Request):
    return templates.TemplateResponse(
        request=request, 
        name="paciente/ejercicios_pac.html", 
        context={"mostrar_cerrar_sesion": True}
    )

@router.get("/api/rutina/{paciente_id}")
async def obtener_rutina_paciente(paciente_id: str):
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT e.nombre, e.descripcion, e.video_url 
        FROM asignaciones_ejercicios ae
        JOIN ejercicios e ON ae.ejercicio_id = e.id
        WHERE ae.paciente_id = ?
    """, (paciente_id,))
    
    resultados = cursor.fetchall()
    conn.close()
    
    rutina = []
    for fila in resultados:
        rutina.append({
            "nombre": fila["nombre"],
            "descripcion": fila["descripcion"],
            "video_url": fila["video_url"]
        })
        
    return rutina

# Ruta para anonimizar datos
@router.delete("/eliminar_cuenta/{paciente_id}")
async def eliminar_cuenta(paciente_id: str):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 1. Verificar si el paciente existe
        paciente = cursor.execute("SELECT id FROM pacientes WHERE id = ?", (paciente_id,)).fetchone()
        if not paciente:
            conn.close()
            raise HTTPException(status_code=404, detail="Paciente no encontrado")

        # 2. ANONIMIZACIÓN:
        cursor.execute("""
            UPDATE pacientes 
            SET nombre = ?, 
                correo = NULL, 
                fecha_nacimiento = NULL, 
                password = ? 
            WHERE id = ?
        """, ("Paciente Anonimizado", "cuenta_eliminada_" + paciente_id, paciente_id))
        
        # NOTA: No se afectan las tablas, el ID sigue siendo el mismo

        conn.commit()
        conn.close()
        return {"mensaje": "Cuenta anonimizada correctamente"}
        
    except Exception as e:
        print(f"Error al eliminar: {e}")
        raise HTTPException(status_code=500, detail="Error interno al procesar la solicitud")