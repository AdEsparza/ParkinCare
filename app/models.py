from pydantic import BaseModel
from typing import List, Optional

class PacienteRegistro(BaseModel):
    nombre: str
    fecha_nacimiento: str
    correo: str
    password: str

class PSRegistro(BaseModel):
    nombre: str
    correo: str
    cedula: str
    password: str

class RegistroSintoma(BaseModel):
    paciente_id: int
    fecha: str
    nivel_temblor: int  # Ej. escala del 1 al 10
    nivel_rigidez: int  # Ej. escala del 1 al 10
    notas: str

class HistoriaClinica(BaseModel):
    paciente_id: int
    edad: int
    sexo: str
    peso: float
    altura: float
    estudios: str
    ocupacion: str
    toma_alcohol: bool
    fuma: bool
    ejercicio: bool
    actividades_ludicas: Optional[str] = None
    antecedentes_familiares: List[str]
    antecedentes_personales: List[str]