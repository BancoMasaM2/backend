import json
import http.server
import urllib.request
import urllib.error
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [PROXY] %(message)s")

BACKEND_HOST = "http://localhost:8080"
PAYMENT_HOST = "http://localhost:5001"
PROXY_PORT = 8000

BACKEND_ROUTES = ["/api/auth", "/api/wallet"]
PAYMENT_ROUTES = ["/api/rates", "/api/payments"]


def determine_target(path: str) -> str:
    for route in BACKEND_ROUTES:
        if path.startswith(route):
            return BACKEND_HOST
    for route in PAYMENT_ROUTES:
        if path.startswith(route):
            return PAYMENT_HOST
    return BACKEND_HOST


class ProxyHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self._handle_request("GET")

    def do_POST(self):
        self._handle_request("POST")

    def _handle_request(self, method: str):
        target_host = determine_target(self.path)
        url = f"{target_host}{self.path}"
        logging.info(f"{method} {self.path} -> {url}")

        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length > 0 else None

        headers = {}
        for key, value in self.headers.items():
            if key.lower() not in ("host", "transfer-encoding"):
                headers[key] = value

        req = urllib.request.Request(url, data=body, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                self.send_response(response.status)
                for key, value in response.headers.items():
                    if key.lower() not in (
                        "transfer-encoding",
                        "content-encoding",
                        "content-length",
                    ):
                        self.send_header(key, value)
                self.send_header("Content-Length", str(len(response.read())))
                self.end_headers()
                response.seek(0)
                self.wfile.write(response.read())
        except urllib.error.HTTPError as e:
            self.send_response(e.code)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(e.read())
        except urllib.error.URLError as e:
            self.send_response(502)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            error_body = json.dumps(
                {
                    "mensaje": f"Error conectando con el servicio: {str(e.reason)}",
                    "success": False,
                }
            )
            self.wfile.write(error_body.encode())

    def log_message(self, format, *args):
        logging.info(f"{args[0]} {args[1]} {args[2]}")


def main():
    server = http.server.HTTPServer(("0.0.0.0", PROXY_PORT), ProxyHandler)
    logging.info(f"Reverse Proxy corriendo en puerto {PROXY_PORT}")
    logging.info(f"Backend: {BACKEND_HOST}")
    logging.info(f"Payment Gateway: {PAYMENT_HOST}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()


if __name__ == "__main__":
    main()
