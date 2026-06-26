import random
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI
from sqlalchemy import text
from backend.database.connection import engine, SessionLocal, Base
from backend.routes.auth import router as auth_router
from backend.routes.usuarios import router as usuarios_router
from backend.routes.cuentas import router as cuentas_router
from backend.routes.operaciones import router as operaciones_router

load_dotenv(Path(__file__).parent / ".env")

Base.metadata.create_all(bind=engine)

with engine.connect() as conn:
    migraciones = [
        "ALTER TABLE usuarios ADD COLUMN verificado INTEGER DEFAULT 0",
        "ALTER TABLE usuarios ADD COLUMN codigo_verificacion TEXT",
        "ALTER TABLE usuarios ADD COLUMN codigo_expiracion TIMESTAMP",
        "ALTER TABLE usuarios ADD COLUMN alias TEXT",
        "ALTER TABLE usuarios ADD COLUMN transfer_codigo TEXT",
        "ALTER TABLE usuarios ADD COLUMN transfer_codigo_expiracion TIMESTAMP",
        "ALTER TABLE usuarios ADD COLUMN transfer_destino_alias TEXT",
        "ALTER TABLE usuarios ADD COLUMN transfer_moneda TEXT",
        "ALTER TABLE usuarios ADD COLUMN transfer_monto REAL",
    ]
    for stmt in migraciones:
        try:
            conn.execute(text(stmt))
            conn.commit()
        except Exception:
            pass

db = SessionLocal()
usuarios_sin_alias = db.execute(
    text("SELECT id, nombre FROM usuarios WHERE alias IS NULL")
).fetchall()
for uid, nombre in usuarios_sin_alias:
    base = nombre.lower().replace(" ", "").replace(".", "")[:20]
    alias = base
    while db.execute(
        text("SELECT 1 FROM usuarios WHERE alias = :a AND id != :uid"),
        {"a": alias, "uid": uid},
    ).first():
        alias = f"{base}{random.randint(10, 99)}"
    db.execute(
        text("UPDATE usuarios SET alias = :a WHERE id = :uid"),
        {"a": alias, "uid": uid},
    )
db.commit()
db.close()

app = FastAPI(title="Broker Simulador - Backend", version="1.0.0")

app.include_router(auth_router)
app.include_router(usuarios_router)
app.include_router(cuentas_router)
app.include_router(operaciones_router)


@app.get("/health")
def health():
    return {"status": "ok"}
