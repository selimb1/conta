from pydantic import BaseModel
from typing import Dict, List, Any

class Validacion(BaseModel):
    regla: str
    severidad: str
    passed: bool
    mensaje: str

class AsientoLinea(BaseModel):
    cuenta: str
    descripcion: str
    debe: float
    haber: float

class AsientoPropuesto(BaseModel):
    fecha: str | None
    lineas: List[AsientoLinea]
    referencia_documento: str

class LibrosDDJJ(BaseModel):
    iva: Dict[str, Any]
    ganancias: Dict[str, Any]
    iibb: Dict[str, Any]

class ProcesamientoOut(BaseModel):
    documento_id: str
    validaciones: List[Validacion]
    campos_extraidos: Dict[str, Any]
    asiento_propuesto: AsientoPropuesto
    alertas: List[str]
    libros_y_ddjj_preliminares: LibrosDDJJ
    archivos_exportables: List[str]