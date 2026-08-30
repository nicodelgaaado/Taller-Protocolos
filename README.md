# Taller de protocolos para sistemas distribuidos

Implementación en Python de dos estilos de comunicación cliente-servidor:

- **REST sobre HTTP/1.1** con mensajes JSON y operaciones `GET /productos` y
  `POST /productos`.
- **gRPC sobre HTTP/2** con Protocol Buffers y el procedimiento remoto
  `ObtenerProducto`.

## Requisitos

- Python 3.10 o superior.
- Las dependencias de `requirements.txt` (gRPC y sus herramientas).

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Parte 1: REST

Inicie el servidor (escucha en `127.0.0.1:8000`):

```bash
python rest/server.py
```

En otra terminal ejecute el cliente demostrativo:

```bash
python rest/client.py
```

También se pueden ejecutar operaciones individuales:

```bash
python rest/client.py listar
python rest/client.py crear --nombre "Monitor" --precio 950000
```

El cliente muestra por separado el tamaño del cuerpo JSON y el tamaño estimado
de la línea inicial más los encabezados HTTP. Esto permite observar que incluso
una petición pequeña tiene un coste fijo de metadatos. La medición es una
estimación a nivel de aplicación: no incluye paquetes TCP/IP, TLS ni posibles
encabezados añadidos por un proxy.

## Parte 2: gRPC

El contrato está en `proto/inventario.proto`. Los módulos Python generados se
incluyen en el repositorio para poder ejecutar el ejemplo directamente. Si se
modifica el contrato, regenérelos desde la raíz:

```bash
python -m grpc_tools.protoc -I proto --python_out=grpc_app \
  --grpc_python_out=grpc_app proto/inventario.proto
```

Inicie el servidor (escucha en `127.0.0.1:50051`) y luego el cliente:

```bash
python grpc_app/server.py
python grpc_app/client.py 1
```

Una consulta inexistente devuelve el estado gRPC `NOT_FOUND`:

```bash
python grpc_app/client.py 999
```

## Análisis: gRPC frente a REST

En microservicios con alto tráfico, gRPC suele ofrecer:

1. **Mensajes más compactos:** Protocol Buffers usa representación binaria y
   evita repetir nombres de campos como ocurre con JSON.
2. **Menor sobrecarga de transporte:** HTTP/2 comprime encabezados con HPACK y
   multiplexa varias llamadas en una sola conexión.
3. **Contrato tipado:** el archivo `.proto` permite validar la interfaz y
   generar clientes/servidores para varios lenguajes, reduciendo errores de
   integración.
4. **Streaming y control de flujo:** gRPC soporta streaming del cliente, del
   servidor y bidireccional de forma nativa.

REST sigue siendo preferible para APIs públicas y navegadores por su sencillez,
legibilidad, herramientas universales y facilidad para aprovechar cachés HTTP.
gRPC no elimina la latencia de red y su formato binario dificulta la inspección
manual; la elección debe responder al contexto y no solo al rendimiento.

## Pruebas

```bash
python -m unittest discover -s tests -v
```
