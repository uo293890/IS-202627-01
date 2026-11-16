"""Ejercicio 4: recibe cada respuesta hasta CRLF."""
import socket
import sys


def recibe_mensaje(s):
    buffer = []
    anterior = b""
    while True:
        dato = s.recv(1)
        if not dato:
            if buffer:
                raise EOFError("Respuesta incompleta")
            return None
        buffer.append(dato)
        if anterior == b"\r" and dato == b"\n":
            return b"".join(buffer)
        anterior = dato


ip = sys.argv[1] if len(sys.argv) > 1 else "localhost"
puerto = int(sys.argv[2]) if len(sys.argv) > 2 else 9999
with socket.create_connection((ip, puerto), timeout=5) as s:
    mensajes = ["UNO", "DOS", "TRES"]
    for mensaje in mensajes:
        s.sendall((mensaje + "\r\n").encode("utf8"))
    for _ in mensajes:
        respuesta = recibe_mensaje(s)
        if respuesta is None:
            raise EOFError("El servidor cerro antes de completar las respuestas")
        print("Respuesta recibida:", repr(respuesta.decode("utf8")))
