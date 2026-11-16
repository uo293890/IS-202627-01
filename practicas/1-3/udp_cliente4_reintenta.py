import socket, sys

ip = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
puerto = int(sys.argv[2]) if len(sys.argv) > 2 else 9999
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
secuencia = 1

while True:
    mensaje = input("Mensaje (FIN para salir): ")
    if mensaje == "FIN": break
    
    mensaje_completo = f"{secuencia}: {mensaje}"
    timeout = 0.1 # Tiempo inicial
    confirmado = False
    
    while not confirmado:
        print(f"Enviando... (Timeout: {timeout}s)")
        s.sendto(mensaje_completo.encode('utf-8'), (ip, puerto))
        s.settimeout(timeout)
        
        try:
            respuesta, _ = s.recvfrom(1024)
            if respuesta.decode('utf-8') == "OK":
                print("Recibida confirmación.")
                confirmado = True
                secuencia += 1
        except socket.timeout:
            timeout *= 2 # Doblamos el timeout
            if timeout > 2.0:
                print("Puede que el servidor esté caído. Inténtelo más tarde.")
                sys.exit(1) # Salimos del programa