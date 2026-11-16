import smtplib
import ssl
import getpass

from email.message import EmailMessage


SERVIDOR = "smtp.gmail.com"
PUERTO = 587


def main():
    usuario = input("Correo de Gmail: ").strip()
    password = getpass.getpass("Contraseña de aplicación: ")

    mensaje = EmailMessage()

    mensaje["From"] = usuario
    mensaje["To"] = usuario
    mensaje["Subject"] = "Prueba de envío mediante smtplib"

    mensaje.set_content(
        "Este correo se ha enviado utilizando la biblioteca "
        "smtplib de Python."
    )

    contexto = ssl.create_default_context()

    with smtplib.SMTP(SERVIDOR, PUERTO, timeout=20) as servidor:

        # Mostrar el diálogo SMTP.
        servidor.set_debuglevel(1)

        # Identificación del cliente.
        servidor.ehlo()

        # Activar conexión cifrada.
        servidor.starttls(context=contexto)

        # Volver a identificarse después de STARTTLS.
        servidor.ehlo()

        # Autenticación.
        servidor.login(usuario, password)

        # Enviar mensaje.
        servidor.send_message(mensaje)

        print("\nMensaje enviado correctamente.")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print("\nERROR:", error)
