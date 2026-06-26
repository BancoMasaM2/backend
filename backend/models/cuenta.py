from sqlalchemy import Column, Integer, String, Float, ForeignKey, UniqueConstraint
from backend.database.connection import Base


class Cuenta(Base):
    __tablename__ = "cuentas"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    moneda = Column(String(3), nullable=False)
    saldo = Column(Float, default=0.0)

    __table_args__ = (UniqueConstraint("usuario_id", "moneda", name="uq_usuario_moneda"),)
