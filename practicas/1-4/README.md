# Práctica 1.4 Programación de red con Python y TCP

- [Memoria con explicaciones y capturas](memoria/memoria.md)
- [Memoria en PDF](memoria/memoria.pdf)
- [Registros de ejecución](memoria/evidencias)
- [Capturas originales](memoria/capturas)

Se conservan sin cambios los seis archivos existentes de los ejercicios 2, 5 y 7. Se añaden los ejercicios 1, 3, 4 y 6 y el cliente que envía tres líneas seguidas. `tcp_cliente.6_oche_len.py` es un alias del cliente 6 para admitir también el nombre escrito en el guion.

## Ejecutar un ejercicio

En una terminal, inicia el servidor; en otra, el cliente. Los servidores aceptan el puerto y los clientes aceptan dirección y puerto. Por defecto se utiliza el puerto 9999.

```bash
python3 tcp_servidor5_oche_readline.py 9999
python3 tcp_cliente5_oche_readline.py localhost 9999
```

Las versiones nuevas de los servidores 1, 3 y 4 permiten introducir el retardo del experimento mediante `RETARDO_LECTURA=1`, sin editar el archivo. El verificador puede añadir ese mismo retardo a la ejecución de los servidores originales sin modificar su contenido.

## Verificar todos los apartados

Requiere Python 3.8 o posterior en Linux, Docker, la imagen `python:3.7`, la red `pruebas`, los puertos 20101 a 20111 y 9090 libres y los nombres `is14_oche` e `is14_externa_verificacion` disponibles.

```bash
docker pull python:3.7
docker network inspect pruebas >/dev/null 2>&1 || docker network create pruebas
python3 verificar_practica.py
```

El verificador guarda trece registros y `resultados.json`. Comprueba también los fallos esperados de las versiones simplistas. Retira sus contenedores y la red temporal al terminar. Los registros se actualizan en cada ejecución.

```bash
python3 verificar_practica.py --capturas
```

Para incluir una comprobación externa nueva añade `--esperar-windows`. Cuando aparezca la espera correspondiente, ejecuta en Windows el cliente original:

```powershell
python tcp_cliente5_oche_readline.py IP_ACTUAL_DE_LA_VM 9090
```

Guarda la salida real y cópiala a la VM como `memoria/evidencias/11_cliente_windows.txt`. El verificador espera hasta cuatro minutos y comprueba las tres respuestas. Sin esa opción se verifica el puerto publicado desde Ubuntu y se indica que Windows se comprueba aparte. La memoria documenta la prueba externa real realizada el 16 de noviembre de 2026.

## Regenerar el PDF

La fuente editable es `memoria/memoria.md`. El generador utiliza `reportlab` y `Pillow` y las capturas originales:

```bash
python3 memoria/generar_pdf.py
```

Revisa visualmente el PDF después de modificarlo o regenerarlo.
