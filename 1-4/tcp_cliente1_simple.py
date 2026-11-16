"""Ejercicio 1: cinco envíos con send y un envío FINAL."""
import socket
import sys

ip = sys.argv[1] if len(sys.argv) > 1 else "localhost"
puerto = int(sys.argv[2]) if len(sys.argv) > 2 else 9999
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((ip, puerto))
    for _ in range(5):
        enviados = s.send(b"ABCDE")
        print("send ABCDE:", enviados, "bytes")
    print("send FINAL:", s.send(b"FINAL"), "bytes")
