#!/usr/bin/env bash
set -euo pipefail

carpeta=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
imagen=${IMAGEN_PYTHON:-python:3.7}

if ! docker network inspect pruebas >/dev/null 2>&1; then
    docker network create pruebas
fi

for i in 1 2 3; do
    nombre="server_hola_$i"
    if docker container inspect "$nombre" >/dev/null 2>&1; then
        docker start "$nombre" >/dev/null
    else
        docker run -d --name "$nombre" --network pruebas \
            -v "$carpeta:/app:ro" "$imagen" \
            python -u /app/udp_servidor6_broadcast.py >/dev/null
    fi
    echo "Servidor disponible: $nombre"
done
docker ps --filter 'name=server_hola_' --format '{{.Names}} | {{.Status}}'
