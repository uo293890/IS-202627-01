import socket
import ssl
import getpass


SERVIDOR = "pop.gmail.com"
PUERTO = 995


def leer_respuesta(archivo):
    linea = archivo.readline()

    if not linea:
        raise ConnectionError("El servidor ha cerrado la conexión.")

    print("SERVIDOR:", linea.decode(errors="replace").rstrip())

    if not linea.startswith(b"+OK"):
        raise RuntimeError("El servidor ha rechazado el comando.")

    return linea


def comando(sock, archivo, texto):
    print("CLIENTE:", texto)
    sock.sendall((texto + "\r\n").encode())
    return leer_respuesta(archivo)


def leer_mensaje(archivo):
    lineas = []

    while True:
        linea = archivo.readline()

        if not linea:
            raise ConnectionError("Conexión cerrada durante RETR.")

        if linea == b".\r\n":
            break

        # POP3 duplica los puntos iniciales de las líneas.
        if linea.startswith(b".."):
            linea = linea[1:]

        lineas.append(linea)

    return b"".join(lineas)


def main():
    usuario = input("Correo de Gmail: ").strip()
    password = getpass.getpass("Contraseña de aplicación: ")

    contexto = ssl.create_default_context()

    with socket.create_connection(
        (SERVIDOR, PUERTO),
        timeout=20
    ) as conexion:

        with contexto.wrap_socket(
            conexion,
            server_hostname=SERVIDOR
        ) as sock:

            archivo = sock.makefile("rb")

            leer_respuesta(archivo)

            comando(sock, archivo, f"USER {usuario}")
            comando(sock, archivo, f"PASS {password}")

            print("\n========== ESTADO DEL BUZON ==========")
            comando(sock, archivo, "STAT")

            print("\n========== PRIMER MENSAJE ==========")
            comando(sock, archivo, "RETR 1")

            contenido = leer_mensaje(archivo)

            print("\nContenido del mensaje:\n")
            print(contenido.decode(errors="replace"))

            comando(sock, archivo, "QUIT")

            archivo.close()


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print("\nERROR:", error)
