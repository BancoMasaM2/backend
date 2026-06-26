from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.database.connection import get_db
from backend.models.cuenta import Cuenta
from backend.models.transferencia import Transferencia
from backend.models.pago import Pago
from backend.services.transferencia_service import (
    iniciar_transferencia,
    confirmar_transferencia,
)

router = APIRouter(prefix="/api/operaciones", tags=["operaciones"])


class TransferirRequest(BaseModel):
    origen_usuario_id: int
    destino_usuario_id: int
    moneda: str
    monto: float


class IniciarTransferenciaRequest(BaseModel):
    origen_usuario_id: int
    destino_alias: str
    moneda: str
    monto: float


class ConfirmarTransferenciaRequest(BaseModel):
    origen_usuario_id: int
    codigo: str


class ConversionRequest(BaseModel):
    usuario_id: int
    monto_origen: float
    moneda_origen: str
    monto_destino: float
    moneda_destino: str
    tasa: float


class PagoRequest(BaseModel):
    usuario_id: int
    monto: float
    descripcion: str = ""


@router.post("/transferir")
def transferir(req: TransferirRequest, db: Session = Depends(get_db)):
    origen = (
        db.query(Cuenta)
        .filter(Cuenta.usuario_id == req.origen_usuario_id, Cuenta.moneda == req.moneda)
        .first()
    )
    if not origen:
        raise HTTPException(status_code=404, detail="Cuenta origen no encontrada")
    if origen.saldo < req.monto:
        raise HTTPException(status_code=400, detail="Saldo insuficiente")

    destino = (
        db.query(Cuenta)
        .filter(
            Cuenta.usuario_id == req.destino_usuario_id, Cuenta.moneda == req.moneda
        )
        .first()
    )
    if not destino:
        destino = Cuenta(
            usuario_id=req.destino_usuario_id, moneda=req.moneda, saldo=0.0
        )
        db.add(destino)
        db.flush()

    origen.saldo -= req.monto
    destino.saldo += req.monto

    transferencia = Transferencia(
        origen_id=origen.id,
        destino_id=destino.id,
        monto=req.monto,
        moneda=req.moneda,
        estado="completada",
    )
    db.add(transferencia)
    db.commit()

    return {
        "transferencia_id": transferencia.id,
        "origen_saldo": origen.saldo,
        "destino_saldo": destino.saldo,
    }


@router.post("/iniciar-transferencia")
def iniciar(req: IniciarTransferenciaRequest, db: Session = Depends(get_db)):
    try:
        resultado = iniciar_transferencia(db, req.origen_usuario_id, req.destino_alias, req.moneda, req.monto)
        return resultado
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/confirmar-transferencia")
def confirmar(req: ConfirmarTransferenciaRequest, db: Session = Depends(get_db)):
    try:
        resultado = confirmar_transferencia(db, req.origen_usuario_id, req.codigo)
        return {"estado": "completada", "detalle": resultado}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/conversion")
def conversion(req: ConversionRequest, db: Session = Depends(get_db)):
    cuenta_origen = (
        db.query(Cuenta)
        .filter(Cuenta.usuario_id == req.usuario_id, Cuenta.moneda == req.moneda_origen)
        .first()
    )
    if not cuenta_origen:
        raise HTTPException(status_code=404, detail="Cuenta origen no encontrada")
    if cuenta_origen.saldo < req.monto_origen:
        raise HTTPException(status_code=400, detail="Saldo insuficiente")

    cuenta_destino = (
        db.query(Cuenta)
        .filter(
            Cuenta.usuario_id == req.usuario_id, Cuenta.moneda == req.moneda_destino
        )
        .first()
    )
    if not cuenta_destino:
        cuenta_destino = Cuenta(
            usuario_id=req.usuario_id, moneda=req.moneda_destino, saldo=0.0
        )
        db.add(cuenta_destino)
        db.flush()

    cuenta_origen.saldo -= req.monto_origen
    cuenta_destino.saldo += req.monto_destino

    transferencia = Transferencia(
        origen_id=cuenta_origen.id,
        destino_id=cuenta_destino.id,
        monto=req.monto_origen,
        moneda=f"{req.moneda_origen}->{req.moneda_destino}",
        estado="completada",
    )
    db.add(transferencia)
    db.commit()

    return {
        "cuenta_origen_saldo": cuenta_origen.saldo,
        "cuenta_destino_saldo": cuenta_destino.saldo,
        "tasa": req.tasa,
    }


@router.post("/pago")
def pago(req: PagoRequest, db: Session = Depends(get_db)):
    cuenta = (
        db.query(Cuenta)
        .filter(Cuenta.usuario_id == req.usuario_id, Cuenta.moneda == "ARS")
        .first()
    )
    if not cuenta:
        raise HTTPException(status_code=404, detail="Cuenta ARS no encontrada")
    if cuenta.saldo < req.monto:
        raise HTTPException(status_code=400, detail="Saldo insuficiente")

    cuenta.saldo -= req.monto

    pago = Pago(
        usuario_id=req.usuario_id,
        monto=req.monto,
        descripcion=req.descripcion,
        estado="completada",
    )
    db.add(pago)
    db.commit()

    return {"pago_id": pago.id, "saldo_restante": cuenta.saldo}
