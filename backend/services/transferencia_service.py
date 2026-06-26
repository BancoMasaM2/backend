from sqlalchemy.orm import Session
from backend.models.usuario import Usuario
from backend.models.cuenta import Cuenta
from backend.models.transferencia import Transferencia
from backend.utils.email_sender import enviar_email
from backend.services.usuario_service import obtener_usuario_por_alias


def _enviar_codigo_transferencia(email: str, codigo: str, monto: float, moneda: str, destino_alias: str) -> None:
    asunto = "Código de confirmación - Transferencia"
    cuerpo = (
        f"Estás por transferir ${monto:.2f} {moneda} a '{destino_alias}'.\n\n"
        f"Tu código de confirmación es: {codigo}\n\nVálido por 15 minutos."
    )
    try:
        enviar_email(email, asunto, cuerpo)
    except Exception as e:
        raise ValueError(f"Error al enviar el email: {e}")


def iniciar_transferencia(db: Session, origen_usuario_id: int, destino_alias: str, moneda: str, monto: float) -> dict:
    origen = db.query(Usuario).filter(Usuario.id == origen_usuario_id).first()
    if not origen:
        raise ValueError("Usuario origen no encontrado")

    destino = obtener_usuario_por_alias(db, destino_alias)
    if not destino:
        raise ValueError("Alias de destino no encontrado")
    if destino.id == origen_usuario_id:
        raise ValueError("No podés transferirte a vos mismo")

    cuenta_origen = db.query(Cuenta).filter(Cuenta.usuario_id == origen_usuario_id, Cuenta.moneda == moneda).first()
    if not cuenta_origen:
        raise ValueError(f"No tenés cuenta en {moneda}")
    if cuenta_origen.saldo < monto:
        raise ValueError("Saldo insuficiente")

    codigo = origen.generar_codigo_transferencia()
    origen.transfer_destino_alias = destino_alias
    origen.transfer_moneda = moneda
    origen.transfer_monto = monto
    db.commit()

    _enviar_codigo_transferencia(origen.email, codigo, monto, moneda, destino_alias)

    return {"mensaje": "Código de confirmación enviado a tu email"}


def confirmar_transferencia(db: Session, origen_usuario_id: int, codigo: str) -> dict:
    origen = db.query(Usuario).filter(Usuario.id == origen_usuario_id).first()
    if not origen:
        raise ValueError("Usuario origen no encontrado")
    if not origen.verificar_codigo_transferencia(codigo):
        raise ValueError("Código inválido o expirado")

    destino_alias = origen.transfer_destino_alias
    moneda = origen.transfer_moneda
    monto = origen.transfer_monto

    if not destino_alias or not moneda or not monto:
        raise ValueError("No hay una transferencia pendiente")

    destino = obtener_usuario_por_alias(db, destino_alias)
    if not destino:
        raise ValueError("Alias de destino no encontrado")

    cuenta_origen = db.query(Cuenta).filter(Cuenta.usuario_id == origen.id, Cuenta.moneda == moneda).first()
    if not cuenta_origen:
        raise ValueError("Cuenta origen no encontrada")
    if cuenta_origen.saldo < monto:
        raise ValueError("Saldo insuficiente")

    cuenta_destino = db.query(Cuenta).filter(Cuenta.usuario_id == destino.id, Cuenta.moneda == moneda).first()
    if not cuenta_destino:
        cuenta_destino = Cuenta(usuario_id=destino.id, moneda=moneda, saldo=0.0)
        db.add(cuenta_destino)
        db.flush()

    cuenta_origen.saldo -= monto
    cuenta_destino.saldo += monto

    transferencia = Transferencia(
        origen_id=cuenta_origen.id,
        destino_id=cuenta_destino.id,
        monto=monto,
        moneda=moneda,
        estado="completada",
    )
    db.add(transferencia)

    origen.transfer_codigo = None
    origen.transfer_codigo_expiracion = None
    origen.transfer_destino_alias = None
    origen.transfer_moneda = None
    origen.transfer_monto = None
    db.commit()

    return {
        "transferencia_id": transferencia.id,
        "origen_saldo": cuenta_origen.saldo,
        "destino_saldo": cuenta_destino.saldo,
    }
