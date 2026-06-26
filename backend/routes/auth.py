from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.database.connection import get_db
from backend.services.auth_service import (
    registrar_usuario,
    login_usuario,
    verificar_usuario,
    reenviar_codigo,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])


class RegistroRequest(BaseModel):
    nombre: str
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


class VerificarCodigoRequest(BaseModel):
    email: str
    codigo: str


class ReenviarCodigoRequest(BaseModel):
    email: str


@router.post("/registro")
def registro(req: RegistroRequest, db: Session = Depends(get_db)):
    try:
        registrar_usuario(db, req.nombre, req.email, req.password)
        return {"mensaje": "Usuario registrado. Revisa tu email para el código de verificación."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/verificar-codigo")
def verificar_codigo(req: VerificarCodigoRequest, db: Session = Depends(get_db)):
    try:
        usuario = verificar_usuario(db, req.email, req.codigo)
        return {"mensaje": "Email verificado exitosamente", "usuario_id": usuario.id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/reenviar-codigo")
def reenviar_codigo_endpoint(req: ReenviarCodigoRequest, db: Session = Depends(get_db)):
    try:
        reenviar_codigo(db, req.email)
        return {"mensaje": "Código reenviado. Revisa tu email."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    try:
        resultado = login_usuario(db, req.email, req.password)
        if resultado is None:
            raise HTTPException(status_code=401, detail="Email o contraseña incorrectos")
        return resultado
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
