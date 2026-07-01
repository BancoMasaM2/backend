import random
from .models import Usuario, Cuenta, Transferencia, Pago
from .utils import enviar_email


def _generar_alias(db, nombre):
    base = nombre.lower().replace(" ", "").replace(".", "")[:20]
    alias = base
    while Usuario.objects.filter(alias=alias).exists():
        alias = f"{base}{random.randint(10, 99)}"
    return alias


def _enviar_codigo(email, codigo):
    asunto = "Codigo de verificacion - Broker"
    cuerpo = f"Tu codigo de verificacion es: {codigo}\n\nValido por 15 minutos."
    try:
        enviar_email(email, asunto, cuerpo)
    except Exception as e:
        raise ValueError(f"Error al enviar el email: {e}")


def _enviar_codigo_transferencia(email, codigo, monto, moneda, destino_alias):
    asunto = "Codigo de confirmacion - Transferencia"
    cuerpo = (
        f"Estas por transferir ${monto:.2f} {moneda} a '{destino_alias}'.\n\n"
        f"Tu codigo de confirmacion es: {codigo}\n\nValido por 15 minutos."
    )
    try:
        enviar_email(email, asunto, cuerpo)
    except Exception as e:
        raise ValueError(f"Error al enviar el email: {e}")


def registrar_usuario(nombre, email, password):
    if Usuario.objects.filter(email=email).exists():
        raise ValueError("El email ya esta registrado")
    alias = _generar_alias(None, nombre)
    usuario = Usuario.objects.create(
        nombre=nombre, email=email, password=password, verificado=False, alias=alias
    )
    Cuenta.objects.create(usuario=usuario, moneda="ARS", saldo=0.0)
    Cuenta.objects.create(usuario=usuario, moneda="USD", saldo=0.0)
    codigo = usuario.generar_nuevo_codigo()
    usuario.save(update_fields=["codigo_verificacion", "codigo_expiracion"])
    _enviar_codigo(email, codigo)
    return usuario


def verificar_usuario(email, codigo):
    try:
        usuario = Usuario.objects.get(email=email)
    except Usuario.DoesNotExist:
        raise ValueError("Email no encontrado")
    if usuario.verificado:
        raise ValueError("El usuario ya esta verificado")
    if not usuario.verificar_codigo(codigo):
        raise ValueError("Codigo invalido o expirado")
    usuario.verificado = True
    usuario.codigo_verificacion = None
    usuario.codigo_expiracion = None
    usuario.save(
        update_fields=["verificado", "codigo_verificacion", "codigo_expiracion"]
    )
    return usuario


def reenviar_codigo(email):
    try:
        usuario = Usuario.objects.get(email=email)
    except Usuario.DoesNotExist:
        raise ValueError("Email no encontrado")
    if usuario.verificado:
        raise ValueError("El usuario ya esta verificado")
    codigo = usuario.generar_nuevo_codigo()
    usuario.save(update_fields=["codigo_verificacion", "codigo_expiracion"])
    _enviar_codigo(email, codigo)
    return usuario


def login_usuario(email, password):
    try:
        usuario = Usuario.objects.get(email=email)
    except Usuario.DoesNotExist:
        return None
    if usuario.password != password:
        return None
    if not usuario.verificado:
        raise ValueError("Debes verificar tu email antes de iniciar sesion")
    return {"usuario_id": usuario.id, "nombre": usuario.nombre, "alias": usuario.alias}


def obtener_usuario_por_id(usuario_id):
    try:
        return Usuario.objects.get(id=usuario_id)
    except Usuario.DoesNotExist:
        return None


def obtener_usuario_por_alias(alias):
    try:
        return Usuario.objects.get(alias=alias)
    except Usuario.DoesNotExist:
        return None


def actualizar_alias(usuario_id, nuevo_alias):
    existe = Usuario.objects.filter(alias=nuevo_alias).exclude(id=usuario_id).exists()
    if existe:
        raise ValueError("El alias ya esta en uso")
    try:
        usuario = Usuario.objects.get(id=usuario_id)
    except Usuario.DoesNotExist:
        raise ValueError("Usuario no encontrado")
    usuario.alias = nuevo_alias
    usuario.save(update_fields=["alias"])
    return usuario


def obtener_cuentas_usuario(usuario_id):
    return Cuenta.objects.filter(usuario_id=usuario_id)


def obtener_cuenta(usuario_id, moneda):
    try:
        return Cuenta.objects.get(usuario_id=usuario_id, moneda=moneda)
    except Cuenta.DoesNotExist:
        return None


def obtener_movimientos(usuario_id):
    cuenta_ids = list(
        Cuenta.objects.filter(usuario_id=usuario_id).values_list("id", flat=True)
    )
    transferencias = Transferencia.objects.filter(
        origen_id__in=cuenta_ids
    ) | Transferencia.objects.filter(destino_id__in=cuenta_ids)
    pagos = Pago.objects.filter(usuario_id=usuario_id)
    movimientos = []
    for t in transferencias:
        es_conversion = "->" in (t.moneda or "") and len(cuenta_ids) >= 2
        if es_conversion:
            movimientos.append(
                {
                    "id": f"T{t.id}",
                    "tipo": "conversion",
                    "concepto": f"Compra de {t.moneda.split('->')[1]}",
                    "monto": t.monto,
                    "moneda": t.moneda,
                    "es_ingreso": False,
                    "fecha": t.fecha.isoformat() if t.fecha else None,
                    "estado": t.estado,
                }
            )
        else:
            es_ingreso = t.destino_id in cuenta_ids
            movimientos.append(
                {
                    "id": f"T{t.id}",
                    "tipo": "transferencia",
                    "concepto": "Transferencia recibida"
                    if es_ingreso
                    else "Transferencia enviada",
                    "monto": t.monto,
                    "moneda": t.moneda,
                    "es_ingreso": es_ingreso,
                    "fecha": t.fecha.isoformat() if t.fecha else None,
                    "estado": t.estado,
                }
            )
    for p in pagos:
        movimientos.append(
            {
                "id": f"P{p.id}",
                "tipo": "pago",
                "concepto": p.descripcion or "Pago",
                "monto": p.monto,
                "moneda": "ARS",
                "es_ingreso": False,
                "fecha": p.fecha.isoformat() if p.fecha else None,
                "estado": p.estado,
            }
        )
    movimientos.sort(key=lambda m: m["fecha"] or "", reverse=True)
    return movimientos


def iniciar_transferencia(origen_usuario_id, destino_alias, moneda, monto):
    try:
        origen = Usuario.objects.get(id=origen_usuario_id)
    except Usuario.DoesNotExist:
        raise ValueError("Usuario origen no encontrado")
    destino = obtener_usuario_por_alias(destino_alias)
    if not destino:
        raise ValueError("Alias de destino no encontrado")
    if destino.id == origen_usuario_id:
        raise ValueError("No podes transferirte a vos mismo")
    try:
        cuenta_origen = Cuenta.objects.get(usuario_id=origen_usuario_id, moneda=moneda)
    except Cuenta.DoesNotExist:
        raise ValueError(f"No tenes cuenta en {moneda}")
    if cuenta_origen.saldo < monto:
        raise ValueError("Saldo insuficiente")
    codigo = origen.generar_codigo_transferencia()
    origen.transfer_destino_alias = destino_alias
    origen.transfer_moneda = moneda
    origen.transfer_monto = monto
    origen.save(
        update_fields=[
            "transfer_codigo",
            "transfer_codigo_expiracion",
            "transfer_destino_alias",
            "transfer_moneda",
            "transfer_monto",
        ]
    )
    _enviar_codigo_transferencia(origen.email, codigo, monto, moneda, destino_alias)
    return {"mensaje": "Codigo de confirmacion enviado a tu email"}


def confirmar_transferencia(origen_usuario_id, codigo):
    try:
        origen = Usuario.objects.get(id=origen_usuario_id)
    except Usuario.DoesNotExist:
        raise ValueError("Usuario origen no encontrado")
    if not origen.verificar_codigo_transferencia(codigo):
        raise ValueError("Codigo invalido o expirado")
    destino_alias = origen.transfer_destino_alias
    moneda = origen.transfer_moneda
    monto = origen.transfer_monto
    if not destino_alias or not moneda or not monto:
        raise ValueError("No hay una transferencia pendiente")
    destino = obtener_usuario_por_alias(destino_alias)
    if not destino:
        raise ValueError("Alias de destino no encontrado")
    try:
        cuenta_origen = Cuenta.objects.get(usuario_id=origen.id, moneda=moneda)
    except Cuenta.DoesNotExist:
        raise ValueError("Cuenta origen no encontrada")
    if cuenta_origen.saldo < monto:
        raise ValueError("Saldo insuficiente")
    cuenta_destino, _ = Cuenta.objects.get_or_create(
        usuario=destino, moneda=moneda, defaults={"saldo": 0.0}
    )
    cuenta_origen.saldo -= monto
    cuenta_destino.saldo += monto
    cuenta_origen.save(update_fields=["saldo"])
    cuenta_destino.save(update_fields=["saldo"])
    transferencia = Transferencia.objects.create(
        origen=cuenta_origen,
        destino=cuenta_destino,
        monto=monto,
        moneda=moneda,
        estado="completada",
    )
    origen.transfer_codigo = None
    origen.transfer_codigo_expiracion = None
    origen.transfer_destino_alias = None
    origen.transfer_moneda = None
    origen.transfer_monto = None
    origen.save(
        update_fields=[
            "transfer_codigo",
            "transfer_codigo_expiracion",
            "transfer_destino_alias",
            "transfer_moneda",
            "transfer_monto",
        ]
    )
    return {
        "transferencia_id": transferencia.id,
        "origen_saldo": cuenta_origen.saldo,
        "destino_saldo": cuenta_destino.saldo,
    }
