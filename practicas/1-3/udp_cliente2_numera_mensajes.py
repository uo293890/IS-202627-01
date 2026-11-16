import socket, sys

ip = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
puerto = int(sys.argv[2]) if len(sys.argv) > 2 else 9999
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
secuencia = 1

while True:
    mensaje = input("Mensaje (FIN para salir): ")
    if mensaje == "FIN": break
    
    # Añadimos el número de secuencia
    mensaje_completo = f"{secuencia}: {mensaje}"
    s.sendto(mensaje_completo.encode('utf-8'), (ip, puerto))
    secuencia += 1