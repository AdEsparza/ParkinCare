import sqlite3

def crear_db():
    conn = sqlite3.connect("parkincare.db")
    cursor = conn.cursor()

    # Tabla para Pacientes
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pacientes(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT,
        fecha_nacimiento TEXT,
        correo TEXT UNIQUE,
        password TEXT
    )
    """)

    # Tabla para Personal de Salud (PS)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS personal_salud(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT,
        correo TEXT UNIQUE,
        cedula TEXT,
        password TEXT
    )
    """)

    # Tabla para el Historial de Síntomas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sintomas(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        paciente_id INTEGER,
        fecha TEXT,
        nivel_temblor INTEGER,
        nivel_rigidez INTEGER,
        notas TEXT,
        FOREIGN KEY(paciente_id) REFERENCES pacientes(id)
    )
    """)

    # Tabla para Historial clínico
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS historia_clinica(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        paciente_id INTEGER,
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
        antecedentes_familiares TEXT, -- Guardaremos una lista separada por comas
        antecedentes_personales TEXT,  -- Guardaremos una lista separada por comas
        FOREIGN KEY(paciente_id) REFERENCES pacientes(id)
    )
    """)

    conn.commit()
    conn.close()