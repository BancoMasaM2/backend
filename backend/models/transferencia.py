from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from backend.database.connection import Base


def _utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Transferencia(Base):
    __tablename__ = "transferencias"

    id = Column(Integer, primary_key=True, index=True)
    origen_id = Column(Integer, ForeignKey("cuentas.id"), nullable=True)
    destino_id = Column(Integer, ForeignKey("cuentas.id"), nullable=True)
    monto = Column(Float, nullable=False)
    moneda = Column(String(3), nullable=False)
    fecha = Column(DateTime, default=_utcnow)
    estado = Column(String(20), default="completada")
