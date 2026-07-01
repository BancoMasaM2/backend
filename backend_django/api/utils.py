import os
import smtplib
from email.message import EmailMessage
from rest_framework.views import exception_handler
from rest_framework.response import Response


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        detail = response.data
        if isinstance(detail, dict):
            messages = []
            for field, errors in detail.items():
                if isinstance(errors, list):
                    messages.extend(str(e) for e in errors)
                else:
                    messages.append(str(errors))
            detail = "; ".join(messages)
        return Response({"detail": detail}, status=response.status_code)
    return response


def _get_smtp_config():
    from django.conf import settings

    return {
        "host": settings.SMTP_HOST,
        "port": settings.SMTP_PORT,
        "user": settings.SMTP_USER,
        "password": settings.SMTP_PASSWORD,
        "from": settings.SMTP_FROM,
        "use_tls": settings.SMTP_USE_TLS,
    }


def enviar_email(destinatario, asunto, cuerpo):
    cfg = _get_smtp_config()
    if not cfg["user"] or not cfg["password"]:
        return
    msg = EmailMessage()
    msg["Subject"] = asunto
    msg["From"] = cfg["from"]
    msg["To"] = destinatario
    msg.set_content(cuerpo)
    with smtplib.SMTP(cfg["host"], cfg["port"]) as server:
        if cfg["use_tls"]:
            server.starttls()
        server.login(cfg["user"], cfg["password"])
        server.send_message(msg)
