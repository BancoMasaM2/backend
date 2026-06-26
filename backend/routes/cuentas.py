from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database.connection import get_db
from backend.services.cuenta_service import obtener_cuentas_usuario, obtener_cuenta

router = APIRouter(prefix="/api/cuentas", tags=["cuentas"])


@router.get("/{usuario_id}")
def get_cuentas(usuario_id: int, db: Session = Depends(get_db)):
    cuentas = obtener_cuentas_usuario(db, usuario_id)
    return [{"id": c.id, "moneda": c.moneda, "saldo": c.saldo} for c in cuentas]


@router.get("/{usuario_id}/{moneda}")
def get_cuenta(usuario_id: int, moneda: str, db: Session = Depends(get_db)):
    moneda = moneda.upper()
    if moneda not in ("ARS", "USD"):
        raise HTTPException(status_code=400, detail="Moneda debe ser ARS o USD")

    cuenta = obtener_cuenta(db, usuario_id, moneda)
    if cuenta is None:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada")
    return {"id": cuenta.id, "moneda": cuenta.moneda, "saldo": cuenta.saldo}
