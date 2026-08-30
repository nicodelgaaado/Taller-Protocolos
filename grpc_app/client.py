"""Cliente del servicio gRPC Inventario."""

import argparse

import grpc

try:
    from . import inventario_pb2, inventario_pb2_grpc
except ImportError:
    import inventario_pb2  # type: ignore[no-redef]
    import inventario_pb2_grpc  # type: ignore[no-redef]


def obtener_producto(producto_id: int, destino: str = "127.0.0.1:50051"):
    with grpc.insecure_channel(destino) as canal:
        cliente = inventario_pb2_grpc.InventarioStub(canal)
        return cliente.ObtenerProducto(
            inventario_pb2.SolicitudProducto(id=producto_id), timeout=5
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Consulta un producto mediante gRPC")
    parser.add_argument("id", type=int, nargs="?", default=1)
    args = parser.parse_args()
    try:
        producto = obtener_producto(args.id)
        print(f"Producto {producto.id}: {producto.nombre} (${producto.precio:.2f})")
    except grpc.RpcError as exc:
        print(f"Error gRPC {exc.code().name}: {exc.details()}")
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()

