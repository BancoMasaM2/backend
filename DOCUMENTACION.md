# Documentación de API - Billetera Virtual

## Arquitectura del Sistema

El sistema está compuesto por tres servicios independientes más un frontend SPA:

| Componente | Tecnología | Puerto | Descripción |
|---|---|---|---|
| **Backend** | Kotlin + Spring Boot 4.1 | `8080` | Autenticación, gestión de usuarios y consulta de billetera |
| **Payment Gateway** | Python + Flask 3.1 | `5001` | Cotización de divisas (BCRA), transferencias, envío de correos SMTP |
| **Reverse Proxy** | Python (`http.server`) | `8000` | Enrutamiento de peticiones al servicio correspondiente |
| **Frontend** | HTML5 + CSS3 + JS vanilla | `3000` | Interfaz de usuario SPA multipágina |

### Diagrama de Arquitectura

```
Cliente (Frontend :3000)
       │
       ▼
Reverse Proxy (:8000)
       │
       ├── /api/auth/*     ──► Backend (:8080)
       ├── /api/wallet/*   ──► Backend (:8080)
       ├── /api/rates/*    ──► Payment Gateway (:5001)
       └── /api/payments/* ──► Payment Gateway (:5001)
```

### Base de Datos Compartida

Tanto el Backend como el Payment Gateway acceden a la misma base de datos PostgreSQL:
- **Backend**: mediante JPA/Hibernate (Spring Data JPA)
- **Payment Gateway**: mediante psycopg2 (SQL directo)

---

## Endpoints del Backend

### A.1) Registro de Usuario

`POST /api/auth/registro`

Registra un nuevo usuario. Crea automáticamente dos cuentas (una en ARS y otra en USD) con alias generados a partir del nombre completo. El email queda en estado `PENDIENTE` hasta ser verificado.

**Request:**
```json
{
  "email": "usuario@ejemplo.com",
  "password": "PasswordSeguro123",
  "nombreCompleto": "Juan Perez",
  "dni": "12345678",
  "fechaNacimiento": "1990-05-15"
}
```

**Response (201 Created):**
```json
{
  "mensaje": "Registro exitoso. Revisa tu correo para verificar tu email.",
  "success": true
}
```

**Response (400 Bad Request) — email duplicado:**
```json
{
  "mensaje": "El email ya está registrado",
  "success": false
}
```

**Response (400 Bad Request) — DNI duplicado:**
```json
{
  "mensaje": "El DNI ya está registrado",
  "success": false
}
```

---

### A.2) Validación de Correo Electrónico

`POST /api/auth/validar-email`

Valida el correo electrónico ingresando el código de 6 dígitos. El código se genera durante el registro y se almacena en `codigo_verificacion_email`. Al validar, cambia `estadoEmail` a `VERIFICADO`.

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

Autentica al usuario mediante sesión con cookies (Spring Session JDBC). El campo `identificador` acepta tanto email como DNI. La cookie `JSESSIONID` (httpOnly) se configura automáticamente en la respuesta. Timeout de sesión: 30 minutos.

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

Genera un token UUID de recuperación y lo almacena en `tokenRecuperacionPass` del usuario. El frontend muestra un mensaje genérico de éxito por seguridad (no revela si el email existe o no).

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

Restablece la contraseña usando el token UUID recibido. Valida que `nuevaPassword` coincida con `confirmarPassword` y que el token exista en la base de datos.

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

**Response (400 Bad Request) — contraseñas no coinciden:**
```json
{
  "mensaje": "Las contraseñas no coinciden",
  "success": false
}
```

**Response (400 Bad Request) — token inválido:**
```json
{
  "mensaje": "Token inválido o expirado",
  "success": false
}
```

---

### A.6) Obtener Usuario Actual

`GET /api/auth/me`

Obtiene los datos del usuario autenticado mediante la sesión activa (requiere cookie `JSESSIONID`).

**Headers:**
```
Cookie: JSESSIONID=<session-id>
```

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

### B.1) Obtener Estado de la Billetera

`GET /api/wallet/estado`

Obtiene el saldo y alias de todas las cuentas (ARS y USD) del usuario autenticado.

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

Obtiene el historial de movimientos del usuario autenticado, ordenado por fecha de creación descendente (más reciente primero). Incluye transferencias donde el usuario sea origen o destino.

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
  },
  {
    "id": "uuid",
    "cuentaOrigenAlias": "juan.perez.usd",
    "cuentaDestinoAlias": "pedro.lopez.usd",
    "monto": 100.00,
    "moneda": "USD",
    "tipo": "TRANSFERENCIA",
    "estado": "PENDIENTE_AUTORIZACION",
    "fechaCreacion": "2024-10-24T15:30:00",
    "descripcion": "Transferencia de $100 a pedro.lopez.usd"
  }
]
```

---

## Endpoints del Payment Gateway

### C.1) Cotización del Dólar (BCRA)

`GET /api/rates/usd`

Obtiene la cotización oficial del dólar estadounidense desde la API de Estadísticas Cambiarias del BCRA (`https://api.bcra.gob.ar/estadisticascambiarias/v1.0/Cotizaciones`). Busca la cotización con `codigoMoneda = "USD"`.

**Response (200 OK):**
```json
{
  "moneda_base": "USD",
  "moneda_destino": "ARS",
  "cotizacion_oficial": 950.50,
  "fecha_actualizacion": "2024-10-25T10:00:00Z"
}
```

**Response (200 OK) — error en BCRA:**
```json
{
  "moneda_base": "USD",
  "moneda_destino": "ARS",
  "cotizacion_oficial": 0.0,
  "fecha_actualizacion": ""
}
```

---

### C.2) Iniciar Transferencia

`POST /api/payments/transferir/iniciar`

Inicia una transferencia entre usuarios. **Fase 1 del proceso de 2 fases.**
1. Valida que exista la cuenta origen (email + moneda) y la cuenta destino (alias)
2. Verifica saldo suficiente
3. Genera un código OTP de 6 dígitos
4. Crea un movimiento en estado `PENDIENTE_AUTORIZACION`
5. Envía el código OTP por correo electrónico al remitente vía Gmail SMTP

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

**Response (400 Bad Request) — saldo insuficiente:**
```json
{
  "mensaje": "Saldo insuficiente",
  "success": false
}
```

**Response (400 Bad Request) — alias destino no existe:**
```json
{
  "mensaje": "Alias destino no encontrado",
  "success": false
}
```

**Email enviado al remitente:**
```
Asunto: Código de autorización - Transferencia Billetera Virtual

Has solicitado una transferencia de $5000.00 ARS
a la cuenta: maria.gomez.ars

Tu código de autorización es: 482910

Si no solicitaste esta transferencia, ignorá este mensaje.
```

---

### C.3) Confirmar Transferencia

`POST /api/payments/transferir/confirmar`

Confirma la transferencia con el código OTP recibido por correo. **Fase 2 del proceso de 2 fases.**
1. Bloquea el movimiento con `SELECT ... FOR UPDATE` (pessimistic lock)
2. Valida que el movimiento exista y esté en `PENDIENTE_AUTORIZACION`
3. Valida que el código OTP coincida
4. Bloquea la cuenta origen con `SELECT ... FOR UPDATE`
5. Re-verifica saldo suficiente (protección contra race conditions)
6. Debita el monto de la cuenta origen
7. Acredita el monto en la cuenta destino
8. Actualiza el movimiento a `COMPLETADO`

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

El proxy corre en el puerto `8000` y es el punto de entrada único para todas las APIs. Está desarrollado íntegramente en Python con la biblioteca estándar (`http.server`), sin utilizar nginx ni ningún otro software preexistente.

### Enrutamiento

| Ruta | Método | Destino | Servicio |
|---|---|---|---|
| `/api/auth/*` | Cualquiera | `http://localhost:8080` | Backend |
| `/api/wallet/*` | Cualquiera | `http://localhost:8080` | Backend |
| `/api/rates/*` | Cualquiera | `http://localhost:5001` | Payment Gateway |
| `/api/payments/*` | Cualquiera | `http://localhost:5001` | Payment Gateway |

### Comportamiento

- Reenvía el método HTTP, headers (excepto `Host` y `Transfer-Encoding`) y body originales
- Recalcula `Content-Length` automáticamente
- Propaga headers `Set-Cookie` para manejo de sesiones
- Errores HTTP (4xx/5xx) → se reenvían con el mismo código y body
- Error de conexión (servicio caído) → `502 Bad Gateway` con JSON

---

## Modelo de Base de Datos (PostgreSQL 16)

### Tabla: `usuarios`

| Columna | Tipo | Restricciones | Descripción |
|---|---|---|---|
| `id` | UUID | PK, default `gen_random_uuid()` | Identificador único del usuario |
| `dni` | VARCHAR(20) | UNIQUE, NOT NULL | Documento nacional de identidad |
| `email` | VARCHAR(255) | UNIQUE, NOT NULL | Correo electrónico |
| `password_hash` | TEXT | NOT NULL | Contraseña hasheada con BCrypt |
| `nombre_completo` | VARCHAR(255) | NOT NULL | Nombre completo del usuario |
| `fecha_nacimiento` | DATE | NOT NULL | Fecha de nacimiento |
| `estado_email` | VARCHAR(20) | NOT NULL, default `PENDIENTE` | Estado de verificación: `PENDIENTE`, `VERIFICADO` |
| `codigo_verificacion_email` | VARCHAR(6) | nullable | Código OTP de 6 dígitos para verificar email |
| `token_recuperacion_pass` | VARCHAR(255) | nullable | Token UUID para recuperación de contraseña |

### Tabla: `cuentas`

| Columna | Tipo | Restricciones | Descripción |
|---|---|---|---|
| `id` | UUID | PK | Identificador único de la cuenta |
| `usuario_id` | UUID | FK → usuarios(id), NOT NULL | Referencia al usuario propietario |
| `moneda` | VARCHAR(3) | NOT NULL | Tipo de moneda: `ARS` o `USD` |
| `saldo` | DECIMAL(19,2) | NOT NULL, default 0.00 | Saldo disponible |
| `alias` | VARCHAR(100) | UNIQUE, NOT NULL | Alias único para transferencias |

**Nota:** Al registrarse, cada usuario recibe automáticamente dos cuentas:
- ARS con alias `{nombre}.{apellido}.ars`
- USD con alias `{nombre}.{apellido}.usd`

### Tabla: `movimientos`

| Columna | Tipo | Restricciones | Descripción |
|---|---|---|---|
| `id` | UUID | PK | Identificador único del movimiento |
| `cuenta_origen_id` | UUID | FK → cuentas(id), nullable | Cuenta de origen (null en depósitos) |
| `cuenta_destino_id` | UUID | FK → cuentas(id), NOT NULL | Cuenta de destino |
| `monto` | DECIMAL(19,2) | NOT NULL | Monto transferido |
| `tipo_movimiento` | VARCHAR(20) | NOT NULL | Tipo: `TRANSFERENCIA`, `DEPOSITO`, `RETIRO` |
| `estado_movimiento` | VARCHAR(20) | NOT NULL, default `PENDIENTE_AUTORIZACION` | Estado: `PENDIENTE_AUTORIZACION`, `COMPLETADO`, `FALLIDO` |
| `descripcion` | VARCHAR(500) | nullable | Descripción legible del movimiento |
| `fecha_creacion` | TIMESTAMP | NOT NULL, updatable=false | Fecha y hora de creación |
| `fecha_autorizacion` | TIMESTAMP | nullable | Fecha y hora de autorización/confirmación |
| `codigo_autorizacion` | VARCHAR(6) | nullable | Código OTP de 6 dígitos para autorizar |

---

## Flujo Completo de Transferencia

### Fase 1: Iniciar

```
Cliente                              Payment Gateway                     DB
  │                                       │                              │
  │  POST /api/payments/transferir/iniciar │                              │
  │  {email_remitente, cuenta_origen,     │                              │
  │   alias_destino, monto}               │                              │
  │──────────────────────────────────────►│                              │
  │                                       │  Verificar alias destino     │
  │                                       │─────────────────────────────►│
  │                                       │◄─────────────────────────────│
  │                                       │  Verificar cuenta origen     │
  │                                       │─────────────────────────────►│
  │                                       │◄─────────────────────────────│
  │                                       │  Verificar saldo suficiente  │
  │                                       │  Generar OTP 6 dígitos       │
  │                                       │  INSERT movimiento PENDIENTE │
  │                                       │─────────────────────────────►│
  │                                       │  Enviar email con OTP        │
  │                                       │  (smtplib → Gmail SMTP)     │
  │  202 {id_transaccion, success}        │                              │
  │◄──────────────────────────────────────│                              │
```

### Fase 2: Confirmar

```
Cliente                              Payment Gateway                     DB
  │                                       │                              │
  │  POST /api/payments/transferir/confirmar│                             │
  │  {id_transaccion, codigo_autorizacion} │                              │
  │──────────────────────────────────────►│                              │
  │                                       │  SELECT ... FOR UPDATE       │
  │                                       │  (bloquea movimiento)        │
  │                                       │─────────────────────────────►│
  │                                       │  Validar OTP y estado        │
  │                                       │  SELECT ... FOR UPDATE       │
  │                                       │  (bloquea cuenta origen)     │
  │                                       │─────────────────────────────►│
  │                                       │  Re-validar saldo            │
  │                                       │  UPDATE saldo origen -= monto│
  │                                       │─────────────────────────────►│
  │                                       │  UPDATE saldo destino += monto│
  │                                       │─────────────────────────────►│
  │                                       │  UPDATE movimiento COMPLETADO│
  │                                       │─────────────────────────────►│
  │  200 {id_transaccion, success}        │                              │
  │◄──────────────────────────────────────│                              │
```

---

## Configuración del Sistema de Correos

El envío de correos electrónicos se realiza desde el Payment Gateway mediante `smtplib` conectándose al servidor SMTP de Gmail.

### Variables de Entorno (`.env`)

| Variable | Default | Descripción |
|---|---|---|
| `SMTP_SERVER` | `smtp.gmail.com` | Servidor SMTP |
| `SMTP_PORT` | `587` | Puerto TLS |
| `SMTP_USER` | — | Dirección de Gmail |
| `SMTP_PASSWORD` | — | Contraseña de aplicación de Gmail |
| `BACKEND_URL` | `http://localhost:8080` | URL del backend (para links en emails) |
| `DB_HOST` | `localhost` | Host de PostgreSQL |
| `DB_PORT` | `5432` | Puerto de PostgreSQL |
| `DB_NAME` | `billetera_virtual` | Nombre de la base de datos |
| `DB_USER` | `user` | Usuario de base de datos |
| `DB_PASSWORD` | `password` | Contraseña de base de datos |

### Tipos de Correos Enviados

| Contexto | Destinatario | Contenido |
|---|---|---|
| Inicio de transferencia | Remitente | Código OTP de 6 dígitos para autorizar la transferencia |

> **Nota:** El código de verificación de email (registro) y el token de recuperación de contraseña se generan y almacenan en la base de datos, pero su envío por correo debe implementarse como paso adicional.

---

## Seguridad

| Aspecto | Implementación |
|---|---|
| **Contraseñas** | Hasheadas con BCrypt (Spring Security) |
| **Sesiones** | Cookies HTTP-only, Spring Session JDBC, timeout 30 min |
| **CSRF** | Deshabilitado (SPA con cookie-based auth) |
| **Transferencias** | Two-phase commit con OTP + pessimistic locks (`FOR UPDATE`) |
| **Verificación email** | Código OTP de 6 dígitos |
| **Recuperación password** | Token UUID único |

---

## Frontend

### Páginas

| Archivo | Ruta | Descripción |
|---|---|---|
| `index.html` | `/` | Inicio de sesión (email/DNI + contraseña) |
| `register.html` | `/register.html` | Registro de usuario |
| `verify-email.html` | `/verify-email.html` | Ingreso de código OTP de 6 dígitos (campos individuales con auto-foco) |
| `forgot-password.html` | `/forgot-password.html` | Solicitud de recuperación de contraseña |
| `reset-password.html` | `/reset-password.html?token=...` | Creación de nueva contraseña |
| `dashboard.html` | `/dashboard.html` | Panel principal: saldos, cotización, transferencias, historial |

### Funcionalidades del Dashboard

- Visualización de saldos ARS y USD
- Cotización del dólar en tiempo real (desde BCRA)
- Formulario de transferencia con selector de moneda
- Modal de confirmación con ingreso de OTP
- Historial de movimientos con estados
- Botón de cierre de sesión

### Estilos

- Tema oscuro con acentos en cian (`#06b6d4`) y verde (`#10b981`)
- Efectos glassmorphism (backdrop-filter blur)
- Gradientes y sombras
- Diseño responsivo (sidebar colapsable en mobile)

---

## Cómo Ejecutar

```bash
# 1. Base de datos
docker compose up -d

# 2. Backend (Spring Boot)
cd backend/
./gradlew bootRun

# 3. Payment Gateway
cd payment-gateway/
cp .env.example .env   # configurar credenciales SMTP
pip install -r requirements.txt
python app.py

# 4. Reverse Proxy
cd proxy/
python proxy.py

# 5. Frontend
cd frontend/
python3 -m http.server 3000
```

Acceder a `http://localhost:3000` (frontend) o `http://localhost:8000` (API entry point).

---

## Resumen de Endpoints

| Método | Path | Auth | Servicio | Descripción |
|---|---|---|---|---|
| `POST` | `/api/auth/registro` | No | Backend | Registrar usuario + crear cuentas ARS/USD |
| `POST` | `/api/auth/validar-email` | No | Backend | Verificar email con código OTP |
| `POST` | `/api/auth/login` | No | Backend | Iniciar sesión (email/DNI + password) |
| `POST` | `/api/auth/olvide-password` | No | Backend | Solicitar token de recuperación |
| `POST` | `/api/auth/reset-password` | No | Backend | Restablecer contraseña con token |
| `GET` | `/api/auth/me` | Sí | Backend | Obtener perfil del usuario actual |
| `GET` | `/api/wallet/estado` | Sí | Backend | Obtener saldos y alias de cuentas |
| `GET` | `/api/wallet/movimientos` | Sí | Backend | Obtener historial de movimientos |
| `GET` | `/api/rates/usd` | No | Payment Gateway | Cotización oficial USD/ARS (BCRA) |
| `POST` | `/api/payments/transferir/iniciar` | No | Payment Gateway | Iniciar transferencia + enviar OTP por email |
| `POST` | `/api/payments/transferir/confirmar` | No | Payment Gateway | Confirmar transferencia con OTP |
