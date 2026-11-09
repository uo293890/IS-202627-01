import ftplib
import getpass

# Lista donde guardaremos las lineas recibidas
lista = []

def acumular(linea):
    lista.append(linea)

# Solicitar contraseña
clave = getpass.getpass("Clave del usuario uo302956: ")

# Conectar al servidor FTP
f = ftplib.FTP("localhost")

try:
    # Autenticarse
    f.login("uo302956", clave)
    print("Conectado al servidor FTP")

    # Entrar en la carpeta de prueba
    f.cwd("prueba-ftp")

    # Obtener el listado mediante LIST
    lista = []
    respuesta = f.retrlines("LIST", acumular)

    # Mostrar resultados
    print("\nRespuesta del protocolo:", respuesta)
    print("\nContenido de la carpeta remota:")

    for linea in lista:
        print(linea)

finally:
    f.quit()
