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
    paciente_id: str
    fecha: str
    temblor: int
    marcha: int
    rigidez: int
    cognitivo: int
    puntuacion_total: int

class HistoriaClinica(BaseModel):
    paciente_id: str
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