# Generated-style gRPC bindings for inventario.proto.
import grpc

try:
    from . import inventario_pb2 as inventario__pb2
except ImportError:
    import inventario_pb2 as inventario__pb2


class InventarioStub:
    def __init__(self, channel):
        self.ObtenerProducto = channel.unary_unary(
            "/inventario.Inventario/ObtenerProducto",
            request_serializer=inventario__pb2.SolicitudProducto.SerializeToString,
            response_deserializer=inventario__pb2.Producto.FromString,
        )


class InventarioServicer:
    def ObtenerProducto(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Método no implementado")
        raise NotImplementedError("ObtenerProducto")


def add_InventarioServicer_to_server(servicer, server):
    rpc_method_handlers = {
        "ObtenerProducto": grpc.unary_unary_rpc_method_handler(
            servicer.ObtenerProducto,
            request_deserializer=inventario__pb2.SolicitudProducto.FromString,
            response_serializer=inventario__pb2.Producto.SerializeToString,
        )
    }
    generic_handler = grpc.method_handlers_generic_handler(
        "inventario.Inventario", rpc_method_handlers
    )
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers(
        "inventario.Inventario", rpc_method_handlers
    )
