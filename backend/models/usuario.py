import random
from datetime import datetime, timedelta, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from backend.database.connection import Base


def _utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def generar_codigo() -> str:
    return str(random.randint(100000, 999999))


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    fecha_creacion = Column(DateTime, default=_utcnow)
    verificado = Column(Boolean, default=False)
    codigo_verificacion = Column(String(6), nullable=True)
    codigo_expiracion = Column(DateTime, nullable=True)
    alias = Column(String(50), unique=True, nullable=True, index=True)
    transfer_codigo = Column(String(6), nullable=True)
    transfer_codigo_expiracion = Column(DateTime, nullable=True)
    transfer_destino_alias = Column(String(50), nullable=True)
    transfer_moneda = Column(String(3), nullable=True)
    transfer_monto = Column(Float, nullable=True)

    def generar_nuevo_codigo(self, expiracion_minutos: int = 15) -> str:
        self.codigo_verificacion = generar_codigo()
        self.codigo_expiracion = _utcnow() + timedelta(minutes=expiracion_minutos)
        return self.codigo_verificacion

    def verificar_codigo(self, codigo: str) -> bool:
        if not self.codigo_verificacion or not self.codigo_expiracion:
            return False
        if _utcnow() > self.codigo_expiracion:
            return False
        return self.codigo_verificacion == codigo

    def generar_codigo_transferencia(self) -> str:
        self.transfer_codigo = generar_codigo()
        self.transfer_codigo_expiracion = _utcnow() + timedelta(minutes=15)
        return self.transfer_codigo

    def verificar_codigo_transferencia(self, codigo: str) -> bool:
        if not self.transfer_codigo or not self.transfer_codigo_expiracion:
            return False
        if _utcnow() > self.transfer_codigo_expiracion:
            return False
        return self.transfer_codigo == codigo
