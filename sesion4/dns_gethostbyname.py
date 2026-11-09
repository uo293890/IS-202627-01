import socket

dominios = [
    "apple.com",
    "www.uniovi.es"
]

for dominio in dominios:
    print("\n==========", dominio, "==========")

    try:
        resultado = socket.gethostbyname_ex(dominio)

        print("Nombre canónico:", resultado[0])
        print("Alias:", resultado[1])
        print("Direcciones IPv4:", resultado[2])

    except socket.gaierror as error:
        print("Error de resolución:", error)
