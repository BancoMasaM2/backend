import httpx
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Cuenta, Transferencia, Pago
from .serializers import UsuarioSerializer, CuentaSerializer
from .services import (
    registrar_usuario,
    verificar_usuario,
    reenviar_codigo,
    login_usuario,
    obtener_usuario_por_id,
    obtener_usuario_por_alias,
    actualizar_alias,
    obtener_cuentas_usuario,
    obtener_cuenta,
    obtener_movimientos,
    iniciar_transferencia,
    confirmar_transferencia,
)

DOLARAPI_URL = "https://dolarapi.com/v1/dolares/{tipo}"
TASAS_FALLBACK = {
    "oficial": {"compra": 1000.0, "venta": 1020.0},
    "blue": {"compra": 1200.0, "venta": 1220.0},
}


# ─── Auth ────────────────────────────────────────────────────────────────────


@api_view(["POST"])
def auth_registro(request):
    registrar_usuario(
        request.data.get("nombre", ""),
        request.data.get("email", ""),
        request.data.get("password", ""),
    )
    return Response(
        {
            "mensaje": "Usuario registrado. Revisa tu email para el codigo de verificacion."
        },
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
def auth_verificar_codigo(request):
    try:
        usuario = verificar_usuario(
            request.data.get("email", ""),
            request.data.get("codigo", ""),
        )
        return Response(
            {"mensaje": "Email verificado exitosamente", "usuario_id": usuario.id}
        )
    except ValueError as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def auth_reenviar_codigo(request):
    try:
        reenviar_codigo(request.data.get("email", ""))
        return Response({"mensaje": "Codigo reenviado. Revisa tu email."})
    except ValueError as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def auth_login(request):
    try:
        resultado = login_usuario(
            request.data.get("email", ""),
            request.data.get("password", ""),
        )
        if resultado is None:
            return Response(
                {"detail": "Email o contrasena incorrectos"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        return Response(resultado)
    except ValueError as e:
        return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)


# ─── Usuarios ────────────────────────────────────────────────────────────────


@api_view(["GET"])
def usuario_detail(request, usuario_id):
    usuario = obtener_usuario_por_id(usuario_id)
    if usuario is None:
        return Response(
            {"detail": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND
        )
    return Response(UsuarioSerializer(usuario).data)


@api_view(["GET"])
def usuario_por_alias(request, alias):
    usuario = obtener_usuario_por_alias(alias)
    if usuario is None:
        return Response(
            {"detail": "Alias no encontrado"}, status=status.HTTP_404_NOT_FOUND
        )
    return Response(
        {"id": usuario.id, "nombre": usuario.nombre, "alias": usuario.alias}
    )


@api_view(["PUT"])
def usuario_alias_update(request, usuario_id):
    try:
        usuario = actualizar_alias(usuario_id, request.data.get("alias", ""))
        return Response({"mensaje": "Alias actualizado", "alias": usuario.alias})
    except ValueError as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def usuario_movimientos(request, usuario_id):
    movimientos = obtener_movimientos(usuario_id)
    return Response(movimientos)


# ─── Cuentas ─────────────────────────────────────────────────────────────────


@api_view(["GET"])
def cuentas_usuario(request, usuario_id):
    cuentas = obtener_cuentas_usuario(usuario_id)
    return Response(
        [{"id": c.id, "moneda": c.moneda, "saldo": c.saldo} for c in cuentas]
    )


@api_view(["GET"])
def cuenta_usuario_moneda(request, usuario_id, moneda):
    moneda = moneda.upper()
    if moneda not in ("ARS", "USD"):
        return Response(
            {"detail": "Moneda debe ser ARS o USD"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    cuenta = obtener_cuenta(usuario_id, moneda)
    if cuenta is None:
        return Response(
            {"detail": "Cuenta no encontrada"}, status=status.HTTP_404_NOT_FOUND
        )
    return Response({"id": cuenta.id, "moneda": cuenta.moneda, "saldo": cuenta.saldo})


# ─── Operaciones ─────────────────────────────────────────────────────────────


@api_view(["POST"])
def operaciones_transferir(request):
    data = request.data
    origen = Cuenta.objects.filter(
        usuario_id=data.get("origen_usuario_id"),
        moneda=data.get("moneda"),
    ).first()
    if not origen:
        return Response(
            {"detail": "Cuenta origen no encontrada"}, status=status.HTTP_404_NOT_FOUND
        )
    if origen.saldo < data.get("monto", 0):
        return Response(
            {"detail": "Saldo insuficiente"}, status=status.HTTP_400_BAD_REQUEST
        )
    destino = Cuenta.objects.filter(
        usuario_id=data.get("destino_usuario_id"),
        moneda=data.get("moneda"),
    ).first()
    if not destino:
        destino = Cuenta(
            usuario_id=data["destino_usuario_id"], moneda=data["moneda"], saldo=0.0
        )
        destino.save()
    origen.saldo -= data["monto"]
    destino.saldo += data["monto"]
    origen.save(update_fields=["saldo"])
    destino.save(update_fields=["saldo"])
    t = Transferencia.objects.create(
        origen=origen,
        destino=destino,
        monto=data["monto"],
        moneda=data["moneda"],
        estado="completada",
    )
    return Response(
        {
            "transferencia_id": t.id,
            "origen_saldo": origen.saldo,
            "destino_saldo": destino.saldo,
        }
    )


@api_view(["POST"])
def operaciones_iniciar_transferencia(request):
    data = request.data
    try:
        resultado = iniciar_transferencia(
            data.get("origen_usuario_id"),
            data.get("destino_alias"),
            data.get("moneda"),
            data.get("monto"),
        )
        return Response(resultado)
    except ValueError as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def operaciones_confirmar_transferencia(request):
    data = request.data
    try:
        resultado = confirmar_transferencia(
            data.get("origen_usuario_id"),
            data.get("codigo"),
        )
        return Response({"estado": "completada", "detalle": resultado})
    except ValueError as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def operaciones_conversion(request):
    data = request.data
    cuenta_origen = Cuenta.objects.filter(
        usuario_id=data.get("usuario_id"),
        moneda=data.get("moneda_origen"),
    ).first()
    if not cuenta_origen:
        return Response(
            {"detail": "Cuenta origen no encontrada"}, status=status.HTTP_404_NOT_FOUND
        )
    if cuenta_origen.saldo < data.get("monto_origen", 0):
        return Response(
            {"detail": "Saldo insuficiente"}, status=status.HTTP_400_BAD_REQUEST
        )
    cuenta_destino = Cuenta.objects.filter(
        usuario_id=data.get("usuario_id"),
        moneda=data.get("moneda_destino"),
    ).first()
    if not cuenta_destino:
        cuenta_destino = Cuenta(
            usuario_id=data["usuario_id"], moneda=data["moneda_destino"], saldo=0.0
        )
        cuenta_destino.save()
    cuenta_origen.saldo -= data["monto_origen"]
    cuenta_destino.saldo += data["monto_destino"]
    cuenta_origen.save(update_fields=["saldo"])
    cuenta_destino.save(update_fields=["saldo"])
    Transferencia.objects.create(
        origen=cuenta_origen,
        destino=cuenta_destino,
        monto=data["monto_origen"],
        moneda=f"{data['moneda_origen']}->{data['moneda_destino']}",
        estado="completada",
    )
    return Response(
        {
            "cuenta_origen_saldo": cuenta_origen.saldo,
            "cuenta_destino_saldo": cuenta_destino.saldo,
            "tasa": data.get("tasa"),
        }
    )


@api_view(["POST"])
def operaciones_pago(request):
    data = request.data
    cuenta = Cuenta.objects.filter(
        usuario_id=data.get("usuario_id"),
        moneda="ARS",
    ).first()
    if not cuenta:
        return Response(
            {"detail": "Cuenta ARS no encontrada"}, status=status.HTTP_404_NOT_FOUND
        )
    if cuenta.saldo < data.get("monto", 0):
        return Response(
            {"detail": "Saldo insuficiente"}, status=status.HTTP_400_BAD_REQUEST
        )
    cuenta.saldo -= data["monto"]
    cuenta.save(update_fields=["saldo"])
    pago = Pago.objects.create(
        usuario_id=data["usuario_id"],
        monto=data["monto"],
        descripcion=data.get("descripcion", ""),
        estado="completada",
    )
    return Response({"pago_id": pago.id, "saldo_restante": cuenta.saldo})


# ─── Payment Gateway ─────────────────────────────────────────────────────────


def _obtener_cotizacion(tipo="blue"):
    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(DOLARAPI_URL.format(tipo=tipo))
            resp.raise_for_status()
            data = resp.json()
            return {
                "tipo": tipo,
                "compra": data.get("compra"),
                "venta": data.get("venta"),
                "fecha": data.get("fechaActualizacion"),
                "fuente": "dolarapi.com",
            }
    except Exception:
        fallback = TASAS_FALLBACK.get(tipo, TASAS_FALLBACK["blue"])
        return {
            "tipo": tipo,
            "compra": fallback["compra"],
            "venta": fallback["venta"],
            "fecha": None,
            "fuente": "fallback",
        }


@api_view(["GET"])
def payments_cotizacion(request):
    data = _obtener_cotizacion(request.query_params.get("tipo", "blue"))
    return Response(data)


@api_view(["POST"])
def payments_conversiones(request):
    data = request.data
    if data.get("monto", 0) <= 0:
        return Response(
            {"detail": "El monto debe ser positivo"}, status=status.HTTP_400_BAD_REQUEST
        )
    desde = data.get("desde", "").upper()
    hacia = data.get("hacia", "").upper()
    if desde not in ("ARS", "USD") or hacia not in ("ARS", "USD"):
        return Response(
            {"detail": "Moneda debe ser ARS o USD"}, status=status.HTTP_400_BAD_REQUEST
        )
    if desde == hacia:
        return Response(
            {"detail": "Las monedas deben ser distintas"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    cotizacion = _obtener_cotizacion("blue")

    if desde == "ARS" and hacia == "USD":
        tasa = cotizacion["venta"]
        monto_destino = round(data["monto"] / tasa, 2)
    elif desde == "USD" and hacia == "ARS":
        tasa = cotizacion["compra"]
        monto_destino = round(data["monto"] * tasa, 2)
    else:
        return Response(
            {"detail": "Par de monedas no soportado"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    usuario_id = data.get("usuario_id")
    cuenta_origen = Cuenta.objects.filter(usuario_id=usuario_id, moneda=desde).first()
    if not cuenta_origen:
        return Response(
            {"detail": "Cuenta origen no encontrada"}, status=status.HTTP_404_NOT_FOUND
        )
    if cuenta_origen.saldo < data["monto"]:
        return Response(
            {"detail": "Saldo insuficiente"}, status=status.HTTP_400_BAD_REQUEST
        )
    cuenta_destino, _ = Cuenta.objects.get_or_create(
        usuario_id=usuario_id, moneda=hacia, defaults={"saldo": 0.0}
    )
    cuenta_origen.saldo -= data["monto"]
    cuenta_destino.saldo += monto_destino
    cuenta_origen.save(update_fields=["saldo"])
    cuenta_destino.save(update_fields=["saldo"])
    Transferencia.objects.create(
        origen=cuenta_origen,
        destino=cuenta_destino,
        monto=data["monto"],
        moneda=f"{desde}->{hacia}",
        estado="completada",
    )
    return Response(
        {
            "monto_origen": data["monto"],
            "moneda_origen": desde,
            "monto_destino": monto_destino,
            "moneda_destino": hacia,
            "tasa": tasa,
            "resultado": {
                "cuenta_origen_saldo": cuenta_origen.saldo,
                "cuenta_destino_saldo": cuenta_destino.saldo,
                "tasa": tasa,
            },
        }
    )


@api_view(["POST"])
def payments_pagos(request):
    data = request.data
    if data.get("monto", 0) <= 0:
        return Response(
            {"detail": "El monto debe ser positivo"}, status=status.HTTP_400_BAD_REQUEST
        )
    cuenta = Cuenta.objects.filter(
        usuario_id=data.get("usuario_id"), moneda="ARS"
    ).first()
    if not cuenta:
        return Response(
            {"detail": "Cuenta ARS no encontrada"}, status=status.HTTP_404_NOT_FOUND
        )
    if cuenta.saldo < data["monto"]:
        return Response(
            {"detail": "Saldo insuficiente"}, status=status.HTTP_400_BAD_REQUEST
        )
    cuenta.saldo -= data["monto"]
    cuenta.save(update_fields=["saldo"])
    pago = Pago.objects.create(
        usuario_id=data["usuario_id"],
        monto=data["monto"],
        descripcion=data.get("descripcion", ""),
        estado="completada",
    )
    return Response(
        {
            "estado": "completada",
            "detalle": {"pago_id": pago.id, "saldo_restante": cuenta.saldo},
        }
    )


@api_view(["POST"])
def payments_transferencias(request):
    data = request.data
    if data.get("monto", 0) <= 0:
        return Response(
            {"detail": "El monto debe ser positivo"}, status=status.HTTP_400_BAD_REQUEST
        )
    if data.get("moneda", "").upper() not in ("ARS", "USD"):
        return Response(
            {"detail": "Moneda debe ser ARS o USD"}, status=status.HTTP_400_BAD_REQUEST
        )
    moneda = data["moneda"].upper()
    origen = Cuenta.objects.filter(
        usuario_id=data.get("origen_usuario_id"),
        moneda=moneda,
    ).first()
    if not origen:
        return Response(
            {"detail": "Cuenta origen no encontrada"}, status=status.HTTP_404_NOT_FOUND
        )
    if origen.saldo < data["monto"]:
        return Response(
            {"detail": "Saldo insuficiente"}, status=status.HTTP_400_BAD_REQUEST
        )
    destino = Cuenta.objects.filter(
        usuario_id=data.get("destino_usuario_id"),
        moneda=moneda,
    ).first()
    if not destino:
        destino = Cuenta(
            usuario_id=data["destino_usuario_id"], moneda=moneda, saldo=0.0
        )
        destino.save()
    origen.saldo -= data["monto"]
    destino.saldo += data["monto"]
    origen.save(update_fields=["saldo"])
    destino.save(update_fields=["saldo"])
    t = Transferencia.objects.create(
        origen=origen,
        destino=destino,
        monto=data["monto"],
        moneda=moneda,
        estado="completada",
    )
    return Response(
        {
            "estado": "completada",
            "detalle": {
                "transferencia_id": t.id,
                "origen_saldo": origen.saldo,
                "destino_saldo": destino.saldo,
            },
        }
    )


# ─── Health ───────────────────────────────────────────────────────────────────


@api_view(["GET"])
def health(request):
    return Response({"status": "ok"})
