# Broker Simulador - Instrucciones para Linux

## Requisitos

- Python 3.12+
- Node.js 18+

## 1. Clonar e instalar dependencias

```bash
git clone <repo> && cd la-prueba-de-la-prueba

# Backend
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt

# Frontend
cd frontend
npm install
cd ..
```

## 2. Configurar variables de entorno

```bash
cp backend/.env.example backend/.env
# Editar backend/.env con tus credenciales SMTP
```

## 3. Iniciar servicios (3 terminales)

### Terminal 1 - Backend (puerto 8000)

```bash
source venv/bin/activate
uvicorn backend.main:app --reload --port 8000
```

### Terminal 2 - Payment Gateway (puerto 8001)

```bash
source venv/bin/activate
uvicorn payment_gateway.main:app --reload --port 8001
```

### Terminal 3 - Proxy / API Gateway (puerto 7000)

```bash
source venv/bin/activate
uvicorn proxy.main:app --reload --port 7000
```

### Terminal 4 - Frontend (puerto 5173)

```bash
cd frontend
npm run dev
```

## 4. Abrir el navegador

```
http://localhost:5173
```

## Script de inicio rápido (opcional)

Guardar como `start.sh`:

```bash
#!/bin/bash
source venv/bin/activate
uvicorn backend.main:app --reload --port 8000 &
uvicorn payment_gateway.main:app --reload --port 8001 &
uvicorn proxy.main:app --reload --port 7000 &
cd frontend && npm run dev &
wait
```


