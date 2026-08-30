"""Servidor REST HTTP/1.1 sin dependencias externas."""

from __future__ import annotations

import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Lock
from typing import Any
from urllib.parse import urlsplit


PRODUCTOS: list[dict[str, Any]] = [
    {"id": 1, "nombre": "Teclado", "precio": 120000.0},
    {"id": 2, "nombre": "Mouse", "precio": 65000.0},
]
PRODUCTOS_LOCK = Lock()


class ProductosHandler(BaseHTTPRequestHandler):
    """Atiende las operaciones del recurso ``/productos``."""

    protocol_version = "HTTP/1.1"

    def _responder(self, estado: HTTPStatus, contenido: Any) -> None:
        cuerpo = json.dumps(contenido, ensure_ascii=False).encode("utf-8")
        self.send_response(estado)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(cuerpo)))
        self.end_headers()
        self.wfile.write(cuerpo)

    def _es_productos(self) -> bool:
        return urlsplit(self.path).path == "/productos"

    def do_GET(self) -> None:  # noqa: N802 (nombre exigido por BaseHTTPRequestHandler)
        if not self._es_productos():
            self._responder(HTTPStatus.NOT_FOUND, {"error": "Recurso no encontrado"})
            return
        with PRODUCTOS_LOCK:
            productos = [producto.copy() for producto in PRODUCTOS]
        self._responder(HTTPStatus.OK, productos)

    def do_POST(self) -> None:  # noqa: N802
        if not self._es_productos():
            self._responder(HTTPStatus.NOT_FOUND, {"error": "Recurso no encontrado"})
            return

        try:
            longitud = int(self.headers.get("Content-Length", "0"))
            datos = json.loads(self.rfile.read(longitud))
        except (ValueError, json.JSONDecodeError):
            self._responder(HTTPStatus.BAD_REQUEST, {"error": "JSON inválido"})
            return

        if (
            not isinstance(datos, dict)
            or not isinstance(datos.get("nombre"), str)
            or not datos["nombre"].strip()
            or isinstance(datos.get("precio"), bool)
            or not isinstance(datos.get("precio"), (int, float))
            or datos["precio"] < 0
        ):
            self._responder(
                HTTPStatus.BAD_REQUEST,
                {"error": "nombre no vacío y precio numérico no negativo son requeridos"},
            )
            return

        with PRODUCTOS_LOCK:
            producto = {
                "id": max((item["id"] for item in PRODUCTOS), default=0) + 1,
                "nombre": datos["nombre"].strip(),
                "precio": float(datos["precio"]),
            }
            PRODUCTOS.append(producto)
        self._responder(HTTPStatus.CREATED, producto)


def ejecutar(host: str = "127.0.0.1", puerto: int = 8000) -> None:
    servidor = ThreadingHTTPServer((host, puerto), ProductosHandler)
    print(f"Servidor REST disponible en http://{host}:{puerto}/productos")
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        servidor.server_close()


if __name__ == "__main__":
    ejecutar()

