import os
import logging
import httpx
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gateway")

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000") #Apunta al back
PAYMENT_GATEWAY_URL = os.getenv("PAYMENT_GATEWAY_URL", "http://localhost:8001") #Apunta a la pasarela
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",") #Apunta al front

app = FastAPI(title="API Gateway", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.api_route("/api/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_backend(path: str, request: Request):
    target_url = f"{BACKEND_URL}/api/{path}"
    return await _forward(target_url, request)


@app.api_route(
    "/payments/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"]
)
async def proxy_payments(path: str, request: Request):
    target_url = f"{PAYMENT_GATEWAY_URL}/payments/{path}"
    return await _forward(target_url, request)


async def _forward(target_url: str, request: Request) -> Response:
    body = await request.body()
    headers = dict(request.headers)
    headers.pop("host", None)

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.request(
                method=request.method,
                url=target_url,
                content=body,
                headers=headers,
                params=request.query_params,
            )
            logger.info("%s %s -> %s", request.method, target_url, resp.status_code)
            return Response(
                content=resp.content,
                status_code=resp.status_code,
                headers=dict(resp.headers),
            )
        except httpx.RequestError as e:
            logger.error("Error forwarding to %s: %s", target_url, e)
            return JSONResponse(
                status_code=502,
                content={
                    "detail": f"Error communicating with upstream service: {str(e)}"
                },
            )
