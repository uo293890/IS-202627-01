"""Ejercicio 6: longitud ASCII terminada en LF y cuerpo UTF-8."""
import socket
import sys


def recibe_mensaje(f):
    cabecera = f.readline()
    if not cabecera:
        return None
    if not cabecera.endswith(b"\n") or not cabecera[:-1].isdigit():
        raise ValueError("Cabecera de longitud no valida")
    longitud = int(cabecera)
    datos = f.read(longitud)
    if len(datos) != longitud:
        raise EOFError("Cuerpo incompleto")
    return datos.decode("utf8")


def envia_mensaje(s, mensaje):
    datos = mensaje.encode("utf8")
    s.sendall(str(len(datos)).encode("ascii") + b"\n" + datos)


puerto = int(sys.argv[1]) if len(sys.argv) > 1 else 9999
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as escucha:
    escucha.bind(("", puerto))
    escucha.listen(5)
    while True:
        sd, origen = escucha.accept()
        with sd, sd.makefile("rb") as f:
            try:
                while True:
                    mensaje = recibe_mensaje(f)
                    if mensaje is None:
                        break
                    print("Mensaje:", repr(mensaje), "bytes:", len(mensaje.encode("utf8")), flush=True)
                    envia_mensaje(sd, mensaje[::-1])
            except (EOFError, ValueError) as error:
                print("Mensaje rechazado:", error, flush=True)
