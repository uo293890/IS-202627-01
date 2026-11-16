import socket, sys, struct

def recvall(sock, n):
    datos = b""
    while len(datos) < n:
        paquete = sock.recv(n - len(datos))
        if not paquete: return None
        datos += paquete
    return datos

puerto = int(sys.argv[1]) if len(sys.argv) > 1 else 9999
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(("", puerto))
s.listen(5)

while True:
    sd, _ = s.accept()
    
    while True:
        # 1. Leemos exactamente 2 bytes (la longitud)
        bytes_longitud = recvall(sd, 2)
        if not bytes_longitud: break
        
        # Desempaquetamos (>H significa Big Endian, Unsigned Short de 2 bytes)
        longitud_mensaje = struct.unpack(">H", bytes_longitud)[0]
        
        # 2. Leemos exactamente la longitud que nos han dicho
        datos_mensaje = recvall(sd, longitud_mensaje)
        texto = datos_mensaje.decode("utf8")
        
        # Damos la vuelta (OCHE)
        texto_invertido = texto[::-1]
        bytes_respuesta = bytes(texto_invertido, "utf8")
        
        # 3. Respondemos con el mismo formato: [2 bytes de longitud] + [datos]
        sd.sendall(struct.pack(">H", len(bytes_respuesta)) + bytes_respuesta)
        
    sd.close()