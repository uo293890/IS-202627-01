import socket, sys

def recvall(sock, n):
    # Función mágica para leer exactamente 'n' bytes sin importar si TCP los parte
    datos = b""
    while len(datos) < n:
        paquete = sock.recv(n - len(datos))
        if not paquete: return None # El cliente cerró la conexión
        datos += paquete
    return datos

puerto = int(sys.argv[1]) if len(sys.argv) > 1 else 9999
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(("", puerto))
s.listen(5)

while True:
    print("Esperando un cliente...")
    sd, origen = s.accept()
    print(f"Cliente conectado desde {origen}")
    
    while True:
        datos_bytes = recvall(sd, 5) # Esperamos exactamente 5 bytes
        if not datos_bytes: break
        
        datos = datos_bytes.decode("ascii")
        if datos == "FINAL":
            print("Recibido FINAL. Cerrando cliente.")
            break
        else:
            print(f"Recibido: {datos}")
    sd.close()