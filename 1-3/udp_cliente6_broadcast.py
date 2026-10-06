import socket

puerto = 12345
ip_broadcast = '<broadcast>' # Magia de Python para no tener que calcular la IP de red

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# El cliente también necesita activar el modo broadcast para poder enviar a la IP de broadcast
s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

print("Buscando servidores en la red local...")
s.sendto(b"BUSCANDO HOLA", (ip_broadcast, puerto))

servidores = []
# Damos 2 segundos para que los servidores respondan
s.settimeout(2.0) 

# Fase 1: Escuchar respuestas de todos los servidores posibles
try:
    while True:
        datos, origen = s.recvfrom(1024)
        if datos.decode('utf-8') == "IMPLEMENTO HOLA":
            ip_servidor = origen[0]
            if ip_servidor not in servidores:
                servidores.append(ip_servidor)
                print(f"-> Servidor encontrado en: {ip_servidor}")
except socket.timeout:
    pass # Es lo normal: el timeout salta cuando ya nadie más responde

# Fase 2: Consumir el servicio del primer servidor que respondió
if servidores:
    servidor_elegido = servidores[0]
    print(f"\nProbando servicio con el primer servidor ({servidor_elegido})...")
    
    s.sendto(b"HOLA", (servidor_elegido, puerto))
    
    s.settimeout(2.0)
    try:
        datos, origen = s.recvfrom(1024)
        print(f"Respuesta final: {datos.decode('utf-8')}")
    except socket.timeout:
        print("Error: El servidor no respondió al servicio HOLA.")
else:
    print("No se encontró ningún servidor en la red.")