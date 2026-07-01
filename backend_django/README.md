# Broker Simulador - Backend (Django)

API de backend para un simulador de bróker/pasarela de pagos construida con Django y Django REST Framework. Soporta registro de usuarios con verificación por email, cuentas en ARS/USD, transferencias, conversión de divisas con cotización en vivo (DolarAPI) y pagos.

---

## Requisitos

- Python 3.10+
- pip
- uv

---

## Instalación y ejecución

```bash
# 1. Clonar / acceder al proyecto
cd backend_django

# 2. Crear entorno virtual.
uv venv
source .venv/bin/activate

# 3. Instalar dependencias
uv pip install -r requirements.txt

# 4. Ejecutar migraciones
python manage.py migrate

# 5. Iniciar servidor
python manage.py runserver 0.0.0.0:9000
```

El servidor se levanta en `http://localhost:9000`.

---

## Variables de entorno (`.env`)

| Variable | Descripción | Default |
|---|---|---|
| `SMTP_HOST` | Host del servidor SMTP | `smtp.gmail.com` |
| `SMTP_PORT` | Puerto SMTP | `587` |
| `SMTP_USER` | Usuario SMTP | |
| `SMTP_PASSWORD` | Contraseña SMTP | |
| `SMTP_FROM` | Remitente de emails | (mismo que SMTP_USER) |
| `SMTP_USE_TLS` | Usar TLS | `true` |
| `DJANGO_SECRET_KEY` | Secret key de Django | |
| `DJANGO_DEBUG` | Modo debug | `True` |

---

## Estructura del proyecto

```
backend_django/
├── api/                          # Aplicación principal
│   ├── __init__.py
│   ├── models.py                 # Usuario, Cuenta, Transferencia, Pago
│   ├── serializers.py            # DRF serializers
│   ├── services.py               # Lógica de negocio
│   ├── utils.py                  # Email sender + exception handler
│   ├── views.py                  # Todos los endpoints
│   └── urls.py                   # Definición de rutas
├── config/                       # Configuración del proyecto
│   ├── __init__.py
│   ├── settings.py               # Settings de Django
│   ├── urls.py                   # URL raíz
│   └── wsgi.py                   # WSGI entrypoint
├── manage.py
├── requirements.txt
└── .env
```

---

## Modelos de datos

### Usuario

| Campo | Tipo | Descripción |
|---|---|---|
| `id` | Integer (PK) | ID autoincremental |
| `nombre` | String(100) | Nombre completo |
| `email` | EmailField (unique) | Correo electrónico |
| `password` | String(255) | Contraseña (en texto plano, simulador) |
| `fecha_creacion` | DateTime | Fecha de registro |
| `verificado` | Boolean | Email verificado |
| `codigo_verificacion` | String(6) nullable | Código de verificación de email |
| `codigo_expiracion` | DateTime nullable | Expiración del código de verificación |
| `alias` | String(50) unique nullable | Alias para transferencias |
| `transfer_codigo` | String(6) nullable | Código de confirmación de transferencia |
| `transfer_codigo_expiracion` | DateTime nullable | Expiración del código de transferencia |
| `transfer_destino_alias` | String(50) nullable | Alias destino de transferencia pendiente |
| `transfer_moneda` | String(3) nullable | Moneda de transferencia pendiente |
| `transfer_monto` | Float nullable | Monto de transferencia pendiente |

### Cuenta

| Campo | Tipo | Descripción |
|---|---|---|
| `id` | Integer (PK) | ID autoincremental |
| `usuario` | ForeignKey(Usuario) | Dueño de la cuenta |
| `moneda` | String(3) | `ARS` o `USD` |
| `saldo` | Float | Saldo disponible |

Unique constraint: `(usuario, moneda)` — un usuario tiene como máximo una cuenta por moneda.

### Transferencia

| Campo | Tipo | Descripción |
|---|---|---|
| `id` | Integer (PK) | ID autoincremental |
| `origen` | ForeignKey(Cuenta) nullable | Cuenta origen |
| `destino` | ForeignKey(Cuenta) nullable | Cuenta destino |
| `monto` | Float | Monto transferido |
| `moneda` | String(3) | Moneda (`ARS`, `USD`, o `ARS->USD`) |
| `fecha` | DateTime | Fecha de la operación |
| `estado` | String(20) | Estado (por defecto `completada`) |

### Pago

| Campo | Tipo | Descripción |
|---|---|---|
| `id` | Integer (PK) | ID autoincremental |
| `usuario` | ForeignKey(Usuario) | Usuario que realiza el pago |
| `monto` | Float | Monto del pago |
| `descripcion` | String(255) nullable | Descripción del pago |
| `fecha` | DateTime | Fecha del pago |
| `estado` | String(20) | Estado (por defecto `pendiente`) |

---

## Rutas de la API

### Auth

| Método | Ruta | Descripción |
|---|---|---|
| `POST` | `/api/auth/registro` | Registrar nuevo usuario |
| `POST` | `/api/auth/verificar-codigo` | Verificar email con código |
| `POST` | `/api/auth/reenviar-codigo` | Reenviar código de verificación |
| `POST` | `/api/auth/login` | Iniciar sesión |

#### `POST /api/auth/registro`

Crea un usuario, genera alias automáticamente, crea cuentas ARS y USD en 0, y envía código de verificación por email.

**Request:**
```json
{
  "nombre": "Juan Pérez",
  "email": "juan@example.com",
  "password": "mi-clave"
}
```

**Response (200):**
```json
{
  "mensaje": "Usuario registrado. Revisa tu email para el codigo de verificacion."
}
```

**Errors:** `400` si el email ya está registrado.

---

#### `POST /api/auth/verificar-codigo`

**Request:**
```json
{
  "email": "juan@example.com",
  "codigo": "123456"
}
```

**Response (200):**
```json
{
  "mensaje": "Email verificado exitosamente",
  "usuario_id": 1
}
```

**Errors:** `400` si el código es inválido o expiró.

---

#### `POST /api/auth/reenviar-codigo`

**Request:**
```json
{
  "email": "juan@example.com"
}
```

**Response (200):**
```json
{
  "mensaje": "Codigo reenviado. Revisa tu email."
}
```

---

#### `POST /api/auth/login`

**Request:**
```json
{
  "email": "juan@example.com",
  "password": "mi-clave"
}
```

**Response (200):**
```json
{
  "usuario_id": 1,
  "nombre": "Juan Pérez",
  "alias": "juanperez"
}
```

**Errors:** `401` si credenciales incorrectas, `403` si email no verificado.

---

### Usuarios

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api/usuarios/{id}/` | Obtener usuario por ID |
| `GET` | `/api/usuarios/alias/{alias}/` | Obtener usuario por alias |
| `PUT` | `/api/usuarios/{id}/alias/` | Actualizar alias |
| `GET` | `/api/usuarios/{id}/movimientos/` | Obtener movimientos del usuario |

#### `GET /api/usuarios/{id}/`

**Response (200):**
```json
{
  "id": 1,
  "nombre": "Juan Pérez",
  "email": "juan@example.com",
  "alias": "juanperez",
  "fecha_creacion": "2026-07-01T14:09:43.221108",
  "verificado": true
}
```

---

#### `GET /api/usuarios/alias/{alias}/`

**Response (200):**
```json
{
  "id": 1,
  "nombre": "Juan Pérez",
  "alias": "juanperez"
}
```

---

#### `PUT /api/usuarios/{id}/alias/`

**Request:**
```json
{
  "alias": "nuevoalias"
}
```

**Response (200):**
```json
{
  "mensaje": "Alias actualizado",
  "alias": "nuevoalias"
}
```

**Errors:** `400` si el alias ya está en uso.

---

#### `GET /api/usuarios/{id}/movimientos/`

Devuelve transferencias, conversiones y pagos del usuario ordenados por fecha descendente.

**Response (200):**
```json
[
  {
    "id": "T1",
    "tipo": "transferencia",
    "concepto": "Transferencia recibida",
    "monto": 500.0,
    "moneda": "ARS",
    "es_ingreso": true,
    "fecha": "2026-07-01T14:09:58.426358",
    "estado": "completada"
  }
]
```

---

### Cuentas

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api/cuentas/{usuario_id}/` | Listar cuentas de un usuario |
| `GET` | `/api/cuentas/{usuario_id}/{moneda}/` | Obtener cuenta específica |

#### `GET /api/cuentas/{usuario_id}/`

**Response (200):**
```json
[
  {"id": 1, "moneda": "ARS", "saldo": 1500.0},
  {"id": 2, "moneda": "USD", "saldo": 100.0}
]
```

---

#### `GET /api/cuentas/{usuario_id}/{moneda}/`

Moneda: `ARS` o `USD`.

**Response (200):**
```json
{
  "id": 1,
  "moneda": "ARS",
  "saldo": 1500.0
}
```

---

### Operaciones

| Método | Ruta | Descripción |
|---|---|---|
| `POST` | `/api/operaciones/transferir` | Transferencia directa entre usuarios |
| `POST` | `/api/operaciones/iniciar-transferencia` | Iniciar transferencia por alias (2 pasos) |
| `POST` | `/api/operaciones/confirmar-transferencia` | Confirmar transferencia con código |
| `POST` | `/api/operaciones/conversion` | Conversión entre monedas |
| `POST` | `/api/operaciones/pago` | Realizar un pago |

#### `POST /api/operaciones/transferir`

**Request:**
```json
{
  "origen_usuario_id": 1,
  "destino_usuario_id": 2,
  "moneda": "ARS",
  "monto": 500.0
}
```

**Response (200):**
```json
{
  "transferencia_id": 1,
  "origen_saldo": 500.0,
  "destino_saldo": 1000.0
}
```

---

#### `POST /api/operaciones/iniciar-transferencia`

Inicia una transferencia de 2 pasos. Envia un código de confirmación por email.

**Request:**
```json
{
  "origen_usuario_id": 1,
  "destino_alias": "juanperez",
  "moneda": "ARS",
  "monto": 200.0
}
```

**Response (200):**
```json
{
  "mensaje": "Codigo de confirmacion enviado a tu email"
}
```

---

#### `POST /api/operaciones/confirmar-transferencia`

Confirma la transferencia con el código recibido por email.

**Request:**
```json
{
  "origen_usuario_id": 1,
  "codigo": "654321"
}
```

**Response (200):**
```json
{
  "estado": "completada",
  "detalle": {
    "transferencia_id": 2,
    "origen_saldo": 800.0,
    "destino_saldo": 1200.0
  }
}
```

---

#### `POST /api/operaciones/conversion**

**Request:**
```json
{
  "usuario_id": 1,
  "monto_origen": 1000,
  "moneda_origen": "ARS",
  "monto_destino": 0.82,
  "moneda_destino": "USD",
  "tasa": 1220.0
}
```

**Response (200):**
```json
{
  "cuenta_origen_saldo": 0.0,
  "cuenta_destino_saldo": 0.82,
  "tasa": 1220.0
}
```

---

#### `POST /api/operaciones/pago`

**Request:**
```json
{
  "usuario_id": 1,
  "monto": 300.0,
  "descripcion": "Pago de servicios"
}
```

**Response (200):**
```json
{
  "pago_id": 1,
  "saldo_restante": 500.0
}
```

---

### Payment Gateway

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api/payments/cotizacion` | Obtener cotización del dólar |
| `POST` | `/api/payments/conversiones` | Conversión con tasa en vivo |
| `POST` | `/api/payments/pagos` | Realizar un pago (desde gateway) |
| `POST` | `/api/payments/transferencias` | Transferencia (desde gateway) |

#### `GET /api/payments/cotizacion`

**Query params:** `tipo` (opcional, default: `blue`). Valores: `blue`, `oficial`.

Obtiene la cotización desde [DolarAPI](https://dolarapi.com). Si falla, usa valores de fallback.

**Response (200):**
```json
{
  "tipo": "blue",
  "compra": 1200.0,
  "venta": 1220.0,
  "fecha": "2026-07-01T14:00:00.000Z",
  "fuente": "dolarapi.com"
}
```

---

#### `POST /api/payments/conversiones`

Convierte entre ARS y USD usando la cotización en vivo de DolarAPI.

**Request:**
```json
{
  "usuario_id": 1,
  "monto": 1000,
  "desde": "ARS",
  "hacia": "USD"
}
```

**Response (200):**
```json
{
  "monto_origen": 1000,
  "moneda_origen": "ARS",
  "monto_destino": 0.82,
  "moneda_destino": "USD",
  "tasa": 1220.0,
  "resultado": {
    "cuenta_origen_saldo": 0.0,
    "cuenta_destino_saldo": 0.82,
    "tasa": 1220.0
  }
}
```

---

#### `POST /api/payments/pagos`

**Request:**
```json
{
  "usuario_id": 1,
  "monto": 300.0,
  "descripcion": "Pago de servicios"
}
```

**Response (200):**
```json
{
  "estado": "completada",
  "detalle": {
    "pago_id": 1,
    "saldo_restante": 500.0
  }
}
```

---

#### `POST /api/payments/transferencias`

**Request:**
```json
{
  "origen_usuario_id": 1,
  "destino_usuario_id": 2,
  "moneda": "ARS",
  "monto": 200.0
}
```

**Response (200):**
```json
{
  "estado": "completada",
  "detalle": {
    "transferencia_id": 1,
    "origen_saldo": 800.0,
    "destino_saldo": 1200.0
  }
}
```

---

### Health Check

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/health/` | Health check |

**Response (200):**
```json
{
  "status": "ok"
}
```

---

## Formato de errores

Todos los errores siguen el formato:

```json
{
  "detail": "Mensaje descriptivo del error"
}
```

Códigos de estado utilizados:
- `400` — Error de validación (datos incorrectos, saldo insuficiente, etc.)
- `401` — Credenciales inválidas
- `403` — Acción prohibida (ej. login sin verificar email)
- `404` — Recurso no encontrado
- `502` — Error al comunicarse con servicios externos

---

## Notas

- Las contraseñas se almacenan en texto plano (simulador educativo).
- No se usa autenticación por tokens; la sesión se maneja desde el frontend con `usuario_id`.
- Al registrar, se crean automáticamente cuentas en ARS y USD con saldo 0.
- El alias se genera automáticamente a partir del nombre.
- La cotización del dólar se obtiene de [DolarAPI](https://dolarapi.com) con fallback a valores fijos.
- Si no hay configuración SMTP, los emails se omiten silenciosamente.
