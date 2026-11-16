import poplib
import ssl
import getpass

from email import message_from_bytes
from email.header import decode_header, make_header


SERVIDOR = "pop.gmail.com"
PUERTO = 995


def decodificar_cabecera(valor):
    if not valor:
        return "(sin información)"

    try:
        return str(
            make_header(
                decode_header(str(valor))
            )
        )
    except Exception:
        return str(valor)


def obtener_cuerpo(mensaje):
    # Si el mensaje tiene varias partes, buscamos texto plano.
    if mensaje.is_multipart():

        for parte in mensaje.walk():

            if parte.get_content_type() == "text/plain":

                if parte.get_content_disposition() == "attachment":
                    continue

                contenido = parte.get_payload(decode=True)

                if contenido:
                    charset = parte.get_content_charset() or "utf-8"

                    return contenido.decode(
                        charset,
                        errors="replace"
                    )

        return "(No se ha encontrado texto plano.)"

    contenido = mensaje.get_payload(decode=True)

    if contenido is None:
        payload = mensaje.get_payload()

        return str(payload)

    charset = mensaje.get_content_charset() or "utf-8"

    return contenido.decode(
        charset,
        errors="replace"
    )


def imprime_resumen_mensaje(msg_bytes):
    mensaje = message_from_bytes(msg_bytes)

    remitente = decodificar_cabecera(
        mensaje.get("From")
    )

    asunto = decodificar_cabecera(
        mensaje.get("Subject")
    )

    cuerpo = obtener_cuerpo(mensaje)

    print("De:", remitente)
    print("Asunto:", asunto)

    print("\nPrimeros 500 caracteres del cuerpo:")

    print(cuerpo[:500])

    print("\n" + "=" * 60)


def main():
    usuario = input("Correo de Gmail: ").strip()
    password = getpass.getpass("Contraseña de aplicación: ")

    contexto = ssl.create_default_context()

    servidor = poplib.POP3_SSL(
        SERVIDOR,
        PUERTO,
        context=contexto,
        timeout=20
    )

    try:
        servidor.set_debuglevel(0)

        servidor.user(usuario)
        servidor.pass_(password)

        numero_mensajes, tamano = servidor.stat()

        print("Número de mensajes:", numero_mensajes)
        print("Tamaño total:", tamano, "bytes")

        for numero in range(1, numero_mensajes + 1):

            print("\n========== MENSAJE", numero, "==========")

            respuesta, lineas, octetos = servidor.retr(numero)

            # Convertimos las líneas recibidas en un único mensaje.
            msg_bytes = b"\r\n".join(lineas) + b"\r\n"

            imprime_resumen_mensaje(msg_bytes)

    finally:
        servidor.quit()

    print("Conexión finalizada.")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print("\nERROR:", error)
