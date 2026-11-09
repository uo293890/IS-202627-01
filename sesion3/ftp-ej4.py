import ftplib
import getpass
import os

# Solicitar contraseña
clave = getpass.getpass("Clave del usuario uo302956: ")

# Conectar al servidor FTP
f = ftplib.FTP("localhost")

try:
    # Autenticarse
    f.login("uo302956", clave)
    print("Conectado al servidor FTP")

    # Cambiar a la carpeta remota
    carpeta_remota = "prueba-ftp"
    f.cwd(carpeta_remota)

    # Crear carpeta local para las descargas
    carpeta_local = "descargas_ftp"
    os.makedirs(carpeta_local, exist_ok=True)

    print("\nContenido de la carpeta remota:")

    # Obtener listado de la carpeta mediante MLSD
    for nombre, atributos in f.mlsd():

        tipo = atributos.get("type")

        # Descargar solamente archivos normales
        if tipo == "file":

            ruta_local = os.path.join(carpeta_local, nombre)

            print("Descargando:", nombre)

            # Descargar en modo binario
            with open(ruta_local, "wb") as archivo:
                f.retrbinary(
                    "RETR " + nombre,
                    archivo.write
                )

        elif tipo == "dir":
            print("Ignorando directorio:", nombre)

    print("\nDescarga finalizada.")
    print("Archivos guardados en:", carpeta_local)

finally:
    f.quit()
