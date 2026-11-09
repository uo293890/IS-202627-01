import socket
import ssl
import base64
import getpass

from email.message import EmailMessage
from email.policy import SMTP


SERVIDOR = "smtp.gmail.com"
PUERTO = 587


def leer_respuesta(archivo, codigo_esperado):
    while True:
        linea = archivo.readline()

        if not linea:
            raise ConnectionError("El servidor ha cerrado la conexión.")

        print("SERVIDOR:", linea.decode(errors="replace").rstrip())

        if len(linea) >= 4 and linea[3:4] == b" ":
            break

    codigo = int(linea[:3])

    if codigo != codigo_esperado:
        raise RuntimeError(
            f"Se esperaba {codigo_esperado}, se recibió {codigo}"
        )


def comando(sock, archivo, texto, codigo):
    print("CLIENTE:", texto)
    sock.sendall((texto + "\r\n").encode())
    leer_respuesta(archivo, codigo)


def main():
    usuario = input("Correo de Gmail: ").strip()
    password = getpass.getpass("Contraseña de aplicación: ")

    mensaje = EmailMessage()
    mensaje["From"] = usuario
    mensaje["To"] = usuario
    mensaje["Subject"] = "Prueba SMTP Gmail con STARTTLS"

    mensaje.set_content(
        "Este correo se ha enviado desde Python utilizando "
        "sockets, SMTP, STARTTLS y autenticación."
    )

    contenido = mensaje.as_bytes(policy=SMTP)

    contexto = ssl.create_default_context()

    sock = socket.create_connection(
        (SERVIDOR, PUERTO),
        timeout=20
    )

    try:
        archivo = sock.makefile("rb")

        leer_respuesta(archivo, 220)

        comando(sock, archivo, "EHLO localhost", 250)

        comando(sock, archivo, "STARTTLS", 220)

        # Cerramos el lector asociado al socket sin cerrar el socket.
        archivo.close()

        # A partir de aquí toda la comunicación estará cifrada.
        sock = contexto.wrap_socket(
            sock,
            server_hostname=SERVIDOR
        )

        archivo = sock.makefile("rb")

        print("\nConexión TLS establecida.")

        comando(sock, archivo, "EHLO localhost", 250)

        comando(sock, archivo, "AUTH LOGIN", 334)

        usuario_b64 = base64.b64encode(
            usuario.encode()
        ).decode()

        sock.sendall((usuario_b64 + "\r\n").encode())
        leer_respuesta(archivo, 334)

        password_b64 = base64.b64encode(
            password.encode()
        ).decode()

        sock.sendall((password_b64 + "\r\n").encode())
        leer_respuesta(archivo, 235)

        comando(sock, archivo, f"MAIL FROM:<{usuario}>", 250)
        comando(sock, archivo, f"RCPT TO:<{usuario}>", 250)
        comando(sock, archivo, "DATA", 354)

        sock.sendall(contenido + b"\r\n.\r\n")
        leer_respuesta(archivo, 250)

        comando(sock, archivo, "QUIT", 221)

        archivo.close()

    finally:
        sock.close()

    print("\nCorreo enviado correctamente.")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print("\nERROR:", error)
