import socket, sys, random

puerto = int(sys.argv[1]) if len(sys.argv) > 1 else 9999
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(("", puerto))

while True:
    datos, origen = s.recvfrom(1024)
    if random.randint(0, 1) == 0:
        print("Simulando paquete perdido...")
    else:
        print(f"Recibido de {origen}: {datos.decode('utf-8')}")
        # Enviar confirmación
        s.sendto(b"OK", origen)