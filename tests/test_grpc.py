import unittest
from concurrent import futures

try:
    import grpc
except ImportError:
    grpc = None


@unittest.skipIf(grpc is None, "grpcio no está instalado")
class GrpcTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from grpc_app import inventario_pb2_grpc
        from grpc_app.server import Inventario

        cls.servidor = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
        inventario_pb2_grpc.add_InventarioServicer_to_server(Inventario(), cls.servidor)
        puerto = cls.servidor.add_insecure_port("127.0.0.1:0")
        cls.servidor.start()
        cls.destino = f"127.0.0.1:{puerto}"

    @classmethod
    def tearDownClass(cls):
        cls.servidor.stop(grace=None).wait()

    def test_obtiene_producto(self):
        from grpc_app.client import obtener_producto

        producto = obtener_producto(1, self.destino)
        self.assertEqual(producto.nombre, "Teclado")

    def test_producto_inexistente(self):
        from grpc_app.client import obtener_producto

        with self.assertRaises(grpc.RpcError) as contexto:
            obtener_producto(999, self.destino)
        self.assertEqual(contexto.exception.code(), grpc.StatusCode.NOT_FOUND)
