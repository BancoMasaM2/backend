CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    verificado INTEGER DEFAULT 0,
    codigo_verificacion TEXT,
    codigo_expiracion TIMESTAMP,
    alias TEXT UNIQUE,
    transfer_codigo TEXT,
    transfer_codigo_expiracion TIMESTAMP,
    transfer_destino_alias TEXT,
    transfer_moneda TEXT,
    transfer_monto REAL
);

CREATE TABLE IF NOT EXISTS cuentas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    moneda TEXT NOT NULL CHECK(moneda IN ('ARS', 'USD')),
    saldo REAL NOT NULL DEFAULT 0.0,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    UNIQUE(usuario_id, moneda)
);

CREATE TABLE IF NOT EXISTS transferencias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    origen_id INTEGER,
    destino_id INTEGER,
    monto REAL NOT NULL,
    moneda TEXT NOT NULL,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estado TEXT NOT NULL DEFAULT 'completada',
    FOREIGN KEY (origen_id) REFERENCES cuentas(id),
    FOREIGN KEY (destino_id) REFERENCES cuentas(id)
);

CREATE TABLE IF NOT EXISTS pagos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    monto REAL NOT NULL,
    descripcion TEXT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estado TEXT NOT NULL DEFAULT 'pendiente',
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);
