import socket
import ssl
import getpass

from email.parser import BytesParser
from email.policy import default


SERVIDOR = "pop.gmail.com"
PUERTO = 995


def leer_respuesta(archivo):
    linea = archivo.readline()

    if not linea:
        raise ConnectionError("El servidor ha cerrado la conexión.")

    if not linea.startswith(b"+OK"):
        raise RuntimeError(
            linea.decode(errors="replace")
        )

    return linea


def comando(sock, archivo, texto):
    sock.sendall((texto + "\r\n").encode())
    return leer_respuesta(archivo)


def leer_mensaje(archivo):
    lineas = []

    while True:
        linea = archivo.readline()

        if not linea:
            raise ConnectionError("Conexión cerrada.")

        if linea == b".\r\n":
            break

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

            respuesta = comando(sock, archivo, "STAT")

            partes = respuesta.decode().split()

            numero_mensajes = int(partes[1])

            print("Número de mensajes:", numero_mensajes)

            for numero in range(1, numero_mensajes + 1):

                print("\n========== MENSAJE", numero, "==========")

                comando(sock, archivo, f"RETR {numero}")

                contenido = leer_mensaje(archivo)

                mensaje = BytesParser(
                    policy=default
                ).parsebytes(contenido)

                print("De:", mensaje.get("From", "(sin remitente)"))
                print("Asunto:", mensaje.get("Subject", "(sin asunto)"))

            comando(sock, archivo, "QUIT")

            archivo.close()


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print("\nERROR:", error)
