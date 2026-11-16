# Práctica 1.3 Programación de red con Python y UDP

Los ejercicios 1 a 7, incluido el opcional, están en esta carpeta. La memoria explica el funcionamiento y los resultados de la ejecución del 16 de noviembre de 2026.

- [Memoria con explicaciones y capturas](memoria/memoria.md)
- [Memoria en PDF](memoria/memoria.pdf)
- [Registros de las pruebas](memoria/evidencias)
- [Capturas originales de VirtualBox](memoria/capturas)

## Ejecución básica

```bash
python3 udp_servidor1.py
python3 udp_cliente1.py
```

Los clientes 1 a 5 aceptan dirección y puerto; los servidores 1 a 5 aceptan puerto. Los valores predeterminados son loopback y 9999. Escribe `FIN` para terminar el cliente.

## Broadcast con tres contenedores

```bash
bash udp_docker_lanzar_servidores.sh
bash udp_docker_lanzar_cliente.sh
bash udp_docker_parar_servidores.sh
```

Los scripts usan la imagen `python:3.7` y la red `pruebas`. El cliente calcula el broadcast de esa red. Se puede elegir otra imagen mediante la variable `IMAGEN_PYTHON`. Las imágenes 3.6 y 3.7 se conservan aquí para reproducir el guion histórico de la asignatura.

## Verificación completa

Requiere Python 3.8 o posterior en Linux, acceso a Docker, las imágenes `python:3.7` y `python:3.6`, la red `pruebas` y los puertos de la práctica libres. La comprobación adicional instala `iputils-ping` en un contenedor temporal y necesita acceso a los repositorios Debian. El verificador reserva los nombres `is13_verificacion_*` y comprueba que `server_hola_1`, `server_hola_2` y `server_hola_3` no existan antes de crearlos.

```bash
docker pull python:3.7
docker pull python:3.6
docker network inspect pruebas >/dev/null 2>&1 || docker network create pruebas
python3 verificar_practica.py
python3 verificar_docker_adicional.py
```

Para detenerse después de cada bloque y tomar capturas:

```bash
python3 verificar_practica.py --capturas
```

Los verificadores actualizan los registros de `memoria/evidencias`. Utilizan una semilla fija en los servidores con pérdidas para repetir el experimento; al ejecutar los programas directamente se mantiene el comportamiento aleatorio normal. La prueba entre Windows y Ubuntu se ejecutó desde Windows y su registro figura en `01_otra_maquina.txt`.

## Actualizar el PDF

La fuente editable de la memoria es `memoria/memoria.md`. El generador necesita los paquetes Python `reportlab` y `Pillow`. Después de editarla se puede reconstruir el PDF con:

```bash
python3 memoria/generar_pdf.py
```

El generador utiliza las capturas originales y limita en el PDF el área visible a la zona con texto, sin cambiar los PNG. Comprueba visualmente el documento después de regenerarlo.
