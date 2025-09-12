from sqlalchemy import Column, String, Date, Numeric, Integer, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
from .db import Base

class Empresa(Base):
    __tablename__ = "empresa"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    razon_social = Column(String, nullable=False)
    cuit = Column(String(11), nullable=False)
    condicion_iva = Column(String, nullable=False)

class Documento(Base):
    __tablename__ = "documento"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    empresa_id = Column(UUID(as_uuid=True), ForeignKey("empresa.id"))
    tipo = Column(String, nullable=False)
    pv = Column(Integer)
    numero = Column(Integer)
    fecha_emision = Column(Date)
    moneda = Column(String, default="ARS")
    total = Column(Numeric(18,2))
    meta = Column(JSONB, default={})  # netos, iva por alícuota, etc.
    hash_archivo = Column(String, unique=True)
    ruta_archivo = Column(Text)