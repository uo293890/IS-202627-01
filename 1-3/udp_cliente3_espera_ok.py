import socket, sys

ip = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
puerto = int(sys.argv[2]) if len(sys.argv) > 2 else 9999
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
secuencia = 1

while True:
    mensaje = input("Mensaje (FIN para salir): ")
    if mensaje == "FIN": break
    
    mensaje_completo = f"{secuencia}: {mensaje}"
    s.sendto(mensaje_completo.encode('utf-8'), (ip, puerto))
    
    # Esperar el OK con timeout
    s.settimeout(0.1)
    try:
        respuesta, origen = s.recvfrom(1024)
        if respuesta.decode('utf-8') == "OK":
            print("Recibida confirmación.")
            secuencia += 1 # Solo avanzamos si llega el OK
    except socket.timeout:
        print("ERROR. El datagrama de confirmación no llega.")