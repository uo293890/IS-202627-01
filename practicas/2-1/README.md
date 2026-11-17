# Práctica 2.1: infraestructura web

[Memoria con capturas](memoria/memoria.md) · [PDF](memoria/memoria.pdf) · [Registros de ejecución](memoria/evidencias)

## Archivos

- `html/` y `html2/`: contenido de los sitios de los puertos 80 y 81.
- `sitios_nginx/` y `nginx.conf`: sitios, proxy `/hola` y configuración global.
- `lanzar_nginx.sh`: despliegue de Nginx; ejecutar desde esta carpeta.
- `hola_flask/hola_flask.py` y `Dockerfile`: saludo Flask con Gunicorn.
- `verificar_practica.py`: comprobaciones HTTP, procesos, SQL y persistencia.
- `memoria/`: documento, generador, capturas nuevas y resultados.

## Lanzamiento en la VM

Requiere Docker, las imágenes del laboratorio y los puertos 80 y 81 disponibles. Los nombres de contenedor siguientes también deben estar disponibles. Si ya están activos, se pueden revisar directamente con `docker ps`.

```bash
cd ~/repositorio_practicas/practicas/2-1
docker network inspect pruebas >/dev/null 2>&1 || docker network create pruebas
docker build -t gunicornflask:1.0 .
docker run -d --rm --name hola-flask --network pruebas gunicornflask:1.0
bash lanzar_nginx.sh
docker run -d --rm --name is21_mariadb_persistente --network pruebas \
  --network-alias mariadb -e MARIADB_ROOT_PASSWORD=claveroot \
  -v "$(pwd)/basedatos_verificacion:/var/lib/mysql" mariadb
```

El saludo se ve en `http://IP_VM/hola`, el sitio 1 en `http://IP_VM/` y el sitio 2 en `http://IP_VM:81/`. El puerto SQL permanece sin publicar. La clave mostrada es la del laboratorio del guion.

`basedatos_verificacion/` contiene datos locales persistentes y se excluye de Git. `.dockerignore` limita el contexto de construcción al módulo Flask y su Dockerfile, para no enviar al constructor bases de datos, memorias ni capturas.

## Verificación

La ejecución completa requiere además Flask y Gunicorn en `~/flaskenv`. El verificador no sustituye la instalación de dependencias. **Detener los contenedores de esta sesión antes de repetir sus experimentos**, conservando la carpeta de datos si se desea mantener su contenido. No detener servicios de otras prácticas.

```bash
python3 verificar_practica.py --capturas --mantener
```

Sin `--mantener`, el verificador limpia los contenedores creados en esa ejecución. `--apt` incluye los bloques 01 y 02, con instalación de Nginx y cambio temporal del índice antes del bloque 01, y restauración y retirada antes del 02. `--desde IDENTIFICADOR` permite continuar con los servicios previos ya preparados.

Cada ejecución escribe los registros y resultados de sus bloques en `memoria/evidencias/`. La opción `--capturas` pausa para fotografiar la consola real: no genera imágenes de terminal. Las capturas publicadas corresponden al 16 y 17 de noviembre de 2026.
