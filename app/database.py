import sqlite3
import random

# 1. Función para conectar (con soporte para nombres de columnas)
def get_db_connection():
    conn = sqlite3.connect("parkincare.db")
    conn.row_factory = sqlite3.Row 
    return conn

# 2. Generador de ID personalizado (pkc000A / pkc000B)
def generar_id_usuario(tipo: str):
    numero = f"{random.randint(0, 999):03d}"
    letra = "A" if tipo == "paciente" else "B"
    return f"pkc{numero}{letra}"

# 3. Creación de todas las tablas
def crear_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Tabla para Pacientes 
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pacientes(
        id TEXT PRIMARY KEY,
        nombre TEXT,
        fecha_nacimiento TEXT,
        correo TEXT UNIQUE,
        password TEXT
    )
    """)

    # Tabla para Personal de Salud 
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS personal_salud(
        id TEXT PRIMARY KEY,
        nombre TEXT,
        correo TEXT UNIQUE,
        cedula TEXT,
        password TEXT
    )
    """)

    # Tabla para el Historial de Síntomas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sintomas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        paciente_id TEXT,
        fecha TEXT,
        detalle_respuestas TEXT,          
        puntuacion_total INTEGER
    )
    """)

    # Tabla para Historial clínico
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS historia_clinica (
        paciente_id TEXT PRIMARY KEY,
        edad INTEGER,
        sexo TEXT,
        peso REAL,
        altura REAL,
        estudios TEXT,
        ocupacion TEXT,
        toma_alcohol BOOLEAN,
        fuma BOOLEAN,
        ejercicio BOOLEAN,
        actividades_ludicas TEXT,
        antecedentes_familiares TEXT,
        antecedentes_personales TEXT,
        FOREIGN KEY (paciente_id) REFERENCES pacientes (id)
        )
    """)

    # Tabla de Catálogo de ejercicios
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ejercicios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT,
        descripcion TEXT,
        video_url TEXT
    )
    """)

    # Tabla de asignaciones (qué ejercicio tiene cada paciente)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS asignaciones_ejercicios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    paciente_id TEXT,
    ejercicio_id INTEGER,
    fecha_asignacion TEXT,
    FOREIGN KEY(ejercicio_id) REFERENCES ejercicios(id)
    )
    """)

    # Ejercicios iniciales
    cursor.execute("SELECT COUNT(*) FROM ejercicios")
    if cursor.fetchone()[0] == 0:
        ejercicios_iniciales = [
            ("Marcha por fases", "Realizar la marcha pasando el pie por encima de los conos, de forma lenta y que los dos pies toquen el espacio entre los conos.", "marcha_fases.mp4"),
            ("Marcha en zig zag", "Realizar la marcha por fases pero de un lado al otro del cono.", "marcha_zigzag.mp4"),
            ("Movimiento prono supino", "Los codos pegados al cuerpo, las manos sobre una superficie y las manos van a voltear a ver al techo y al piso.", "prono_supino.mp4"),
            ("Sentado inclinarse hacia adelante", "Sentado en una silla, tomar una pelota e inclinarse hacia adelante hasta tocar el suelo con la pelota.", "sentado_inclinarse.mp4"),
            ("Juego con resistencia", "Se coloca la liga abrazando las muñecas, quedando por dentro, y se va a tratar de alcanzar los círculos de colores.", "resistencia.mp4"),
            ("Tomar el vaso", "Se va a tratar de vaciar el líquido de un vaso a otro.", "tomar_vaso.mp4")
        ]
        cursor.executemany("INSERT INTO ejercicios (nombre, descripcion, video_url) VALUES (?, ?, ?)", ejercicios_iniciales)

    conn.commit()
    conn.close()