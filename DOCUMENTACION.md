# Documentación de API - Billetera Virtual

## Arquitectura del Sistema

El sistema está compuesto por tres servicios independientes:

| Servicio | Tecnología | Puerto | Descripción |
|---|---|---|---|
| **Backend** | Kotlin + Spring Boot | `8080` | Autenticación, gestión de usuarios y consulta de billetera |
| **Payment Gateway** | Python + Flask | `5001` | Cotización de divisas, transferencias, envío de correos |
| **Reverse Proxy** | Python (http.server) | `8000` | Enrutamiento de peticiones al servicio correspondiente |

```
Cliente → Reverse Proxy (:8000) → Backend (:8080) para /api/auth/* y /api/wallet/*
                              → Payment Gateway (:5001) para /api/rates/* y /api/payments/*
```

---

## Servicio: Backend

### A.1) Registro de Usuario
`POST /api/auth/registro`

Registra un nuevo usuario y crea sus cuentas (ARS y USD) automáticamente.

**Request:**
```json
{
  "email": "usuario@ejemplo.com",
  "password": "PasswordSeguro123",
  "nombre_completo": "Juan Perez",
  "dni": "12345678",
  "fecha_nacimiento": "1990-05-15"
}
```

**Response (201 Created):**
```json
{
  "mensaje": "Registro exitoso. Revisa tu correo para verificar tu email.",
  "success": true
}
```

**Response (400 Bad Request):**
```json
{
  "mensaje": "El email ya está registrado",
  "success": false
}
```

---

### A.2) Validación de Correo Electrónico
`POST /api/auth/validar-email`

Valida el correo electrónico con el código de 6 dígitos enviado al email.

**Request:**
```json
{
  "email": "usuario@ejemplo.com",
  "codigo": "482910"
}
```

**Response (200 OK):**
```json
{
  "mensaje": "Email verificado exitosamente",
  "success": true
}
```

**Response (400 Bad Request):**
```json
{
  "mensaje": "Código inválido",
  "success": false
}
```

---

### A.3) Inicio de Sesión
`POST /api/auth/login`

Autentica al usuario mediante sesión con cookies (Spring Session JDBC). El campo `identificador` puede ser un email o un DNI. La cookie `JSESSIONID` se configura automáticamente.

**Request:**
```json
{
  "identificador": "usuario@ejemplo.com",
  "password": "PasswordSeguro123"
}
```

**Response (200 OK):**
```json
{
  "mensaje": "Inicio de sesión exitoso",
  "success": true
}
```

---

### A.6) Obtener Usuario Actual
`GET /api/auth/me`

Obtiene los datos del usuario autenticado (requiere sesión activa).

**Response (200 OK):**
```json
{
  "email": "usuario@ejemplo.com",
  "nombreCompleto": "Juan Perez"
}
```

**Response (401 Unauthorized):**
```json
{
  "mensaje": "Credenciales inválidas",
  "success": false
}
```

---

### A.4) Olvidé mi Contraseña
`POST /api/auth/olvide-password`

Solicita un link de recuperación de contraseña. Se envía al correo del usuario.

**Request:**
```json
{
  "email": "usuario@ejemplo.com"
}
```

**Response (200 OK):**
```json
{
  "mensaje": "Revisa tu correo para restablecer tu contraseña",
  "success": true
}
```

---

### A.5) Restablecer Contraseña
`POST /api/auth/reset-password`

Restablece la contraseña usando el token recibido por correo.

**Request:**
```json
{
  "tokenUrl": "uuid-del-token",
  "nuevaPassword": "NuevaPass123",
  "confirmarPassword": "NuevaPass123"
}
```

**Response (200 OK):**
```json
{
  "mensaje": "Contraseña actualizada exitosamente",
  "success": true
}
```

---

### B.1) Obtener Estado de la Billetera
`GET /api/wallet/estado`

Obtiene el saldo y alias de todas las cuentas del usuario autenticado.

**Headers:**
```
Cookie: JSESSIONID=<session-id>
```

**Response (200 OK):**
```json
{
  "usuario": "Juan Perez",
  "cuentas": [
    {
      "moneda": "ARS",
      "saldo": 150000.50,
      "alias": "juan.perez.ars"
    },
    {
      "moneda": "USD",
      "saldo": 350.00,
      "alias": "juan.perez.usd"
    }
  ]
}
```

---

### B.2) Historial de Movimientos
`GET /api/wallet/movimientos`

Obtiene el historial de movimientos del usuario autenticado.

**Headers:**
```
Cookie: JSESSIONID=<session-id>
```

**Response (200 OK):**
```json
[
  {
    "id": "uuid",
    "cuentaOrigenAlias": "juan.perez.ars",
    "cuentaDestinoAlias": "maria.gomez.ars",
    "monto": 5000.00,
    "moneda": "ARS",
    "tipo": "TRANSFERENCIA",
    "estado": "COMPLETADO",
    "fechaCreacion": "2024-10-25T10:00:00",
    "descripcion": "Transferencia de $5000 a maria.gomez.ars"
  }
]
```

---

## Servicio: Payment Gateway

### C.1) Cotización del Dólar
`GET /api/rates/usd`

Obtiene la cotización oficial del dólar desde la API del BCRA.

**Response (200 OK):**
```json
{
  "moneda_base": "USD",
  "moneda_destino": "ARS",
  "cotizacion_oficial": 950.50,
  "fecha_actualizacion": "2024-10-25T10:00:00Z"
}
```

---

### C.2) Iniciar Transferencia
`POST /api/payments/transferir/iniciar`

Inicia una transferencia. Verifica fondos, crea el movimiento en estado `PENDIENTE_AUTORIZACION` y envía un código OTP de 6 dígitos al correo del remitente.

**Request:**
```json
{
  "email_remitente": "usuario@ejemplo.com",
  "cuenta_origen": "ARS",
  "alias_destino": "maria.gomez.ars",
  "monto": 5000.00
}
```

**Response (202 Accepted):**
```json
{
  "mensaje": "Transferencia iniciada. Revisa tu correo para autorizar.",
  "success": true,
  "id_transaccion": "uuid-de-la-transaccion"
}
```

**Response (400 Bad Request):**
```json
{
  "mensaje": "Saldo insuficiente",
  "success": false
}
```

---

### C.3) Confirmar Transferencia
`POST /api/payments/transferir/confirmar`

Confirma la transferencia con el código OTP recibido por correo. Descuenta el saldo del origen y acredita en el destino.

**Request:**
```json
{
  "id_transaccion": "uuid-de-la-transaccion",
  "codigo_autorizacion": "123456"
}
```

**Response (200 OK):**
```json
{
  "mensaje": "Transferencia confirmada exitosamente",
  "success": true,
  "id_transaccion": "uuid-de-la-transaccion"
}
```

**Response (400 Bad Request):**
```json
{
  "mensaje": "Código de autorización inválido",
  "success": false
}
```

---

## Servicio: Reverse Proxy

El proxy corre en el puerto `8000` y enruta automáticamente según el path:

| Ruta | Destino |
|---|---|
| `/api/auth/*` | Backend (`:8080`) |
| `/api/wallet/*` | Backend (`:8080`) |
| `/api/rates/*` | Payment Gateway (`:5001`) |
| `/api/payments/*` | Payment Gateway (`:5001`) |

El proxy no utiliza nginx ni ningún otro software preexistente; está desarrollado manualmente en Python usando la librería estándar `http.server`.

---

## Modelo de Base de Datos (PostgreSQL)

### Tabla: `usuarios`

| Columna | Tipo | Descripción |
|---|---|---|
| `id` | UUID (PK) | Identificador único |
| `dni` | VARCHAR(20), UNIQUE | Documento nacional de identidad |
| `email` | VARCHAR(255), UNIQUE | Correo electrónico |
| `password_hash` | TEXT | Contraseña hasheada (BCrypt) |
| `nombre_completo` | VARCHAR(255) | Nombre completo |
| `fecha_nacimiento` | DATE | Fecha de nacimiento |
| `estado_email` | ENUM('PENDIENTE','VERIFICADO') | Estado de verificación del email |
| `codigo_verificacion_email` | VARCHAR(6) | Código de 6 dígitos para verificación |
| `token_recuperacion_pass` | VARCHAR(255) | Token para recuperación de contraseña |

### Tabla: `cuentas`

| Columna | Tipo | Descripción |
|---|---|---|
| `id` | UUID (PK) | Identificador único |
| `usuario_id` | UUID (FK) | Referencia al usuario dueño |
| `moneda` | ENUM('ARS','USD') | Tipo de moneda |
| `saldo` | DECIMAL(19,2) | Saldo disponible |
| `alias` | VARCHAR(100), UNIQUE | Alias único para transferencias |

### Tabla: `movimientos`

| Columna | Tipo | Descripción |
|---|---|---|
| `id` | UUID (PK) | Identificador único |
| `cuenta_origen_id` | UUID (FK, nullable) | Cuenta de origen (null en depósitos) |
| `cuenta_destino_id` | UUID (FK) | Cuenta de destino |
| `monto` | DECIMAL(19,2) | Monto transferido |
| `tipo_movimiento` | ENUM('TRANSFERENCIA','DEPOSITO','RETIRO') | Tipo de movimiento |
| `estado_movimiento` | ENUM('PENDIENTE_AUTORIZACION','COMPLETADO','FALLIDO') | Estado del movimiento |
| `descripcion` | VARCHAR(500) | Descripción opcional |
| `fecha_creacion` | TIMESTAMP | Fecha de creación |
| `fecha_autorizacion` | TIMESTAMP | Fecha de autorización (nullable) |
| `codigo_autorizacion` | VARCHAR(6) | Código OTP para autorizar transferencia |

---

## Flujo Completo de Transferencia

```
1. POST /api/payments/transferir/iniciar
   ├── Payment Gateway verifica fondos
   ├── Crea movimiento en PENDIENTE_AUTORIZACION
   └── Envía código OTP por email al remitente

2. POST /api/payments/transferir/confirmar
   ├── Payment Gateway valida el código OTP
   ├── Descuenta saldo de la cuenta origen
   ├── Acredita saldo en la cuenta destino
   └── Actualiza movimiento a COMPLETADO
```

---

## Cómo Ejecutar

```bash
# 1. Backend (Spring Boot)
cd backend/
./gradlew bootRun

# 2. Payment Gateway
cd payment-gateway/
pip install -r requirements.txt
python app.py

# 3. Reverse Proxy
cd proxy/
python proxy.py
```

El punto de entrada para el frontend es `http://localhost:8000`.

---

## Frontend

El frontend es una aplicación web SPA de páginas múltiples ubicada en `frontend/`.

### Páginas

| Archivo | Descripción |
|---|---|
| `index.html` | Inicio de sesión |
| `register.html` | Registro de usuario |
| `verify-email.html` | Verificación de email con código OTP de 6 dígitos |
| `forgot-password.html` | Solicitud de recuperación de contraseña |
| `reset-password.html` | Creación de nueva contraseña |
| `dashboard.html` | Panel principal: saldos, transferencias e historial |

### Diseño

- Interfaz oscura moderna con acentos en cian (`#06b6d4`) y verde (`#10b981`)
- Gradientes y efectos glassmorphism (blur + backdrop-filter)
- Componentes: cards de saldo, tabs de moneda, inputs OTP, modales de confirmación
- Totalmente responsivo

### Para servir el frontend

```bash
cd frontend/
python3 -m http.server 3000
# o cualquier servidor estático
```

Luego acceder a `http://localhost:3000` (o a través del proxy en `http://localhost:8000`).
