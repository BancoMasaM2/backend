from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.database.connection import get_db
from backend.services.usuario_service import (
    obtener_usuario_por_id,
    obtener_usuario_por_alias,
    actualizar_alias,
    obtener_movimientos,
)

router = APIRouter(prefix="/api/usuarios", tags=["usuarios"])


class AliasRequest(BaseModel):
    alias: str


@router.get("/{usuario_id}")
def get_usuario(usuario_id: int, db: Session = Depends(get_db)):
    usuario = obtener_usuario_por_id(db, usuario_id)
    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {"id": usuario.id, "nombre": usuario.nombre, "email": usuario.email, "alias": usuario.alias}


@router.get("/alias/{alias}")
def get_usuario_por_alias(alias: str, db: Session = Depends(get_db)):
    usuario = obtener_usuario_por_alias(db, alias)
    if usuario is None:
        raise HTTPException(status_code=404, detail="Alias no encontrado")
    return {"id": usuario.id, "nombre": usuario.nombre, "alias": usuario.alias}


@router.put("/{usuario_id}/alias")
def put_alias(usuario_id: int, req: AliasRequest, db: Session = Depends(get_db)):
    try:
        usuario = actualizar_alias(db, usuario_id, req.alias)
        return {"mensaje": "Alias actualizado", "alias": usuario.alias}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{usuario_id}/movimientos")
def get_movimientos(usuario_id: int, db: Session = Depends(get_db)):
    movimientos = obtener_movimientos(db, usuario_id)
    return movimientos



