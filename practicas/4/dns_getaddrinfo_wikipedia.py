import socket

dominio = "en.wikipedia.org"
puerto = 80

print("Resolviendo:", dominio)

try:
    resultados = socket.getaddrinfo(
        dominio,
        puerto,
        family=socket.AF_INET,
        type=socket.SOCK_STREAM
    )

    conectado = False

    for resultado in resultados:
        familia, tipo, protocolo, canonico, direccion = resultado

        try:
            print("Intentando conectar con:", direccion)

            with socket.socket(familia, tipo, protocolo) as conexion:
                conexion.settimeout(10)
                conexion.connect(direccion)

                peticion = (
                    "GET / HTTP/1.1\r\n"
                    "Host: en.wikipedia.org\r\n"
                    "Connection: close\r\n"
                    "\r\n"
                )

                conexion.sendall(peticion.encode())

                print("\nRespuesta del servidor:\n")

                while True:
                    datos = conexion.recv(4096)

                    if not datos:
                        break

                    print(datos.decode("utf-8", errors="replace"), end="")

                conectado = True
                break

        except OSError as error:
            print("No se pudo utilizar esta dirección:", error)

    if not conectado:
        print("No se ha podido establecer la conexión.")

except socket.gaierror as error:
    print("Error DNS:", error)

print("\n\n========== PRUEBA IPV6 ==========")

try:
    resultados_ipv6 = socket.getaddrinfo(
        dominio,
        puerto,
        family=socket.AF_INET6,
        type=socket.SOCK_STREAM
    )

    for resultado in resultados_ipv6:
        familia, tipo, protocolo, canonico, direccion = resultado

        try:
            with socket.socket(familia, tipo, protocolo) as conexion:
                conexion.settimeout(10)
                conexion.connect(direccion)
                print("Conexión IPv6 establecida:", direccion)
                break

        except OSError as error:
            print("No se pudo conectar por IPv6:", error)

except socket.gaierror as error:
    print("No hay resolución IPv6 disponible:", error)
