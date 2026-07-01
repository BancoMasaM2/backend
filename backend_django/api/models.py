import random
from datetime import timedelta
from django.db import models
from django.utils import timezone


def generar_codigo():
    return str(random.randint(100000, 999999))


def _utcnow():
    return timezone.now().replace(tzinfo=None)


class Usuario(models.Model):
    nombre = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    fecha_creacion = models.DateTimeField(default=_utcnow)
    verificado = models.BooleanField(default=False)
    codigo_verificacion = models.CharField(max_length=6, null=True, blank=True)
    codigo_expiracion = models.DateTimeField(null=True, blank=True)
    alias = models.CharField(max_length=50, unique=True, null=True, blank=True)
    transfer_codigo = models.CharField(max_length=6, null=True, blank=True)
    transfer_codigo_expiracion = models.DateTimeField(null=True, blank=True)
    transfer_destino_alias = models.CharField(max_length=50, null=True, blank=True)
    transfer_moneda = models.CharField(max_length=3, null=True, blank=True)
    transfer_monto = models.FloatField(null=True, blank=True)

    def generar_nuevo_codigo(self, expiracion_minutos=15):
        self.codigo_verificacion = generar_codigo()
        self.codigo_expiracion = _utcnow() + timedelta(minutes=expiracion_minutos)
        return self.codigo_verificacion

    def verificar_codigo(self, codigo):
        if not self.codigo_verificacion or not self.codigo_expiracion:
            return False
        if _utcnow() > self.codigo_expiracion:
            return False
        return self.codigo_verificacion == codigo

    def generar_codigo_transferencia(self):
        self.transfer_codigo = generar_codigo()
        self.transfer_codigo_expiracion = _utcnow() + timedelta(minutes=15)
        return self.transfer_codigo

    def verificar_codigo_transferencia(self, codigo):
        if not self.transfer_codigo or not self.transfer_codigo_expiracion:
            return False
        if _utcnow() > self.transfer_codigo_expiracion:
            return False
        return self.transfer_codigo == codigo


class Cuenta(models.Model):
    usuario = models.ForeignKey(
        Usuario, on_delete=models.CASCADE, related_name="cuentas"
    )
    moneda = models.CharField(max_length=3)
    saldo = models.FloatField(default=0.0)

    class Meta:
        unique_together = ("usuario", "moneda")


class Transferencia(models.Model):
    origen = models.ForeignKey(
        Cuenta,
        on_delete=models.SET_NULL,
        null=True,
        related_name="transferencias_origen",
    )
    destino = models.ForeignKey(
        Cuenta,
        on_delete=models.SET_NULL,
        null=True,
        related_name="transferencias_destino",
    )
    monto = models.FloatField()
    moneda = models.CharField(max_length=3)
    fecha = models.DateTimeField(default=_utcnow)
    estado = models.CharField(max_length=20, default="completada")


class Pago(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="pagos")
    monto = models.FloatField()
    descripcion = models.CharField(max_length=255, null=True, blank=True)
    fecha = models.DateTimeField(default=_utcnow)
    estado = models.CharField(max_length=20, default="pendiente")
