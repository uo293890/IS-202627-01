"""Ejercicio 3: intercala cada envío con una recepción simplista."""
import socket
import sys

ip = sys.argv[1] if len(sys.argv) > 1 else "localhost"
puerto = int(sys.argv[2]) if len(sys.argv) > 2 else 9999
with socket.create_connection((ip, puerto), timeout=3) as s:
    for mensaje in ("UNO", "DOS", "TRES"):
        s.sendall((mensaje + "\r\n").encode("utf8"))
        print("Enviado:", repr(mensaje), "Respuesta:", repr(s.recv(80)))
