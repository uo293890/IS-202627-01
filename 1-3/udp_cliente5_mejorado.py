import socket, sys

ip = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
puerto = int(sys.argv[2]) if len(sys.argv) > 2 else 9999
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Conectamos para fijar el origen/destino y evitar paquetes de extraños
s.connect((ip, puerto)) 
secuencia = 1

while True:
    mensaje = input("Mensaje (FIN para salir): ")
    if mensaje == "FIN": break
    
    mensaje_completo = f"{secuencia}:{mensaje}"
    timeout = 0.1
    confirmado = False
    
    while not confirmado:
        # Al usar connect, usamos send y recv normales
        s.send(mensaje_completo.encode('utf-8'))
        s.settimeout(timeout)
        
        try:
            respuesta = s.recv(1024).decode('utf-8')
            if respuesta == f"OK:{secuencia}": # Comprobamos que confirma el paquete correcto
                print(f"Recibida confirmación del paquete {secuencia}.")
                confirmado = True
                secuencia += 1
        except socket.timeout:
            timeout *= 2
            if timeout > 2.0:
                print("Servidor no responde. Abortando.")
                sys.exit(1)