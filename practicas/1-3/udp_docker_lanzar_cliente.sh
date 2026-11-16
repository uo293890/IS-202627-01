#!/usr/bin/env bash
set -euo pipefail

carpeta=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
imagen=${IMAGEN_PYTHON:-python:3.7}
subred=$(docker network inspect pruebas --format '{{range .IPAM.Config}}{{println .Subnet}}{{end}}' | head -n 1)
broadcast=$(python3 -c 'import ipaddress, sys; print(ipaddress.ip_network(sys.argv[1]).broadcast_address)' "$subred")
echo "Subred: $subred; broadcast: $broadcast"

# -i permite redirigir entradas; -t solo se activa si hay una terminal real.
opciones=(-i)
if [[ -t 0 && -t 1 ]]; then opciones+=(-t); fi
docker run "${opciones[@]}" --rm --network pruebas \
    -v "$carpeta:/app:ro" "$imagen" \
    python -u /app/udp_cliente6_broadcast.py "$broadcast"
