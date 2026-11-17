#!/usr/bin/env bash
set -eu
cd -- "$(dirname -- "$0")"
docker network inspect pruebas >/dev/null 2>&1 || docker network create pruebas
# Las credenciales por defecto son las del guion de laboratorio.
docker run --name basedatos --rm -d --network pruebas \
  -e MYSQL_ROOT_PASSWORD="${DB_ROOT_PASSWORD:-claveroot}" \
  -e MYSQL_USER=amigosuser -e MYSQL_DATABASE=amigosdb \
  -e MYSQL_PASSWORD="${DB_PASSWORD:-amigospass}" \
  -v "$(pwd)/${DB_DIR:-basedatos}:/var/lib/mysql" mariadb
