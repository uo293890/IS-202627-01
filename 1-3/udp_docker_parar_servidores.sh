#!/usr/bin/env bash
set -euo pipefail

# Solo elimina los tres contenedores de esta práctica; conserva la red.
for i in 1 2 3; do
    nombre="server_hola_$i"
    if docker container inspect "$nombre" >/dev/null 2>&1; then
        docker rm -f "$nombre"
    fi
done
