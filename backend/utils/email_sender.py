import os
import smtplib
from email.message import EmailMessage


def _get_smtp_config():
    return {
        "host": os.getenv("SMTP_HOST", "smtp.gmail.com"),
        "port": int(os.getenv("SMTP_PORT", "587")),
        "user": os.getenv("SMTP_USER", ""),
        "password": os.getenv("SMTP_PASSWORD", ""),
        "from": os.getenv("SMTP_FROM", os.getenv("SMTP_USER", "")),
        "use_tls": os.getenv("SMTP_USE_TLS", "true").lower() == "true",
    }


def enviar_email(destinatario: str, asunto: str, cuerpo: str) -> None:
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
