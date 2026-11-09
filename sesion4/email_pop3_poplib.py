import poplib
import ssl
import getpass


SERVIDOR = "pop.gmail.com"
PUERTO = 995


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
        servidor.set_debuglevel(2)

        print("\n========== AUTENTICACION ==========")

        servidor.user(usuario)
        servidor.pass_(password)

        print("\n========== ESTADO DEL BUZON ==========")

        numero_mensajes, tamano = servidor.stat()

        print("Número de mensajes:", numero_mensajes)
        print("Tamaño total:", tamano, "bytes")

        if numero_mensajes > 0:

            print("\n========== PRIMER MENSAJE ==========")

            respuesta, lineas, octetos = servidor.retr(1)

            print("Respuesta:", respuesta)
            print("Tamaño:", octetos)

            print("\nContenido del mensaje:\n")

            for linea in lineas:
                print(linea.decode(errors="replace"))

        else:
            print("No hay mensajes en el buzón.")

    finally:
        servidor.quit()

    print("\nConexión POP3 finalizada.")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print("\nERROR:", error)
