#!/usr/bin/env bash
set -eu
cd -- "$(dirname -- "$0")"
docker run --rm -d --network pruebas --name nginx \
  -v "$(pwd)/sitios_nginx:/etc/nginx/conf.d:ro" -p 80:80 nginx
