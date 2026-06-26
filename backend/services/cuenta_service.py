from sqlalchemy.orm import Session
from backend.models.cuenta import Cuenta


def obtener_cuentas_usuario(db: Session, usuario_id: int) -> list[Cuenta]:
    return db.query(Cuenta).filter(Cuenta.usuario_id == usuario_id).all()


def obtener_cuenta(db: Session, usuario_id: int, moneda: str) -> Cuenta | None:
    return (
        db.query(Cuenta)
        .filter(Cuenta.usuario_id == usuario_id, Cuenta.moneda == moneda)
        .first()
    )
