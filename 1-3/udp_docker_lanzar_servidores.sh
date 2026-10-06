#!/bin/bash

# 1. Creamos la red (el || true evita que de error si ya existe)
docker network create pruebas 2>/dev/null || true

# 2. Lanzamos 3 contenedores en segundo plano (-d)
for i in {1..3}; do
    echo "Lanzando servidor $i..."
    docker run -d \
        --name server_hola_$i \
        --network pruebas \
        -v $(pwd):/app \
        python:3.7 python /app/udp_servidor6_broadcast.py
done

echo "¡Servidores en ejecución! Usa 'docker ps' para comprobarlo."