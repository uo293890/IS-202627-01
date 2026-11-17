# Práctica 2.2: Amigos y HTTP

[Memoria](memoria/memoria.md) · [PDF](memoria/memoria.pdf) · [Evidencias](memoria/evidencias)

Aplicación Flask con vistas HTML y API REST, SQLAlchemy, migraciones y el ejercicio adicional `device`. El despliegue final usa Nginx, Gunicorn y MariaDB en la red `pruebas`.

## Arranque

Desde una VM con Docker y Flask/Flask-SQLAlchemy/PyMySQL/Flask-Migrate instalados en `~/flaskenv`:

```bash
cd ~/repositorio_practicas/practicas/2-2
# Los nombres basedatos, amigos y nginx deben estar disponibles.
# Se usa una carpeta independiente para no modificar bases anteriores.
DB_DIR=basedatos_verificacion bash lanza-basedatos.sh
```

Esperar a que MariaDB termine su inicialización. Para aplicar el esquema desde Ubuntu:

```bash
DB_IP=$(docker inspect basedatos --format '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}')
export DATABASE_URI="mysql+pymysql://amigosuser:amigospass@${DB_IP}/amigosdb"
cd amigos
~/flaskenv/bin/flask --app lanzar db upgrade
docker build -t amigos:2.0 .
cd ..
bash lanza-flask.sh
bash lanza-nginx.sh
```

Las credenciales predeterminadas son las del guion. La aplicación admite `DATABASE_URI` directamente, sin necesitar un archivo de secretos local. `amigos/.dockerignore` excluye `instance/` y datos locales de la imagen. La variable exportada en Ubuntu usa la IP del contenedor; el script de Gunicorn usa su nombre DNS `basedatos`.

La interfaz se abre en `http://IP_VM/html/amigos`, la API en `http://IP_VM/api/amigos` y los dispositivos en `http://IP_VM/api/devices`. Solo Nginx publica un puerto de la VM, el 80.

## Migraciones y datos

- `e753fcc1a838`: tabla `amigos` original.
- `a9d678823200`: columna nullable `device` de tipo TEXT.

Las migraciones se versionan. Las carpetas `basedatos/`, `basedatos_verificacion/` e `instance/` permanecen locales. El código conserva el nombre `amigos` para no crear por error otra tabla llamada `amigo`.

## Verificación y capturas

```bash
python3 verificar_practica.py --preparar --capturas
```

La ejecución anterior exige una **base de verificación recién inicializada y vacía**, montada en `basedatos_verificacion`, además de los nombres de contenedor y puertos libres. No se debe ejecutar `--preparar` contra los datos finales existentes: el verificador comprueba el montaje y rechaza una base que ya contenga tablas. El downgrade opcional se realiza antes de insertar datos.

`--desde BLOQUE` permite retomar cuando se han preparado sus requisitos. Los bloques 05 a 09 necesitan el servidor de desarrollo activo; el bloque 10 construye la imagen y los contenedores finales. Las pruebas dejan datos de ejemplo y vacían todos los dispositivos al acabar. Para pruebas nuevas que deban partir de cero, usar una VM/copia de laboratorio con un directorio de verificación nuevo, conservando aparte cualquier dato anterior.

`memoria/evidencias/resultados.json` registra 13 bloques correctos. Se añade una comparación de la versión 1.0 reconstruida desde el commit anterior, documentada en `09_version1.txt`. Las capturas de la memoria son nuevas; no se reutiliza el archivo histórico de GitHub.
