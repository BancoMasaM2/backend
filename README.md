# Billetera Virtual

Sistema completo de billetera virtual con autenticación, cuentas en ARS/USD, transferencias con confirmación por correo electrónico y cotización del dólar vía BCRA.

---

## 📦 Estructura del Proyecto

```
backend/
├── backend/             # API REST (Kotlin + Spring Boot) — Puerto 8080
│   ├── src/main/kotlin/com/billeteravirtual/backend/
│   │   ├── controller/   # AuthController, WalletController
│   │   ├── service/      # AuthService, WalletService, UsuarioService
│   │   ├── repository/   # JPA Repositories
│   │   ├── security/     # CustomUserDetailsService
│   │   ├── config/       # SecurityConfig
│   │   ├── dto/          # Request/Response DTOs
│   │   └── models/       # Usuario, Cuenta, Movimiento + Enums
│   └── build.gradle.kts
│
├── payment-gateway/     # Pasarela de pago (Python + Flask) — Puerto 5001
│   └── app.py           # Cotización BCRA, transferencias, envío de correos
│
├── proxy/               # Reverse Proxy (Python, sin nginx) — Puerto 8000
│   └── proxy.py
│
├── frontend/            # Interfaz web (HTML + CSS + JS)
│   ├── index.html           # Login
│   ├── register.html        # Registro
│   ├── verify-email.html    # Verificación con código OTP
│   ├── forgot-password.html # Recuperar contraseña
│   ├── reset-password.html  # Nueva contraseña
│   ├── dashboard.html       # Panel principal
│   ├── styles.css           # Estilos
│   └── app.js               # Helpers de API
│
├── DOCUMENTACION.md     # Documentación detallada de endpoints
└── README.md            # Este archivo
```

---

## ⚙️ Requisitos

| Herramienta | Versión |
|---|---|---|
| Java JDK | 25 |
| Kotlin | 2.3.x |
| Docker | 24+ |
| Docker Compose | 2.x |
| Python | 3.10+ |

---

## 🚀 Paso a Paso para Poner en Marcha

### 1. Clonar el repositorio

```bash
git clone <repo-url>
cd backend
```

### 2. Iniciar PostgreSQL con Docker

```bash
# Desde la raíz del proyecto
docker compose up -d
```

Esto levanta un contenedor con PostgreSQL 16 en `localhost:5432`, con la base `billetera_virtual`, usuario `user` y contraseña `password`.

> Para cambiar credenciales, editá `docker-compose.yml` y reflejalas en `backend/src/main/resources/application.yaml`.

### 3. Configurar el Payment Gateway

```bash
cd payment-gateway

# Copiar y configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales de Gmail para SMTP:
#   SMTP_USER=tu-correo@gmail.com
#   SMTP_PASSWORD=contraseña-de-aplicación

# Instalar dependencias
pip install -r requirements.txt
```

Para generar una contraseña de aplicación de Gmail:
1. Ir a https://myaccount.google.com/security
2. Activar verificación en dos pasos
3. Ir a "Contraseñas de aplicación"
4. Generar una para "Correo"

### 4. Iniciar el Backend (Spring Boot)

```bash
cd backend
./gradlew bootRun
```

El backend arranca en `http://localhost:8080`.
Las tablas se crean automáticamente gracias a `ddl-auto: update`.

### 5. Iniciar el Payment Gateway

```bash
cd payment-gateway
python app.py
```

El payment gateway arranca en `http://localhost:5001`.

### 6. Iniciar el Reverse Proxy

```bash
cd proxy
python proxy.py
```

El proxy arranca en `http://localhost:8000`.

### 7. Servir el Frontend

```bash
cd frontend
python3 -m http.server 3000
```

Opcional: el frontend también puede servirse desde el proxy si se agrega una ruta estática en `proxy.py`. Para development, usar el servidor de Python.

---

## 🌐 Acceder a la Aplicación

| Servicio | URL |
|---|---|
| Frontend | http://localhost:3000 |
| Reverse Proxy (punto de entrada API) | http://localhost:8000 |
| Backend (directo) | http://localhost:8080 |
| Payment Gateway (directo) | http://localhost:5001 |

> El frontend se comunica con el proxy (`:8000`), que redirige cada petición al servicio correspondiente.

---

## 🔄 Flujo de Uso

```
1. Registrarse      → POST /api/auth/registro
2. Verificar email  → Ingresar código OTP de 6 dígitos
3. Iniciar sesión   → POST /api/auth/login
4. Ver saldos       → Dashboard muestra ARS y USD
5. Transferir       → Ingresar alias destino y monto
6. Autorizar        → Ingresar código OTP recibido por correo
7. Confirmar        → La transferencia se completa
```

---

## 🧪 Probar con curl

```bash
# Registrar usuario
curl -X POST http://localhost:8000/api/auth/registro \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"12345678","nombreCompleto":"Test User","dni":"12345678","fechaNacimiento":"1990-01-01"}'

# Login (guarda cookie)
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{"identificador":"test@test.com","password":"12345678"}'

# Ver estado de billetera
curl http://localhost:8000/api/wallet/estado -b cookies.txt

# Cotización dólar
curl http://localhost:8000/api/rates/usd
```

---

## 📄 Documentación de Endpoints

Ver `DOCUMENTACION.md` para la documentación detallada de cada ruta con ejemplos de request/response.
