import socket

dominio = "en.wikipedia.org"

print("Consultando:", dominio)

try:
    resultados = socket.getaddrinfo(
        dominio,
        "www",
        type=socket.SOCK_STREAM
    )

    for resultado in resultados:
        print("\nResultado:")
        print("Familia:", resultado[0])
        print("Tipo:", resultado[1])
        print("Protocolo:", resultado[2])
        print("Nombre canónico:", resultado[3])
        print("Dirección:", resultado[4])

except socket.gaierror as error:
    print("Error:", error)
