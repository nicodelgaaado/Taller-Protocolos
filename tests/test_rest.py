import json
import threading
import unittest
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer

from rest.server import PRODUCTOS, PRODUCTOS_LOCK, ProductosHandler


class RestTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.servidor = ThreadingHTTPServer(("127.0.0.1", 0), ProductosHandler)
        cls.hilo = threading.Thread(target=cls.servidor.serve_forever, daemon=True)
        cls.hilo.start()
        cls.puerto = cls.servidor.server_port

    @classmethod
    def tearDownClass(cls):
        cls.servidor.shutdown()
        cls.servidor.server_close()
        cls.hilo.join()

    def setUp(self):
        with PRODUCTOS_LOCK:
            PRODUCTOS[:] = [{"id": 1, "nombre": "Teclado", "precio": 120000.0}]

    def peticion(self, metodo, ruta="/productos", cuerpo=None):
        conexion = HTTPConnection("127.0.0.1", self.puerto)
        datos = json.dumps(cuerpo) if cuerpo is not None else None
        conexion.request(metodo, ruta, body=datos, headers={"Content-Type": "application/json"})
        respuesta = conexion.getresponse()
        contenido = json.loads(respuesta.read())
        conexion.close()
        return respuesta.status, contenido

    def test_lista_productos(self):
        estado, contenido = self.peticion("GET")
        self.assertEqual(estado, 200)
        self.assertEqual(contenido[0]["nombre"], "Teclado")

    def test_crea_producto(self):
        estado, contenido = self.peticion("POST", cuerpo={"nombre": "Monitor", "precio": 900})
        self.assertEqual(estado, 201)
        self.assertEqual(contenido, {"id": 2, "nombre": "Monitor", "precio": 900.0})

    def test_rechaza_producto_invalido(self):
        estado, contenido = self.peticion("POST", cuerpo={"nombre": "", "precio": -1})
        self.assertEqual(estado, 400)
        self.assertIn("error", contenido)

    def test_recurso_inexistente(self):
        estado, _ = self.peticion("GET", "/otro")
        self.assertEqual(estado, 404)


if __name__ == "__main__":
    unittest.main()
