# Billetera Virtual

Sistema completo de billetera virtual con autenticación, cuentas en ARS/USD, transferencias con confirmación OTP por correo electrónico y cotización del dólar vía API del BCRA.

---

## Stack Tecnológico

| Componente | Tecnología | Puerto |
|---|---|---|
| **Backend (API REST)** | Kotlin 2.3 + Spring Boot 4.1 + Java 25 | `8080` |
| **Payment Gateway** | Python 3.10+ / Flask 3.1 | `5001` |
| **Reverse Proxy** | Python puro (`http.server`, sin nginx) | `8000` |
| **Frontend** | HTML5 + CSS3 + JavaScript vanilla | `3000` |
| **Base de Datos** | PostgreSQL 16 (Docker) | `5432` |

---

## Arquitectura

```
                          ┌──────────────────┐
                          │    Frontend SPA   │
                          │  localhost:3000   │
                          └────────┬─────────┘
                                   │ Todas las llamadas pasan por:
                                   ▼
                    ┌──────────────────────────────────┐
                    │     Reverse Proxy (Python)        │
                    │        localhost:8000             │
                    │                                  │
                    │  /api/auth/*     ─────┐           │
                    │  /api/wallet/*    ─────┤           │
                    │  /api/rates/*     ─────┼────┐      │
                    │  /api/payments/*  ─────┼────┤      │
                    └────────────────────────┼────┼──────┘
                                             │    │
                    ┌────────────────────────┘    └──────────────┐
                    ▼                                            ▼
    ┌───────────────────────────────┐          ┌──────────────────────────────┐
    │  Backend (Kotlin + Spring)    │          │  Payment Gateway (Python)     │
    │  localhost:8080               │          │  localhost:5001               │
    │                               │          │                               │
    │  Auth: registro, login,       │          │  GET  /api/rates/usd          │
    │  validar-email, olvide/reset  │          │    → BCRA (cotización USD)    │
    │  password, sesiones           │          │                               │
    │                               │          │  POST /api/payments/transferir│
    │  Wallet: saldos, movimientos  │          │    /iniciar → valida fondos,  │
    │                               │          │    crea movimiento PENDIENTE, │
    │  DB: PostgreSQL               │          │    envía OTP por email       │
    └───────────────────────────────┘          │                               │
                                               │  POST /api/payments/transferir│
                                               │    /confirmar → verifica OTP, │
                                               │    debita origen, acredita    │
                                               │    destino, COMPLETADO        │
                                               │                               │
                                               │  Email: smtplib + Gmail API   │
                                               │  DB: psycopg2 (directo)       │
                                               └──────────────────────────────┘
```

---

## Estructura del Proyecto

```
backend/
├── backend/                    # API REST (Kotlin + Spring Boot)
│   ├── src/main/kotlin/com/billeteravirtual/backend/
│   │   ├── BackendApplication.kt       # Entry point
│   │   ├── config/SecurityConfig.kt    # Spring Security (CSRF off, rutas públicas)
│   │   ├── controller/
│   │   │   ├── AuthController.kt       # /api/auth/*
│   │   │   └── WalletController.kt     # /api/wallet/*
│   │   ├── dto/request/                # DTOs de entrada
│   │   ├── dto/response/               # DTOs de salida
│   │   ├── models/                     # Entidades JPA (Usuario, Cuenta, Movimiento, Enums)
│   │   ├── repository/                 # JPA Repositories
│   │   ├── security/                   # CustomUserDetailsService
│   │   └── service/                    # AuthService, WalletService, UsuarioService
│   ├── build.gradle.kts
│   └── src/main/resources/application.yaml
│
├── payment-gateway/            # Pasarela de pago (Python + Flask)
│   ├── app.py                  # Cotización BCRA, transferencias, envío de correos SMTP
│   ├── requirements.txt        # flask, requests, python-dotenv, psycopg2-binary
│   └── .env.example            # Template de configuración SMTP Gmail
│
├── proxy/                      # Reverse Proxy propio (Python, sin nginx)
│   └── proxy.py                # 95 líneas, enruta por prefijo de URL
│
├── frontend/                   # Interfaz web SPA
│   ├── index.html              # Login
│   ├── register.html           # Registro
│   ├── verify-email.html       # Verificación OTP 6 dígitos
│   ├── forgot-password.html    # Recuperar contraseña
│   ├── reset-password.html     # Nueva contraseña
│   ├── dashboard.html          # Panel principal
│   ├── styles.css              # Estilos (tema oscuro, glassmorphism)
│   └── app.js                  # Helpers de API (apiFetch, alertas, formatos)
│
├── docker-compose.yml          # PostgreSQL 16
├── DOCUMENTACION.md            # Documentación detallada de endpoints
└── README.md                   # Este archivo
```

---

## Requisitos

| Herramienta | Versión |
|---|---|
| Java JDK | 25 |
| Kotlin | 2.3.x |
| Docker | 24+ |
| Docker Compose | 2.x |
| Python | 3.10+ |

---

## Paso a Paso para Poner en Marcha

### 1. Clonar el repositorio

```bash
git clone <repo-url>
cd backend
```

### 2. Iniciar PostgreSQL con Docker

```bash
docker compose up -d
```

Esto levanta PostgreSQL 16 en `localhost:5432`, base `billetera_virtual`, usuario `user`, password `password`. Los datos persisten en el volumen `pgdata`.

### 3. Configurar el Payment Gateway

```bash
cd payment-gateway
cp .env.example .env
# Editar .env con credenciales de Gmail:
#   SMTP_USER=tu-correo@gmail.com
#   SMTP_PASSWORD=contraseña-de-aplicación
pip install -r requirements.txt
```

> Para generar una contraseña de aplicación de Gmail: activar verificación en dos pasos en la cuenta Google → ir a "Contraseñas de aplicación" → generar una para "Correo".

### 4. Iniciar el Backend (Spring Boot)

```bash
cd backend
./gradlew bootRun
```

Arranca en `http://localhost:8080`. Las tablas se crean automáticamente con `ddl-auto: update`.

### 5. Iniciar el Payment Gateway

```bash
cd payment-gateway
python app.py
```

Arranca en `http://localhost:5001`.

### 6. Iniciar el Reverse Proxy

```bash
cd proxy
python proxy.py
```

Arranca en `http://localhost:8000`. Es el punto de entrada único para todas las APIs.

### 7. Servir el Frontend

```bash
cd frontend
python3 -m http.server 3000
```

---

## Acceder a la Aplicación

| Servicio | URL |
|---|---|
| Frontend | http://localhost:3000 |
| Reverse Proxy (entry point API) | http://localhost:8000 |
| Backend (directo) | http://localhost:8080 |
| Payment Gateway (directo) | http://localhost:5001 |

> El frontend se comunica exclusivamente con el proxy (`:8000`), que redirige cada petición al servicio correspondiente.

---

## Flujo de Uso

```
1. Registrarse           → POST /api/auth/registro
2. Validar email         → Ingresar código OTP de 6 dígitos recibido por mail
3. Iniciar sesión        → POST /api/auth/login (email o DNI + contraseña)
4. Ver saldos            → Dashboard muestra cuentas ARS y USD
5. Consultar cotización  → GET /api/rates/usd (BCRA)
6. Iniciar transferencia → Ingresar alias destino, moneda y monto
                            → Llega código OTP al correo
7. Confirmar transfer.   → Ingresar código OTP recibido por correo
                            → Se debita origen y acredita destino
8. Ver movimientos       → Historial completo de transferencias
```

---

## Probar con curl

```bash
# Registrar usuario
curl -X POST http://localhost:8000/api/auth/registro \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"12345678","nombreCompleto":"Test User","dni":"12345678","fechaNacimiento":"1990-01-01"}'

# Verificar email
curl -X POST http://localhost:8000/api/auth/validar-email \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","codigo":"123456"}'

# Login (guarda cookie)
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{"identificador":"test@test.com","password":"12345678"}'

# Ver estado de billetera
curl http://localhost:8000/api/wallet/estado -b cookies.txt

# Cotización dólar (BCRA)
curl http://localhost:8000/api/rates/usd

# Iniciar transferencia
curl -X POST http://localhost:8000/api/payments/transferir/iniciar \
  -H "Content-Type: application/json" \
  -d '{"email_remitente":"test@test.com","cuenta_origen":"ARS","alias_destino":"otro.usuario.ars","monto":1000}'

# Confirmar transferencia
curl -X POST http://localhost:8000/api/payments/transferir/confirmar \
  -H "Content-Type: application/json" \
  -d '{"id_transaccion":"uuid","codigo_autorizacion":"123456"}'
```

---

## Documentación de Endpoints

Ver `DOCUMENTACION.md` para la documentación detallada de cada ruta con ejemplos de request/response y modelo de base de datos.
