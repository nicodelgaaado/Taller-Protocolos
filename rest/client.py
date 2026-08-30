"""Cliente REST y medición didáctica del overhead HTTP."""

from __future__ import annotations

import argparse
import json
from typing import Any
from urllib import error, request
from urllib.parse import urlsplit


URL = "http://127.0.0.1:8000/productos"


def _tamano_encabezados(metodo: str, solicitud: request.Request, respuesta: Any) -> tuple[int, int]:
    ruta = urlsplit(solicitud.full_url).path
    peticion = f"{metodo} {ruta} HTTP/1.1\r\n"
    peticion += "".join(f"{k}: {v}\r\n" for k, v in solicitud.header_items()) + "\r\n"
    estado = f"HTTP/1.1 {respuesta.status} {respuesta.reason}\r\n"
    cabeceras = estado + "".join(f"{k}: {v}\r\n" for k, v in respuesta.headers.items()) + "\r\n"
    return len(peticion.encode()), len(cabeceras.encode())


def solicitar(metodo: str, producto: dict[str, Any] | None = None) -> Any:
    cuerpo = json.dumps(producto).encode() if producto is not None else None
    solicitud = request.Request(URL, data=cuerpo, method=metodo)
    solicitud.add_header("Accept", "application/json")
    if cuerpo is not None:
        solicitud.add_header("Content-Type", "application/json")
        solicitud.add_header("Content-Length", str(len(cuerpo)))

    try:
        with request.urlopen(solicitud) as respuesta:
            recibido = respuesta.read()
            overhead_req, overhead_res = _tamano_encabezados(metodo, solicitud, respuesta)
            print(f"HTTP {respuesta.status}")
            print(f"Cuerpo enviado: {len(cuerpo or b'')} bytes; encabezados petición: ~{overhead_req} bytes")
            print(f"Cuerpo recibido: {len(recibido)} bytes; encabezados respuesta: ~{overhead_res} bytes")
            return json.loads(recibido)
    except error.HTTPError as exc:
        detalle = json.loads(exc.read())
        raise RuntimeError(f"HTTP {exc.code}: {detalle}") from exc


def main() -> None:
    parser = argparse.ArgumentParser(description="Cliente del catálogo REST")
    subparsers = parser.add_subparsers(dest="operacion")
    subparsers.add_parser("listar")
    crear = subparsers.add_parser("crear")
    crear.add_argument("--nombre", required=True)
    crear.add_argument("--precio", required=True, type=float)
    args = parser.parse_args()

    if args.operacion == "crear":
        print(json.dumps(solicitar("POST", {"nombre": args.nombre, "precio": args.precio}), indent=2))
    elif args.operacion == "listar":
        print(json.dumps(solicitar("GET"), indent=2, ensure_ascii=False))
    else:
        print("Producto creado:", solicitar("POST", {"nombre": "Audífonos", "precio": 89000}))
        print("Catálogo:", solicitar("GET"))


if __name__ == "__main__":
    main()
