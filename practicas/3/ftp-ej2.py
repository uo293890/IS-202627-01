import ftplib
import getpass

clave = getpass.getpass("Clave del usuario uo302956: ")

f = ftplib.FTP("localhost")

try:
    # Autenticarse
    f.login("uo302956", clave)
    print("Conectado al servidor FTP")

    # Entrar en la carpeta remota
    f.cwd("prueba-ftp")

    print("\nContenido de la carpeta remota:")

    # Obtener el listado mediante MLSD
    for nombre, atributos in f.mlsd():

        # Ignorar las pseudocarpetas
        if atributos.get("type") not in ("cdir", "pdir"):

            print(nombre)

finally:
    f.quit()
