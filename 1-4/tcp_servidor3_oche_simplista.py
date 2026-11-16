"""Ejercicio 3: versión deliberadamente simplista del servicio OCHE."""
import os
import socket
import sys
import time

puerto = int(sys.argv[1]) if len(sys.argv) > 1 else 9999
retardo = float(os.environ.get("RETARDO_LECTURA", "0"))
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as escucha:
    escucha.bind(("", puerto))
    escucha.listen(5)
    while True:
        sd, origen = escucha.accept()
        with sd:
            time.sleep(retardo)
            while True:
                datos = sd.recv(80)
                if not datos:
                    break
                print("recv(80):", repr(datos), flush=True)
                # Se presupone una línea completa por recv: el experimento
                # del guion muestra por qué esta suposición no es válida.
                linea = datos.decode("utf8")[:-2]
                respuesta = (linea[::-1] + "\r\n").encode("utf8")
                sd.sendall(respuesta)
                print("Respuesta:", repr(respuesta), flush=True)
