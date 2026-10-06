import socket, sys, time

puerto = int(sys.argv[1]) if len(sys.argv) > 1 else 9999
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(("", puerto))
s.listen(5)

while True:
    sd, origen = s.accept()
    # time.sleep(1) # Descomenta para probar el Ejercicio 3 (colisión de mensajes)
    
    # Convertimos el socket a un "archivo" para usar readline
    f = sd.makefile(mode="r", encoding="utf8", newline="\r\n")
    
    while True:
        mensaje = f.readline() # Lee hasta encontrar \r\n de forma infalible
        if not mensaje: break # Cliente desconectado
        
        linea = mensaje[:-2] # Quitamos el \r\n final (2 caracteres)
        linea_invertida = linea[::-1] # Magia de Python para invertir string
        
        # Respondemos
        sd.sendall(bytes(linea_invertida + "\r\n", "utf8"))
    
    sd.close()