from rest_framework import serializers
from .models import Usuario, Cuenta


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ["id", "nombre", "email", "alias", "fecha_creacion", "verificado"]


class CuentaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cuenta
        fields = ["id", "usuario_id", "moneda", "saldo"]
