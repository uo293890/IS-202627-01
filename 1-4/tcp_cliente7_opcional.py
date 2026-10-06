import socket, sys, struct

def recvall(sock, n):
    datos = b""
    while len(datos) < n:
        paquete = sock.recv(n - len(datos))
        if not paquete: return None
        datos += paquete
    return datos

ip = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
puerto = int(sys.argv[2]) if len(sys.argv) > 2 else 9999

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((ip, puerto))

mensaje = input("Mensaje para el servidor OCHE: ")
bytes_mensaje = bytes(mensaje, "utf8")

# Empaquetamos la longitud en 2 bytes y concatenamos el mensaje
paquete = struct.pack(">H", len(bytes_mensaje)) + bytes_mensaje
s.sendall(paquete)

# Leemos la respuesta (primero 2 bytes de longitud, luego los datos)
bytes_longitud = recvall(s, 2)
longitud = struct.unpack(">H", bytes_longitud)[0]

datos_respuesta = recvall(s, longitud)
print(f"Respuesta del servidor: {datos_respuesta.decode('utf8')}")

s.close()