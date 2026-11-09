import socket
from email.message import EmailMessage
from email.policy import SMTP


SERVIDOR = "relay.uniovi.es"
PUERTO = 25


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
            f"Error SMTP: se esperaba {codigo_esperado}, "
            f"se recibió {codigo}"
        )


def comando(sock, archivo, texto, codigo):
    print("CLIENTE:", texto)
    sock.sendall((texto + "\r\n").encode())
    leer_respuesta(archivo, codigo)


def main():
    fromaddr = input("Correo Uniovi del remitente: ").strip()
    toaddr = input("Correo del destinatario: ").strip()

    subject = "Prueba EmailMessage desde Python"
    data = (
        "Este mensaje se ha construido utilizando EmailMessage.\n"
        "El envío se realiza mediante un socket SMTP."
    )

    mensaje = EmailMessage()

    mensaje["From"] = fromaddr
    mensaje["To"] = toaddr
    mensaje["Subject"] = subject

    mensaje.set_content(data)

    contenido = mensaje.as_bytes(policy=SMTP)

    print("\nMensaje MIME generado:")
    print(contenido.decode(errors="replace"))

    with socket.create_connection((SERVIDOR, PUERTO), timeout=15) as sock:
        archivo = sock.makefile("rb")

        leer_respuesta(archivo, 220)

        comando(sock, archivo, "EHLO localhost", 250)
        comando(sock, archivo, f"MAIL FROM:<{fromaddr}>", 250)
        comando(sock, archivo, f"RCPT TO:<{toaddr}>", 250)
        comando(sock, archivo, "DATA", 354)

        sock.sendall(contenido + b"\r\n.\r\n")

        leer_respuesta(archivo, 250)

        comando(sock, archivo, "QUIT", 221)

    print("\nCorreo enviado correctamente.")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print("\nERROR:", error)
