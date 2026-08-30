"""Servidor del servicio gRPC Inventario."""

from concurrent import futures

import grpc

try:
    from . import inventario_pb2, inventario_pb2_grpc
except ImportError:
    import inventario_pb2  # type: ignore[no-redef]
    import inventario_pb2_grpc  # type: ignore[no-redef]


PRODUCTOS = {
    1: inventario_pb2.Producto(id=1, nombre="Teclado", precio=120000),
    2: inventario_pb2.Producto(id=2, nombre="Mouse", precio=65000),
}


class Inventario(inventario_pb2_grpc.InventarioServicer):
    def ObtenerProducto(self, request, context):  # noqa: N802
        producto = PRODUCTOS.get(request.id)
        if producto is None:
            context.abort(grpc.StatusCode.NOT_FOUND, f"No existe el producto {request.id}")
        return producto


def ejecutar(puerto: int = 50051) -> None:
    servidor = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    inventario_pb2_grpc.add_InventarioServicer_to_server(Inventario(), servidor)
    servidor.add_insecure_port(f"127.0.0.1:{puerto}")
    servidor.start()
    print(f"Servidor gRPC disponible en 127.0.0.1:{puerto}")
    servidor.wait_for_termination()


if __name__ == "__main__":
    ejecutar()

