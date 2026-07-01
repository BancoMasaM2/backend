# Banco MASA — Broker Simulador

Plataforma financiera digital que simula operaciones bancarias básicas: cuentas en ARS y USD, transferencias entre usuarios, compra de dólar blue y pagos en línea. Arquitectura orientada a microservicios con un API Gateway como único punto de entrada.

---

## Índice

- [Arquitectura general](#arquitectura-general)
- [Tecnologías utilizadas](#tecnologías-utilizadas)
- [Backend (Django)](#backend-django)
- [API Gateway (Proxy)](#api-gateway-proxy)
- [Payment Gateway (Pasarela de Pagos)](#payment-gateway-pasarela-de-pagos)
- [Frontend](#frontend)
- [Ejecución del proyecto](#ejecución-del-proyecto)
- [Flujo de datos extremo a extremo](#flujo-de-datos-extremo-a-extremo)
- [Variables de entorno](#variables-de-entorno)
- [Ejecución distribuida en múltiples PCs](#ejecución-distribuida-en-múltiples-pcs)

---

## Arquitectura general

```
┌──────────────┐     ┌──────────────────┐
│   Frontend   │     │  API Gateway     │
│  React+Vite  │────▶│  FastAPI :7000   │
│   :5173      │     │  (proxy inverso) │
└──────────────┘     └────────┬─────────┘
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
     ┌──────────────────┐            ┌──────────────────┐
     │    Backend       │            │ Payment Gateway  │
     │  Django :8000    │◀──────────▶│  FastAPI :8001   │
     │  (SQLite + DRF)  │   HTTP     │  (cotizaciones,  │
     │   operaciones)   │            │   conversiones)  │
     └──────────────────┘            └──────────────────┘
```

El **API Gateway** actúa como reverse proxy y único punto de contacto para el frontend, enrutando las peticiones según el prefijo de la ruta. El backend está construido con **Django REST Framework**, mientras que el proxy y la pasarela de pagos son **FastAPI**.

---

## Tecnologías utilizadas

### Backend (Django)

| Tecnología | Versión | Propósito |
|---|---|---|
| **Python** | 3.12+ | Lenguaje base |
| **Django** | 5.1.1 | Framework web con ORM, migraciones y admin |
| **Django REST Framework** | 3.15.2 | Construcción de APIs REST con serializadores y views |
| **django-cors-headers** | 4.4.0 | Middleware CORS (deshabilitado en producción; lo maneja el proxy) |
| **httpx** | 0.27.2 | Cliente HTTP para obtener cotizaciones de dolarapi.com |
| **python-dotenv** | 1.0.1 | Carga variables de entorno desde `.env` |
| **SQLite** | — | Motor de base de datos embebido. Archivo: `backend_django/db.sqlite3` |

### Proxy y Payment Gateway

| Tecnología | Versión | Propósito |
|---|---|---|
| **FastAPI** | 0.115.0 | Framework web ASGI para APIs REST con documentación OpenAPI automática |
| **Uvicorn** | 0.30.6 | Servidor ASGI de alto rendimiento |
| **httpx** | 0.27.2 | Cliente HTTP asíncrono para comunicación entre microservicios |
| **Pydantic** | 2.9.2 | Validación de datos mediante modelos con type hints |

### Frontend

| Tecnología | Versión | Propósito |
|---|---|---|
| **React** | 18.2.0 | Librería para interfaces de usuario basadas en componentes |
| **Vite** | 7.0.0 | Bundler y dev server ultrarrápido |
| **React Router DOM** | 6.20.0 | Enrutamiento declarativo del lado del cliente |
| **JavaScript (ES Modules)** | — | Lenguaje del frontend |

### Comunicación entre servicios

- **Frontend → Gateway**: `fetch()` desde el navegador hacia `http://<gateway>:7000`
- **Gateway → Backend**: `httpx.AsyncClient` hacia Django en `:8000`
- **Gateway → Payment Gateway**: `httpx.AsyncClient` hacia FastAPI en `:8001`
- **Payment Gateway → Gateway → Backend**: La pasarela envía operaciones de escritura al Gateway (`GATEWAY_URL`), que las reenvía al Backend Django para persistir en la base de datos

---

## Backend (Django)

### Ubicación: `backend_django/`

Servicio principal que concentra la lógica de negocio, acceso a la base de datos y autenticación. Construido con Django REST Framework, se ejecuta con `manage.py runserver`.

### Estructura

```
backend_django/
├── manage.py
├── requirements.txt           # Django, DRF, corsheaders, httpx, python-dotenv
├── .env                       # SMTP y DJANGO_SECRET_KEY
├── db.sqlite3                 # Base de datos SQLite
├── config/
│   ├── settings.py            # Configuración de Django
│   ├── urls.py                # Raíz → incluye api.urls
│   └── wsgi.py                # Entrypoint WSGI
└── api/
    ├── models.py              # Usuario, Cuenta, Transferencia, Pago
    ├── serializers.py         # DRF serializers
    ├── views.py               # Endpoints (auth, usuarios, cuentas, operaciones, payments, health)
    ├── urls.py                # Enrutamiento de la API
    ├── services.py            # Lógica de negocio
    ├── utils.py               # SMTP email sender + exception handler
    └── migrations/
        └── 0001_initial.py    # Migración inicial
```

### Modelos de datos (`api/models.py`)

Cuatro tablas definidas como modelos de Django ORM:

**Usuario**
- `id`, `nombre`, `email` (único), `password` (texto plano — simulación educativa), `fecha_creacion`
- `verificado`, `codigo_verificacion`, `codigo_expiracion` — flujo de verificación por email
- `alias` — identificador único amigable para transferencias
- `transfer_codigo`, `transfer_codigo_expiracion`, `transfer_destino_alias`, `transfer_moneda`, `transfer_monto` — estado de una transferencia en curso (confirmación en 2 pasos)

**Cuenta**
- `id`, `usuario_id` (FK), `moneda` (ARS/USD), `saldo`
- Restricción `unique_together("usuario", "moneda")` — un usuario tiene una cuenta por moneda

**Transferencia**
- `id`, `origen_id` (FK → cuentas), `destino_id` (FK → cuentas), `monto`, `moneda`, `fecha`, `estado`
- Almacena transferencias entre usuarios y conversiones de moneda (moneda: `"ARS->USD"`, ambas cuentas del mismo usuario)

**Pago**
- `id`, `usuario_id` (FK), `monto`, `descripcion`, `fecha`, `estado`

### Rutas de la API (`api/urls.py`)

| Ruta | View | Método | Descripción |
|---|---|---|---|
| `/api/auth/registro` | `auth_registro` | POST | Registro con verificación por email |
| `/api/auth/verificar-codigo` | `auth_verificar_codigo` | POST | Verifica código OTP de 6 dígitos |
| `/api/auth/reenviar-codigo` | `auth_reenviar_codigo` | POST | Reenvía el código de verificación |
| `/api/auth/login` | `auth_login` | POST | Inicio de sesión |
| `/api/usuarios/{id}` | `usuario_detail` | GET | Perfil del usuario |
| `/api/usuarios/alias/{alias}` | `usuario_por_alias` | GET | Búsqueda por alias |
| `/api/usuarios/{id}/alias` | `usuario_alias_update` | PUT | Actualiza el alias |
| `/api/usuarios/{id}/movimientos` | `usuario_movimientos` | GET | Historial consolidado |
| `/api/cuentas/{usuario_id}` | `cuentas_usuario` | GET | Cuentas del usuario |
| `/api/cuentas/{usuario_id}/{moneda}` | `cuenta_usuario_moneda` | GET | Cuenta por moneda |
| `/api/operaciones/transferir` | `operaciones_transferir` | POST | Transferencia directa entre usuarios |
| `/api/operaciones/iniciar-transferencia` | `operaciones_iniciar_transferencia` | POST | Inicia transferencia en 2 pasos (envía código) |
| `/api/operaciones/confirmar-transferencia` | `operaciones_confirmar_transferencia` | POST | Confirma transferencia con código |
| `/api/operaciones/conversion` | `operaciones_conversion` | POST | Conversión ARS↔USD |
| `/api/operaciones/pago` | `operaciones_pago` | POST | Pago desde cuenta ARS |
| `/api/payments/cotizacion` | `payments_cotizacion` | GET | Cotización del dólar (endpoint directo) |
| `/api/payments/conversiones` | `payments_conversiones` | POST | Conversión con cotización (endpoint directo) |
| `/api/payments/pagos` | `payments_pagos` | POST | Pago (endpoint directo) |
| `/api/payments/transferencias` | `payments_transferencias` | POST | Transferencia (endpoint directo) |
| `/health/` | `health` | GET | Health check |

### Servicios (`api/services.py`)

Capa intermedia entre views y base de datos. Contiene la lógica de negocio:

- `registrar_usuario()`: crea usuario con cuentas ARS/USD, envía código de verificación por email
- `verificar_usuario()` / `reenviar_codigo()`: flujo de verificación OTP
- `login_usuario()`: validación de credenciales
- `obtener_usuario_por_id()` / `obtener_usuario_por_alias()` / `actualizar_alias()`: gestión de perfil
- `obtener_movimientos()`: historial consolidado (transferencias, conversiones y pagos ordenados por fecha)
- `iniciar_transferencia()` / `confirmar_transferencia()`: flujo de transferencia en 2 pasos con código por email

---

## API Gateway (Proxy)

### Ubicación: `proxy/`

### En el mateoboggio@etec-System-Product-Name:~/la-prueba-de-la-prueba$   ejecutar: 
source proxy/.venv/bin/activate
uvicorn proxy.main:app --host 0.0.0.0 --port 7000 --reload


Actúa como **reverse proxy** y **punto único de entrada** para el frontend. Ningún otro servicio es accesible directamente desde el navegador.

### Funcionamiento interno

```python
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
PAYMENT_GATEWAY_URL = os.getenv("PAYMENT_GATEWAY_URL", "http://localhost:8001")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
```

El gateway define dos rutas comodín:

1. **`/api/{path:path}`** — Reenvía la petición al Backend Django
   - Ejemplo: `GET /api/cuentas/5` → `GET http://localhost:8000/api/cuentas/5`
2. **`/payments/{path:path}`** — Reenvía la petición a la Payment Gateway
   - Ejemplo: `POST /payments/conversiones` → `POST http://localhost:8001/payments/conversiones`

### Función `_forward()`

Núcleo del proxy. Realiza una copia exacta de la petición original (método HTTP, headers, body y query params). Timeout de 30 segundos. Si el servicio destino no responde, retorna `502 Bad Gateway`.

### ¿Por qué es necesaria esta capa?

1. **Separación de responsabilidades**: el frontend solo conoce una URL (el gateway), no la topología interna
2. **Seguridad**: los servicios internos no exponen puertos al exterior
3. **Flexibilidad**: se pueden agregar o reubicar servicios sin modificar el frontend
4. **CORS centralizado**: se configura en un solo lugar

---

## Payment Gateway (Pasarela de Pagos)

### Ubicación: `payment_gateway/`

Microservicio FastAPI especializado en operaciones financieras (cotizaciones, conversiones). No tiene acceso directo a la base de datos; delega las operaciones de escritura al Backend Django a través del API Gateway.

### Rutas

| Ruta | Descripción |
|---|---|
| `POST /payments/transferencias` | Transferencia entre usuarios |
| `POST /payments/conversiones` | Conversión ARS↔USD con cotización en vivo |
| `GET /payments/cotizacion` | Cotización del dólar blue/oficial |
| `POST /payments/pagos` | Pago desde cuenta ARS |

### Servicios (`payment_gateway/services/`)

- **`conversion_service.py`**: obtiene cotización de DolarAPI, calcula monto destino, envía operación al Backend por `{GATEWAY_URL}/api/operaciones/conversion`
- **`pago_service.py`**: reenvía el pago a `{GATEWAY_URL}/api/operaciones/pago`
- **`transferencia_service.py`**: reenvía la transferencia a `{GATEWAY_URL}/api/operaciones/transferir`

### Providers (`payment_gateway/providers/`)

- **`cotizacion_api.py`**: consume [DolarAPI](https://dolarapi.com) para cotizaciones en tiempo real. Incluye fallback con valores por defecto si la API externa no responde

---

## Frontend

### Ubicación: `frontend/`

Aplicación web SPA (Single Page Application) construida con React y Vite.

### Estructura

```
frontend/
├── index.html
├── vite.config.js
├── package.json
├── public/
└── src/
    ├── main.jsx            # Punto de entrada, monta BrowserRouter
    ├── App.jsx             # Componente raíz, define rutas y layout
    ├── services/
    │   └── api.js          # Cliente HTTP hacia el Gateway
    ├── pages/
    │   ├── Home.jsx
    │   ├── Login.jsx
    │   ├── Registro.jsx
    │   ├── Dashboard.jsx
    │   ├── ComprarDolares.jsx
    │   ├── Transferencias.jsx
    │   ├── Pagos.jsx
    │   └── Historial.jsx
    └── components/
        ├── Navbar.jsx
        ├── SaldoCard.jsx
        └── FormTransferencia.jsx
```

### Cliente HTTP (`services/api.js`)

Función `request()` genérica que construye la URL anteponiendo `VITE_GATEWAY_URL` (default `http://localhost:7000`), serializa el body a JSON, y maneja errores HTTP. Cada operación expone un método en el objeto `api`.

### Gestión de estado

Sin estado global. La sesión se persiste en `localStorage` con tres claves: `usuario_id`, `nombre` y `alias`.

---

## Ejecución del proyecto

### Prerrequisitos

| Software | Versión |
|---|---|
| Python | 3.12+ |
| Node.js | 20+ |
| npm | (incluido) |

### Instalación de dependencias

```bash
# Backend Django
cd backend_django
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Proxy y Payment Gateway
cd ..
python -m venv venv && source venv/bin/activate
pip install -r proxy/requirements.txt   # o requirements.txt raíz

# Frontend
cd frontend
npm install
```

### Comandos de ejecución

```bash
# Terminal 1 — Backend Django (puerto 8000)
cd backend_django
source .venv/bin/activate
python manage.py runserver 0.0.0.0:8000

# Terminal 2 — Payment Gateway (puerto 8001)
source venv/bin/activate
uvicorn payment_gateway.main:app --port 8001 --reload

# Terminal 3 — API Gateway (puerto 7000)
source venv/bin/activate
BACKEND_URL=http://localhost:8000 uvicorn proxy.main:app --port 7000 --reload

# Terminal 4 — Frontend (puerto 5173)
cd frontend && npm run dev
```

### Orden de arranque recomendado

1. **Backend Django** (debe estar listo primero)
2. **Payment Gateway**
3. **API Gateway** (depende de Backend y Payment Gateway)
4. **Frontend** (depende del Gateway)

---

## Flujo de datos extremo a extremo

### Ejemplo: Compra de dólares

```
1. Usuario ingresa monto en ARS y presiona "Comprar"
   Frontend → fetch POST /payments/conversiones {usuario_id, monto: 10000, desde: "ARS", hacia: "USD"}
                ↓
2. API Gateway recibe en :7000, reenvía a Payment Gateway :8001
   httpx POST http://localhost:8001/payments/conversiones
                ↓
3. Payment Gateway obtiene cotización blue de dolarapi.com
   GET https://dolarapi.com/v1/dolares/blue
                ↓
   Si la API externa falla, usa valores de fallback (compra: 1200, venta: 1220)
                ↓
4. Calcula monto_destino = 10000 / 1220 = 8.20 USD
                ↓
5. Payment Gateway envía la operación al Gateway
   httpx POST http://localhost:7000/api/operaciones/conversion
   {usuario_id, monto_origen: 10000, moneda_origen: "ARS", monto_destino: 8.20, moneda_destino: "USD", tasa: 1220}
                ↓
6. API Gateway reenvía al Backend Django
   httpx POST http://localhost:8000/api/operaciones/conversion
                ↓
7. Backend Django:
   a. Busca la cuenta ARS del usuario → verifica saldo ≥ 10000
   b. Busca (o crea) la cuenta USD del usuario
   c. Debita 10000 ARS, acredita 8.20 USD
   d. Inserta una Transferencia con moneda "ARS->USD"
   e. Guarda en SQLite
                ↓
8. La respuesta viaja de vuelta por la misma cadena:
   Django → Gateway → Payment Gateway → Gateway → Frontend
                ↓
9. Frontend muestra: "Compra exitosa. Recibiste $8.20 USD a una tasa de $1220 ARS/USD."
```

---

## Variables de entorno

### Proxy (`proxy/main.py`)

| Variable | Default | Descripción |
|---|---|---|
| `BACKEND_URL` | `http://localhost:8000` | URL del Backend Django |
| `PAYMENT_GATEWAY_URL` | `http://localhost:8001` | URL del Payment Gateway |
| `CORS_ORIGINS` | `http://localhost:5173` | Orígenes CORS permitidos (separados por coma) |

### Payment Gateway (`payment_gateway/services/*.py`)

| Variable | Default | Descripción |
|---|---|---|
| `GATEWAY_URL` | `http://localhost:7000` | URL del API Gateway (por donde la pasarela envía operaciones al Backend) |

### Backend Django (`backend_django/config/settings.py`, `backend_django/.env`)

| Variable | Default | Descripción |
|---|---|---|
| `DJANGO_SECRET_KEY` | `django-insecure-...` | Secret key de Django |
| `DJANGO_DEBUG` | `True` | Modo debug |
| `CORS_ALLOWED_ORIGINS` | `http://localhost:5173,http://localhost:7000` | Orígenes CORS permitidos en Django |
| `SMTP_HOST` | `smtp.gmail.com` | Servidor SMTP |
| `SMTP_PORT` | `587` | Puerto SMTP |
| `SMTP_USER` | — | Usuario SMTP |
| `SMTP_PASSWORD` | — | Contraseña SMTP |
| `SMTP_FROM` | (mismo que SMTP_USER) | Dirección remitente |

### Frontend (variables Vite)

| Variable | Default | Descripción |
|---|---|---|
| `VITE_GATEWAY_URL` | `http://localhost:7000` | URL del API Gateway |

---

## Ejecución distribuida en múltiples PCs

Cada servicio puede ejecutarse en una máquina diferente mediante variables de entorno.

### Esquema de red

| Servicio | IP | Puerto |
|---|---|---|
| Backend Django | 192.168.220.127 | 8000 |
| Payment Gateway | 192.168.220.125 | 8001 |
| API Gateway | 192.168.220.113 | 7000 |
| Frontend | 192.168.220.123 | 5173 |

### Comandos de ejecución distribuida

**192.168.220.127 — Backend Django**
```bash
cd backend_django
python manage.py runserver 0.0.0.0:8000
```

**192.168.220.125 — Payment Gateway**
```bash
GATEWAY_URL=http://192.168.220.113:7000 uvicorn payment_gateway.main:app --host 0.0.0.0 --port 8001 --reload
```

**192.168.220.113 — API Gateway**
```bash
BACKEND_URL=http://192.168.220.127:8000 \
PAYMENT_GATEWAY_URL=http://192.168.220.125:8001 \
CORS_ORIGINS=http://192.168.220.123:5173 \
uvicorn proxy.main:app --host 0.0.0.0 --port 7000 --reload
```

**192.168.220.123 — Frontend**
```bash
cd frontend
VITE_GATEWAY_URL=http://192.168.220.113:7000 npm run dev
```

### Consideraciones

- **Firewall**: los puertos deben estar abiertos en cada PC
- **Red local**: las IPs privadas solo funcionan dentro de la misma red
- **Base de datos**: SQLite no soporta acceso concurrente desde múltiples procesos. Si el Backend se escala horizontalmente, debe migrarse a PostgreSQL o MySQL
