from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path("api/auth/registro", views.auth_registro),
    path("api/auth/verificar-codigo", views.auth_verificar_codigo),
    path("api/auth/reenviar-codigo", views.auth_reenviar_codigo),
    path("api/auth/login", views.auth_login),
    # Usuarios
    path("api/usuarios/alias/<str:alias>/", views.usuario_por_alias),
    path("api/usuarios/<int:usuario_id>/", views.usuario_detail),
    path("api/usuarios/<int:usuario_id>/alias/", views.usuario_alias_update),
    path("api/usuarios/<int:usuario_id>/movimientos/", views.usuario_movimientos),
    # Cuentas
    path("api/cuentas/<int:usuario_id>/", views.cuentas_usuario),
    path("api/cuentas/<int:usuario_id>/<str:moneda>/", views.cuenta_usuario_moneda),
    # Operaciones
    path("api/operaciones/transferir", views.operaciones_transferir),
    path(
        "api/operaciones/iniciar-transferencia", views.operaciones_iniciar_transferencia
    ),
    path(
        "api/operaciones/confirmar-transferencia",
        views.operaciones_confirmar_transferencia,
    ),
    path("api/operaciones/conversion", views.operaciones_conversion),
    path("api/operaciones/pago", views.operaciones_pago),
    # Payment Gateway
    path("api/payments/cotizacion", views.payments_cotizacion),
    path("api/payments/conversiones", views.payments_conversiones),
    path("api/payments/pagos", views.payments_pagos),
    path("api/payments/transferencias", views.payments_transferencias),
    # Health
    path("health/", views.health),
]
