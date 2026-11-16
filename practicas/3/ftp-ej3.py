import ftplib
import getpass

# Solicitar contraseña
clave = getpass.getpass("Clave del usuario uo302956: ")

# Conectar al servidor FTP
f = ftplib.FTP("localhost")

try:
    # Autenticarse
    f.login("uo302956", clave)
    print("Conectado al servidor FTP")

    # Cambiar a la carpeta donde esta el fichero
    f.cwd("prueba-ftp")

    # Crear fichero local y descargar en modo binario
    with open("prueba_ftp_copia.txt", "wb") as f_local:
        respuesta = f.retrbinary(
            "RETR prueba_ftp.txt",
            f_local.write
        )

    print("Descarga completada")
    print("Respuesta del servidor:", respuesta)

finally:
    f.quit()
