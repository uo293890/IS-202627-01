import socket
import sys

ip = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
puerto = int(sys.argv[2]) if len(sys.argv) > 2 else 9999
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while True:
    mensaje = input("Mensaje (escribe FIN para salir): ")
    if mensaje == "FIN":
        break
    s.sendto(mensaje.encode('utf-8'), (ip, puerto))