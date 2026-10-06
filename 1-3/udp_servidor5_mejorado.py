import socket, sys, random

puerto = int(sys.argv[1]) if len(sys.argv) > 1 else 9999
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(("", puerto))
paquetes_procesados = set() # Evitar duplicados

while True:
    datos, origen = s.recvfrom(1024)
    if random.randint(0, 1) == 0:
        print("Simulando paquete perdido...")
        continue

    texto = datos.decode('utf-8')
    secuencia = texto.split(":")[0] # Extraemos el ID/Secuencia
    
    if secuencia not in paquetes_procesados:
        print(f"Procesando nuevo paquete de {origen}: {texto}")
        paquetes_procesados.add(secuencia)
    else:
        print(f"Ignorando duplicado de {origen}: {texto}")
        
    # Siempre respondemos el OK + Secuencia, incluso si es duplicado
    s.sendto(f"OK:{secuencia}".encode('utf-8'), origen)