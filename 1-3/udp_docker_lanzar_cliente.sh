#!/bin/bash

echo "Lanzando el cliente..."

# Usamos -it para ver la salida interactiva en consola
# Usamos --rm para que el contenedor se autodestruya al terminar y no deje basura
docker run -it --rm \
    --name cliente_hola \
    --network pruebas \
    -v $(pwd):/app \
    python:3.7 python /app/udp_cliente6_broadcast.py