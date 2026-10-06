import socket
import sys

puerto = int(sys.argv[1]) if len(sys.argv) > 1 else 9999
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(("", puerto))

print(f"Servidor escuchando en el puerto {puerto}...")
while True:
    datos, origen = s.recvfrom(1024)
    print(f"[{origen}] dice: {datos.decode('utf-8')}")