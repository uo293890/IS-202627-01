import socket, sys

ip = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
puerto = int(sys.argv[2]) if len(sys.argv) > 2 else 9999

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((ip, puerto))

# Simulamos el envío rápido (Ejercicio 3)
mensajes = ["UNO", "DOS", "TRES"]
for m in mensajes:
    s.sendall(bytes(m + "\r\n", "utf8"))

# Tratamos la recepción como un archivo
f = s.makefile(mode="r", encoding="utf8", newline="\r\n")

for _ in mensajes:
    respuesta = f.readline()
    print(f"Respuesta recibida: {repr(respuesta)}") # repr muestra los \r\n ocultos

s.close()