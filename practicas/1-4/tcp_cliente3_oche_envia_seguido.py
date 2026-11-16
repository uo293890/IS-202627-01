"""Experimento: tres envíos seguidos y después tres recv sin framing."""
import socket
import sys

ip = sys.argv[1] if len(sys.argv) > 1 else "localhost"
puerto = int(sys.argv[2]) if len(sys.argv) > 2 else 9999
with socket.create_connection((ip, puerto), timeout=3) as s:
    for mensaje in ("UNO", "DOS", "TRES"):
        s.sendall((mensaje + "\r\n").encode("utf8"))
    for numero in range(1, 4):
        try:
            print("recv", numero, ":", repr(s.recv(80)), flush=True)
        except socket.timeout:
            print("Timeout: contar llamadas a recv no delimita las respuestas.")
            sys.exit(1)
