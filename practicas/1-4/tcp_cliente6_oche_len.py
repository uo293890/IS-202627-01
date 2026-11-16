"""Ejercicio 6: usa el mismo framing para peticiones y respuestas."""
import socket
import sys


def recibe_mensaje(f):
    cabecera = f.readline()
    if not cabecera or not cabecera.endswith(b"\n") or not cabecera[:-1].isdigit():
        raise EOFError("Cabecera de respuesta ausente o no valida")
    longitud = int(cabecera)
    datos = f.read(longitud)
    if len(datos) != longitud:
        raise EOFError("Respuesta incompleta")
    return datos.decode("utf8")


ip = sys.argv[1] if len(sys.argv) > 1 else "localhost"
puerto = int(sys.argv[2]) if len(sys.argv) > 2 else 9999
with socket.create_connection((ip, puerto), timeout=5) as s, s.makefile("rb") as f:
    mensajes = ["UNO", "DOS", "TRES", "mañana", "uno\r\ndos", ""]
    for mensaje in mensajes:
        datos = mensaje.encode("utf8")
        s.sendall(str(len(datos)).encode("ascii") + b"\n" + datos)
    for mensaje in mensajes:
        print("Enviado:", repr(mensaje), "Respuesta:", repr(recibe_mensaje(f)))
