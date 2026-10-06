#!/bin/bash

# Nos aseguramos de que la red existe
docker network create pruebas 2>/dev/null || true

# Detenemos cualquier nginx anterior por si acaso
docker stop servidor_nginx 2>/dev/null || true

echo "Lanzando contenedor Nginx con dos sitios web..."

docker run -d --rm \
  --name servidor_nginx \
  --network pruebas \
  -p 80:80 \
  -p 81:81 \
  -v $(pwd)/html:/usr/share/nginx/html \
  -v $(pwd)/html2:/usr/share/nginx/html2 \
  -v $(pwd)/sitios_nginx:/etc/nginx/conf.d \
  -v $(pwd)/nginx.conf:/etc/nginx/nginx.conf \
  nginx

echo "¡Listo! Comprueba 'docker ps'."
echo "Abre tu navegador en http://IP_DE_TU_MAQUINA y en http://IP_DE_TU_MAQUINA:81"