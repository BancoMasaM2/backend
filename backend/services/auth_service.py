import random
from sqlalchemy.orm import Session
from backend.models.usuario import Usuario
from backend.models.cuenta import Cuenta
from backend.utils.email_sender import enviar_email


def _generar_alias(db: Session, nombre: str) -> str:
    base = nombre.lower().replace(" ", "").replace(".", "")[:20]
    alias = base
    while db.query(Usuario).filter(Usuario.alias == alias).first():
        alias = f"{base}{random.randint(10, 99)}"
    return alias


def registrar_usuario(db: Session, nombre: str, email: str, password: str) -> Usuario:
    existente = db.query(Usuario).filter(Usuario.email == email).first()
    if existente:
        raise ValueError("El email ya está registrado")

    alias = _generar_alias(db, nombre)
    usuario = Usuario(
        nombre=nombre,
        email=email,
        password=password,
        verificado=False,
        alias=alias,
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    cuenta_ars = Cuenta(usuario_id=usuario.id, moneda="ARS", saldo=0.0)
    cuenta_usd = Cuenta(usuario_id=usuario.id, moneda="USD", saldo=0.0)
    db.add(cuenta_ars)
    db.add(cuenta_usd)
    db.commit()

    codigo = usuario.generar_nuevo_codigo()
    db.commit()

    _enviar_codigo(email, codigo)

    return usuario


def _enviar_codigo(email: str, codigo: str) -> None:
    asunto = "Código de verificación - Broker"
    cuerpo = f"Tu código de verificación es: {codigo}\n\nVálido por 15 minutos."
    try:
        enviar_email(email, asunto, cuerpo)
    except Exception as e:
        raise ValueError(f"Error al enviar el email: {e}")


def verificar_usuario(db: Session, email: str, codigo: str) -> Usuario:
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    if not usuario:
        raise ValueError("Email no encontrado")
    if usuario.verificado:
        raise ValueError("El usuario ya está verificado")
    if not usuario.verificar_codigo(codigo):
        raise ValueError("Código inválido o expirado")

    usuario.verificado = True
    usuario.codigo_verificacion = None
    usuario.codigo_expiracion = None
    db.commit()
    return usuario


def reenviar_codigo(db: Session, email: str) -> Usuario:
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    if not usuario:
        raise ValueError("Email no encontrado")
    if usuario.verificado:
        raise ValueError("El usuario ya está verificado")

    codigo = usuario.generar_nuevo_codigo()
    db.commit()
    _enviar_codigo(email, codigo)
    return usuario


def login_usuario(db: Session, email: str, password: str) -> dict | None:
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    if not usuario:
        return None
    if usuario.password != password:
        return None
    if usuario.verificado is False:
        raise ValueError("Debes verificar tu email antes de iniciar sesión")
    return {
        "usuario_id": usuario.id,
        "nombre": usuario.nombre,
        "alias": usuario.alias,
    }
