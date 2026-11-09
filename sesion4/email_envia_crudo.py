import socket
import getpass

SERVIDOR = "relay.uniovi.es"
PUERTO = 25


def leer_respuesta(archivo, codigo_esperado):
    lineas = []

    while True:
        linea = archivo.readline()

        if not linea:
            raise ConnectionError("El servidor ha cerrado la conexión.")

        print("SERVIDOR:", linea.decode(errors="replace").rstrip())
        lineas.append(linea)

        # Una respuesta SMTP termina cuando el cuarto carácter es un espacio.
        if len(linea) >= 4 and linea[3:4] == b" ":
            break

    codigo = int(lineas[-1][:3])

    if codigo != codigo_esperado:
        raise RuntimeError(
            f"Respuesta inesperada: {codigo}. "
            f"Se esperaba: {codigo_esperado}"
        )

    return lineas


def comando(sock, archivo, texto, codigo):
    print("CLIENTE:", texto)
    sock.sendall((texto + "\r\n").encode())
    return leer_respuesta(archivo, codigo)


def main():
    correo = input("Introduce tu correo de Uniovi: ").strip()

    if not correo:
        print("Debes introducir una dirección de correo.")
        return

    remitente = correo
    destinatario = correo

    asunto = "Prueba SMTP desde Python"
    cuerpo = "Este mensaje se ha enviado utilizando sockets y SMTP."

    mensaje = (
        f"From: {remitente}\r\n"
        f"To: {destinatario}\r\n"
        f"Subject: {asunto}\r\n"
        "\r\n"
        f"{cuerpo}\r\n"
    )

    print("\nConectando con", SERVIDOR)

    with socket.create_connection((SERVIDOR, PUERTO), timeout=15) as sock:
        archivo = sock.makefile("rb")

        leer_respuesta(archivo, 220)

        comando(sock, archivo, "EHLO localhost", 250)
        comando(sock, archivo, f"MAIL FROM:<{remitente}>", 250)
        comando(sock, archivo, f"RCPT TO:<{destinatario}>", 250)

        comando(sock, archivo, "DATA", 354)

        print("CLIENTE: Enviando mensaje...")

        sock.sendall(
            mensaje.encode("utf-8") + b"\r\n.\r\n"
        )

        leer_respuesta(archivo, 250)

        comando(sock, archivo, "QUIT", 221)

    print("\nMensaje enviado correctamente.")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print("\nERROR:", error)
