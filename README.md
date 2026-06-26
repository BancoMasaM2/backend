# Banco MASA — Broker Simulador

Plataforma financiera digital que simula operaciones bancarias básicas: cuentas en ARS y USD, transferencias entre usuarios, compra de dólar blue y pagos en línea. Arquitectura orientada a microservicios con un API Gateway como único punto de entrada.

---

## Índice

- [Arquitectura general](#arquitectura-general)
- [Tecnologías utilizadas](#tecnologías-utilizadas)
- [Backend](#backend)
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
     ┌────────────────┐            ┌──────────────────┐
     │    Backend     │            │ Payment Gateway  │
     │  FastAPI :8000 │◀──────────▶│  FastAPI :8001   │
     │  (SQLite +     │   HTTP     │  (cotizaciones,  │
     │   operaciones) │            │   conversiones)  │
     └────────────────┘            └──────────────────┘
```

Cada servicio es una aplicación **FastAPI** independiente. El **API Gateway** actúa como reverse proxy y único punto de contacto para el frontend, enrutando las peticiones según el prefijo de la ruta.

---

## Tecnologías utilizadas

### Backend / Proxy / Payment Gateway

| Tecnología | Versión | Propósito |
|---|---|---|
| **Python** | 3.12+ | Lenguaje base de los tres servicios backend |
| **FastAPI** | 0.115.0 | Framework web ASGI para construir APIs REST con tipado estático, documentación automática (OpenAPI/Swagger) y soporte nativo de asincronía |
| **Uvicorn** | 0.30.6 | Servidor ASGI de alto rendimiento basado en `uvloop` y `httptools`. Ejecuta las aplicaciones FastAPI |
| **SQLAlchemy** | 2.0.35 | ORM (Object-Relational Mapper) para interactuar con SQLite mediante modelos Python. Soporta `asyncio` y `sessionmaker` para manejo de sesiones |
| **Pydantic** | 2.9.2 | Validación de datos por medio de modelos con type hints. FastAPI lo usa internamente para parsear requests y responses |
| **httpx** | 0.27.2 | Cliente HTTP asíncrono para comunicación entre microservicios. Reemplaza a `requests` con soporte nativo de `async/await` |
| **SQLite** | — | Motor de base de datos embebido, sin servidor. Almacena el archivo `backend/database.db` |
| **python-dotenv** | 1.0.1 | Carga variables de entorno desde archivos `.env` |
| **Alembic** | 1.13.2 | Migraciones de base de datos (presente en dependencias, aunque el proyecto usa migraciones manuales con `ALTER TABLE`) |

### Frontend

| Tecnología | Versión | Propósito |
|---|---|---|
| **React** | 18.2.0 | Librería para construir interfaces de usuario basadas en componentes reactivos |
| **Vite** | 7.0.0 | Bundler y dev server ultrarrápido. Usa esbuild para transformación y Rollup para empaquetado en producción |
| **React Router DOM** | 6.20.0 | Enrutamiento declarativo del lado del cliente. Maneja las transiciones entre vistas sin recargar la página |
| **JavaScript (ES Modules)** | — | Lenguaje del frontend. Los módulos se importan estáticamente con `import/export` |
| **CSS-in-JS (inline styles)** | — | Estrategia de estilos. Cada componente define su objeto `styles` con las reglas CSS en notación camelCase |

### Comunicación entre servicios

- **Frontend → Gateway**: `fetch()` desde el navegador hacia `http://<gateway>:7000`
- **Gateway → Backend**: `httpx.AsyncClient` (peticiones HTTP asíncronas)
- **Gateway → Payment Gateway**: `httpx.AsyncClient`
- **Payment Gateway → Gateway → Backend**: La pasarela envía las operaciones de escritura (conversiones, transferencias, pagos) al Gateway (`GATEWAY_URL`), que las reenvía al Backend para que persista en la base de datos

---

## Backend

### Ubicación: `backend/`

Servicio principal que concentra la lógica de negocio y el acceso a la base de datos.

### Modelos de datos (`backend/models/`)

Cuatro tablas definidas mediante SQLAlchemy ORM:

**Usuario** (`usuario.py`)
- `id`, `nombre`, `email` (único), `password` (texto plano en esta simulación), `fecha_creacion`
- `verificado`, `codigo_verificacion`, `codigo_expiracion` — flujo de verificación por email
- `alias` — identificador único amigable para transferencias
- `transfer_codigo`, `transfer_codigo_expiracion`, `transfer_destino_alias`, `transfer_moneda`, `transfer_monto` — estado de una transferencia en curso (two-step confirmation)

**Cuenta** (`cuenta.py`)
- `id`, `usuario_id` (FK), `moneda` (ARS/USD), `saldo`
- Restricción `UNIQUE(usuario_id, moneda)` — un usuario tiene exactamente una cuenta por moneda

**Transferencia** (`transferencia.py`)
- `id`, `origen_id` (FK → cuentas), `destino_id` (FK → cuentas), `monto`, `moneda`, `fecha`, `estado`
- Almacena tanto transferencias entre usuarios como conversiones de moneda (en cuyo caso `moneda` es `"ARS->USD"` y ambas cuentas pertenecen al mismo usuario)

**Pago** (`pago.py`)
- `id`, `usuario_id` (FK), `monto`, `descripcion`, `fecha`, `estado`

### Rutas de la API (`backend/routes/`)

Cada router se monta con un prefijo y se registra en `main.py` mediante `app.include_router()`.

| Router | Prefijo | Endpoints |
|---|---|---|
| `auth.py` | `/api/auth` | `POST /registro`, `POST /verificar-codigo`, `POST /reenviar-codigo`, `POST /login` |
| `usuarios.py` | `/api/usuarios` | `GET /{id}`, `GET /alias/{alias}`, `PUT /{id}/alias`, `GET /{id}/movimientos` |
| `cuentas.py` | `/api/cuentas` | `GET /{usuario_id}`, `GET /{usuario_id}/{moneda}` |
| `operaciones.py` | `/api/operaciones` | `POST /transferir`, `POST /iniciar-transferencia`, `POST /confirmar-transferencia`, `POST /conversion`, `POST /pago` |

### Servicios (`backend/services/`)

Capa intermedia entre rutas y base de datos. Contiene la lógica de negocio:

- **`auth_service.py`**: registro con verificación por email, login con validación de credenciales, generación y verificación de códigos OTP (one-time password) de 6 dígitos
- **`cuenta_service.py`**: consultas de cuentas por usuario y moneda
- **`usuario_service.py`**: perfil de usuario, actualización de alias, y `obtener_movimientos()` que construye el historial consolidado (mezcla transferencias, conversiones y pagos ordenados por fecha descendente)
- **`transferencia_service.py`**: flujo de dos pasos para transferencias seguras: `iniciar_transferencia()` envía un código por email, `confirmar_transferencia()` valida el código y ejecuta el movimiento

### Base de datos (`backend/database/`)

- `connection.py`: configura SQLAlchemy con `sqlite:///backend/database.db`. Usa `check_same_thread=False` porque FastAPI puede atender múltiples requests en distintos threads
- `schema.sql`: DDL de las cuatro tablas. Las migraciones adicionales se ejecutan en `main.py` mediante `ALTER TABLE` con manejo silencioso de errores (para columnas ya existentes)

### Utilidades (`backend/utils/`)

- `email_sender.py`: envía emails mediante SMTP (configurado para Gmail). Si no hay credenciales SMTP configuradas, la función retorna silenciosamente sin enviar (modo desarrollo)

---

## API Gateway (Proxy)

### Ubicación: `proxy/`

Actúa como **reverse proxy** y **punto único de entrada** para el frontend. Ningún otro servicio es accesible directamente desde el navegador.

### Funcionamiento interno

```python
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
PAYMENT_GATEWAY_URL = os.getenv("PAYMENT_GATEWAY_URL", "http://localhost:8001")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
```

El gateway define dos rutas comodín (capturan todo el subpath):

1. **`/api/{path:path}`** — Reenvía la petición al Backend precediendo `BACKEND_URL`
   - Ejemplo: `GET /api/cuentas/5` → `GET http://localhost:8000/api/cuentas/5`
2. **`/payments/{path:path}`** — Reenvía la petición a la Payment Gateway
   - Ejemplo: `POST /payments/conversiones` → `POST http://localhost:8001/payments/conversiones`

### Función `_forward()`

Es el núcleo del proxy. Realiza una copia exacta de la petición original:

```python
async def _forward(target_url, request):
    body = await request.body()
    headers = dict(request.headers)
    headers.pop("host", None)  # evita conflictos de host

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.request(
            method=request.method,
            url=target_url,
            content=body,
            headers=headers,
            params=request.query_params,
        )
        return Response(content=resp.content, status_code=resp.status_code, headers=dict(resp.headers))
```

**Características:**
- **Reenvío transparente**: el método HTTP, headers, body y query params se transfieren idénticos
- **Timeout de 30 segundos** por petición para evitar conexiones colgadas
- **Manejo de errores**: si el servicio destino no responde, retorna `502 Bad Gateway` con el detalle del error
- **CORS configurable**: se setea mediante la variable `CORS_ORIGINS` (separado por comas). Por defecto permite solo `http://localhost:5173`

### ¿Por qué es necesaria esta capa?

1. **Separación de responsabilidades**: el frontend solo conoce una URL (el gateway), no la topología interna
2. **Seguridad**: los servicios internos (Backend, Payment Gateway) no exponen puertos al exterior
3. **Flexibilidad**: se pueden agregar, quitar o reubicar servicios sin modificar el frontend
4. **CORS centralizado**: se configura en un solo lugar en lugar de en cada microservicio

---

## Payment Gateway (Pasarela de Pagos)

### Ubicación: `payment_gateway/`

Microservicio especializado en operaciones financieras que requieren lógica adicional (cotizaciones, cálculos de conversión). No tiene acceso directo a la base de datos; todas las operaciones de escritura las delega al Backend a través del API Gateway.

### Rutas (`payment_gateway/routes/`)

| Router | Prefijo | Endpoints |
|---|---|---|
| `transferencias.py` | `/payments` | `POST /transferencias` |
| `conversiones.py` | `/payments` | `POST /conversiones`, `GET /cotizacion` |
| `pagos.py` | `/payments` | `POST /pagos` |

### Servicios (`payment_gateway/services/`)

- **`transferencia_service.py`**: recibe los datos de la transferencia y los reenvía al Backend (`{GATEWAY_URL}/api/operaciones/transferir`) para que persista el movimiento
- **`conversion_service.py`**: obtiene la cotización actual del dólar blue mediante `cotizacion_api.py`, calcula el monto destino según la tasa correspondiente, y envía la operación al Backend (`{GATEWAY_URL}/api/operaciones/conversion`)
- **`pago_service.py`**: reenvía el pago al Backend (`{GATEWAY_URL}/api/operaciones/pago`)

### Providers (`payment_gateway/providers/`)

- **`cotizacion_api.py`**: consume la API externa [DolarAPI](https://dolarapi.com) para obtener cotizaciones en tiempo real. Incluye un **fallback** con valores por defecto si la API externa no responde. Los tipos de cotización disponibles son `"oficial"` y `"blue"`

### Flujo de una conversión ARS → USD

1. El frontend envía `POST /payments/conversiones` al Gateway
2. El Gateway reenvía a la Payment Gateway: `POST /payments/conversiones`
3. `conversion_service.py` obtiene la cotización blue de DolarAPI (o fallback)
4. Calcula: `monto_destino = monto_origen / tasa_venta`
5. Envía al Gateway: `POST {GATEWAY_URL}/api/operaciones/conversion`
6. El Gateway reenvía al Backend: `POST /api/operaciones/conversion`
7. El Backend debita la cuenta ARS, acredita la cuenta USD y registra una Transferencia con `moneda = "ARS->USD"`

---

## Frontend

### Ubicación: `frontend/`

Aplicación web SPA (Single Page Application) construida con React y Vite.

### Estructura

```
frontend/
├── index.html              # Punto de entrada HTML
├── vite.config.js          # Configuración de Vite (host, puerto)
├── package.json            # Dependencias y scripts
├── public/                 # Archivos estáticos
└── src/
    ├── main.jsx            # Punto de entrada React, monta BrowserRouter
    ├── App.jsx             # Componente raíz, define rutas y layout
    ├── services/
    │   └── api.js          # Cliente HTTP, wrapper de fetch()
    ├── pages/
    │   ├── Home.jsx        # Portal público del banco
    │   ├── Login.jsx       # Inicio de sesión
    │   ├── Registro.jsx    # Registro con verificación por email
    │   ├── Dashboard.jsx   # Panel principal con saldos y cotización
    │   ├── ComprarDolares.jsx  # Compra de USD con ARS
    │   ├── Transferencias.jsx  # Transferencias entre usuarios (2 pasos)
    │   ├── Pagos.jsx       # Pagos desde cuenta ARS
    │   └── Historial.jsx   # Tabla de movimientos consolidados
    └── components/
        ├── Navbar.jsx      # Barra de navegación del broker
        ├── SaldoCard.jsx   # Card visual de saldo por moneda
        └── FormTransferencia.jsx  # Formulario de transferencia
```

### Enrutamiento

El enrutamiento se maneja con `react-router-dom` v6. Las rutas protegidas verifican la existencia de `usuario_id` en `localStorage`:

| Ruta | Componente | Acceso |
|---|---|---|
| `/` | Home | Público |
| `/login` | Login | Público |
| `/registro` | Registro | Público |
| `/dashboard` | Dashboard | Autenticado |
| `/transferencias` | Transferencias | Autenticado |
| `/comprar-dolares` | ComprarDolares | Autenticado |
| `/pagos` | Pagos | Autenticado |
| `/historial` | Historial | Autenticado |
| `*` | Redirección a `/` | — |

### Cliente HTTP (`services/api.js`)

Función `request()` genérica que:
1. Construye la URL completa anteponiendo `GATEWAY_URL` (configurable vía `VITE_GATEWAY_URL`, defecto `http://localhost:7000`)
2. Serializa el body a JSON
3. Agrega headers `Content-Type: application/json`
4. Maneja errores HTTP lanzando excepciones con el mensaje del servidor

Cada operación del banco expone un método en el objeto `api`:
- `api.login()`, `api.registro()`, `api.verificarCodigo()`, `api.reenviarCodigo()`
- `api.getPerfil()`, `api.getCuentas()`, `api.getMovimientos()`
- `api.transferir()`, `api.iniciarTransferencia()`, `api.confirmarTransferencia()`
- `api.convertir()`, `api.getCotizacion()`
- `api.pagar()`

### Gestión de estado

No se utiliza un estado global (Redux, Zustand, Context). La sesión se persiste en `localStorage` con tres claves:
- `usuario_id` — identificador del usuario autenticado
- `nombre` — nombre para mostrar en el Navbar
- `alias` — alias del usuario para operaciones

---

## Ejecución del proyecto

### Prerrequisitos

| Software | Versión | Propósito |
|---|---|---|
| Python | 3.12+ | Entorno de ejecución de los servicios backend |
| Node.js | 20+ | Entorno de ejecución del frontend y npm |
| npm | (incluido) | Gestor de paquetes de Node.js |

### Instalación de dependencias

```bash
# Backend, Gateway y Payment Gateway comparten el mismo requirements.txt
pip install -r requirements.txt

# Frontend
cd frontend
npm install
cd ..
```

**`requirements.txt`** incluye FastAPI, Uvicorn, SQLAlchemy, httpx, Pydantic, python-dotenv y Alembic. Se instalan de forma global (o en un virtual environment). FastAPI requiere Uvicorn como servidor ASGI porque FastAPI en sí mismo no es un servidor, es un framework que produce un objeto `app` ASGI. Uvicorn es quien realmente escucha en el puerto y despacha las peticiones al objeto `app`.

**`npm install`** descarga React, React DOM, React Router DOM y Vite (con el plugin de React) desde el registro npm. Vite es el bundler que reemplaza a Webpack; ofrece recarga en caliente (HMR) en desarrollo y empaquetado optimizado con Rollup en producción.

### Comandos de ejecución

```bash
# Terminal 1 — Backend (puerto 8000)
uvicorn backend.main:app --port 8000 --reload

# Terminal 2 — Payment Gateway (puerto 8001)
uvicorn payment_gateway.main:app --port 8001 --reload

# Terminal 3 — API Gateway (puerto 7000)
uvicorn proxy.main:app --port 7000 --reload

# Terminal 4 — Frontend (puerto 5173)
cd frontend && npm run dev
```

#### Explicación de cada comando

**`uvicorn backend.main:app --port 8000 --reload`**

| Parte | Explicación |
|---|---|
| `uvicorn` | Servidor ASGI. A diferencia de WSGI (Gunicorn, uWSGI), ASGI soporta asincronía nativa. Uvicorn usa `uvloop` (implementación de event loop en C basada en libuv) para máximo rendimiento |
| `backend.main:app` | Importa el objeto `app` desde el módulo `backend.main.py`. La sintaxis es `ruta.al.archivo:nombre_del_objeto` |
| `--port 8000` | Puerto TCP donde el servidor escucha conexiones HTTP |
| `--reload` | Modo desarrollo: reinicia el servidor automáticamente cuando detecta cambios en archivos Python. Útil para desarrollo pero **debe omitirse en producción** por seguridad y rendimiento |

**`npm run dev`**

Ejecuta el script `dev` definido en `package.json`: `"dev": "vite"`. Vite inicia un servidor de desarrollo con las siguientes características:
- **Hot Module Replacement (HMR)**: los cambios en archivos JSX/CSS se reflejan al instante sin recargar la página
- **Servidor en `0.0.0.0:5173`**: configurado en `vite.config.js` con `host: '0.0.0.0'` para permitir acceso desde otros dispositivos en la red local
- **Proxy automático**: no necesita proxy porque la comunicación con el backend se hace mediante HTTP directo desde `fetch()` (CORS se maneja en el Gateway)

### Orden de arranque recomendado

1. **Backend** (debe estar listo antes que los demás porque Gateway y Payment Gateway intentarán conectar)
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
6. API Gateway reenvía al Backend
   httpx POST http://localhost:8000/api/operaciones/conversion
                ↓
7. Backend:
   a. Busca la cuenta ARS del usuario → verifica saldo ≥ 10000
   b. Busca (o crea) la cuenta USD del usuario
   c. Debita 10000 ARS, acredita 8.20 USD
   d. Inserta una Transferencia con moneda "ARS->USD"
   e. Commit a SQLite
                ↓
8. La respuesta viaja de vuelta por la misma cadena:
   Backend → Gateway → Payment Gateway → Gateway → Frontend
                ↓
9. Frontend muestra: "Compra exitosa. Recibiste $8.20 USD a una tasa de $1220 ARS/USD."
```

---

## Variables de entorno

### Proxy (`proxy/main.py`)

| Variable | Default | Descripción |
|---|---|---|
| `BACKEND_URL` | `http://localhost:8000` | URL del servicio Backend |
| `PAYMENT_GATEWAY_URL` | `http://localhost:8001` | URL del Payment Gateway |
| `CORS_ORIGINS` | `http://localhost:5173` | Orígenes CORS permitidos (separados por coma) |

### Payment Gateway (`payment_gateway/services/*.py`)

| Variable | Default | Descripción |
|---|---|---|
| `GATEWAY_URL` | `http://localhost:7000` | URL del API Gateway (por donde la pasarela envía operaciones al Backend) |

### Backend (`backend/database/connection.py`, `backend/.env`)

| Variable | Default | Descripción |
|---|---|---|
| `DATABASE_PATH` | `backend/database.db` | Ruta del archivo SQLite |
| `SMTP_HOST` | `smtp.gmail.com` | Servidor SMTP para envío de emails |
| `SMTP_PORT` | `587` | Puerto SMTP |
| `SMTP_USER` | — | Usuario SMTP |
| `SMTP_PASSWORD` | — | Contraseña SMTP |
| `SMTP_FROM` | (mismo que SMTP_USER) | Dirección remitente |

### Frontend (variables Vite)

| Variable | Default | Descripción |
|---|---|---|
| `VITE_GATEWAY_URL` | `http://localhost:7000` | URL del API Gateway para todas las peticiones HTTP |

---

## Ejecución distribuida en múltiples PCs

Cada servicio puede ejecutarse en una máquina diferente gracias a la configuración por variables de entorno.

### Esquema de red típico

| Servicio | PC | Puerto |
|---|---|---|
| Backend | PC1 (192.168.1.10) | 8000 |
| Payment Gateway | PC2 (192.168.1.20) | 8001 |
| API Gateway | PC3 (192.168.1.30) | 7000 |
| Frontend | PC4 (192.168.1.40) | 5173 |

### Comandos distribuidos

**PC1 — Backend**
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

**PC2 — Payment Gateway**
```bash
set GATEWAY_URL=http://192.168.1.30:7000
uvicorn payment_gateway.main:app --host 0.0.0.0 --port 8001 --reload
```

**PC3 — API Gateway**
```bash
set BACKEND_URL=http://192.168.1.10:8000
set PAYMENT_GATEWAY_URL=http://192.168.1.20:8001
set CORS_ORIGINS=http://192.168.1.40:5173
uvicorn proxy.main:app --host 0.0.0.0 --port 7000 --reload
```

**PC4 — Frontend**
```bash
cd frontend
set VITE_GATEWAY_URL=http://192.168.1.30:7000
npm run dev
```

### Comunicación entre servicios en la misma PC vs. diferentes PCs

- Si dos servicios están en **la misma PC**, la URL puede ser `localhost` (evita overhead de red)
- Si están en **PCs diferentes**, se usa la IP privada correspondiente
- El flag `--host 0.0.0.0` en Uvicorn es necesario para que el servidor acepte conexiones desde **cualquier interfaz de red**, no solo `localhost`. Sin este flag, Uvicorn por defecto escucha solo en `127.0.0.1`, lo que impediría conexiones desde otras máquinas

### Consideraciones

- **Firewall**: los puertos deben estar abiertos en cada PC (Windows Firewall o iptables)
- **Red local**: las IPs privadas (192.168.x.x) solo funcionan dentro de la misma red. Para acceso desde internet se necesitaría un reverse proxy público (Nginx, Caddy) con SSL
- **Base de datos**: SQLite no soporta acceso concurrente desde múltiples procesos. Si el Backend se escala horizontalmente, debe migrarse a PostgreSQL o MySQL
