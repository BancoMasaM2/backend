from sqlalchemy.orm import Session
from sqlalchemy import or_
from backend.models.usuario import Usuario
from backend.models.cuenta import Cuenta
from backend.models.transferencia import Transferencia
from backend.models.pago import Pago


def obtener_usuario_por_id(db: Session, usuario_id: int) -> Usuario | None:
    return db.query(Usuario).filter(Usuario.id == usuario_id).first()


def obtener_usuario_por_alias(db: Session, alias: str) -> Usuario | None:
    return db.query(Usuario).filter(Usuario.alias == alias).first()


def actualizar_alias(db: Session, usuario_id: int, nuevo_alias: str) -> Usuario:
    existente = db.query(Usuario).filter(Usuario.alias == nuevo_alias).first()
    if existente and existente.id != usuario_id:
        raise ValueError("El alias ya está en uso")

    usuario = obtener_usuario_por_id(db, usuario_id)
    if not usuario:
        raise ValueError("Usuario no encontrado")

    usuario.alias = nuevo_alias
    db.commit()
    return usuario


def obtener_movimientos(db: Session, usuario_id: int) -> list[dict]:
    cuentas = db.query(Cuenta.id).filter(Cuenta.usuario_id == usuario_id).all()
    cuenta_ids = [c.id for c in cuentas]

    transferencias = (
        db.query(Transferencia)
        .filter(or_(Transferencia.origen_id.in_(cuenta_ids), Transferencia.destino_id.in_(cuenta_ids)))
        .all()
    ) if cuenta_ids else []

    pagos = db.query(Pago).filter(Pago.usuario_id == usuario_id).all()

    movimientos = []

    for t in transferencias:
        es_conversion = "->" in (t.moneda or "") and len(cuenta_ids) >= 2
        if es_conversion:
            movimientos.append({
                "id": f"T{t.id}",
                "tipo": "conversion",
                "concepto": f"Compra de {t.moneda.split('->')[1]}",
                "monto": t.monto,
                "moneda": t.moneda,
                "es_ingreso": False,
                "fecha": t.fecha.isoformat() if t.fecha else None,
                "estado": t.estado,
            })
        else:
            es_ingreso = t.destino_id in cuenta_ids
            movimientos.append({
                "id": f"T{t.id}",
                "tipo": "transferencia",
                "concepto": "Transferencia recibida" if es_ingreso else "Transferencia enviada",
                "monto": t.monto,
                "moneda": t.moneda,
                "es_ingreso": es_ingreso,
                "fecha": t.fecha.isoformat() if t.fecha else None,
                "estado": t.estado,
            })

    for p in pagos:
        movimientos.append({
            "id": f"P{p.id}",
            "tipo": "pago",
            "concepto": p.descripcion or "Pago",
            "monto": p.monto,
            "moneda": "ARS",
            "es_ingreso": False,
            "fecha": p.fecha.isoformat() if p.fecha else None,
            "estado": p.estado,
        })

    movimientos.sort(key=lambda m: m["fecha"] or "", reverse=True)
    return movimientos
