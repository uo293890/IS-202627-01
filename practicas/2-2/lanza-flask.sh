#!/usr/bin/env bash
set -eu
docker run --name amigos --rm -d --network pruebas \
  -e DEPLOYMENT_MODE=production \
  -e "DATABASE_URI=${APP_DATABASE_URI:-mysql+pymysql://amigosuser:amigospass@basedatos/amigosdb}" \
  "${AMIGOS_IMAGE:-amigos:2.0}"
