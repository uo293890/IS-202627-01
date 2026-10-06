import socket

puerto = 12345
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Activamos modo broadcast
s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
s.bind(("", puerto))

print(f"Servidor HOLA escuchando en puerto {puerto}...")

while True:
    datos, origen = s.recvfrom(1024)
    mensaje = datos.decode('utf-8')
    ip_cliente = origen[0] # origen es una tupla (IP, Puerto)
    
    if mensaje == "BUSCANDO HOLA":
        print(f"Petición de descubrimiento de {ip_cliente}")
        s.sendto(b"IMPLEMENTO HOLA", origen)
        
    elif mensaje == "HOLA":
        print(f"Petición de servicio de {ip_cliente}")
        respuesta = f"HOLA: {ip_cliente}"
        s.sendto(respuesta.encode('utf-8'), origen)