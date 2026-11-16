"""Ejercicio 4: delimita cada línea leyendo un byte de cada vez."""
import os
import socket
import sys
import time


def recibe_mensaje(s):
    buffer = []
    anterior = b""
    while True:
        dato = s.recv(1)
        if not dato:
            if buffer:
                raise EOFError("La conexion termino antes del delimitador CRLF")
            return None
        buffer.append(dato)
        if anterior == b"\r" and dato == b"\n":
            return b"".join(buffer)
        anterior = dato


puerto = int(sys.argv[1]) if len(sys.argv) > 1 else 9999
retardo = float(os.environ.get("RETARDO_LECTURA", "0"))
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as escucha:
    escucha.bind(("", puerto))
    escucha.listen(5)
    while True:
        sd, origen = escucha.accept()
        with sd:
            time.sleep(retardo)
            try:
                while True:
                    mensaje = recibe_mensaje(sd)
                    if mensaje is None:
                        break
                    linea = mensaje[:-2].decode("utf8")
                    print("Linea completa:", repr(linea), flush=True)
                    sd.sendall((linea[::-1] + "\r\n").encode("utf8"))
            except EOFError as error:
                print(error, flush=True)
