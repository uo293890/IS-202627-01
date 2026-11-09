import paramiko
import getpass
import base64
import stat
import os

# Crear cliente SSH
client = paramiko.SSHClient()

# Clave publica Ed25519 del servidor localhost
key = paramiko.Ed25519Key(
    data=base64.b64decode(
        b'AAAAC3NzaC1lZDI1NTE5AAAAIKtgafdhc316Q2PLR5AkJ4mYdweTCB8c2TRftFDkmrOK'
    )
)

# Registrar la clave para verificar el servidor
client.get_host_keys().add('localhost', 'ssh-ed25519', key)

# Solicitar contraseña
clave = getpass.getpass("Clave del usuario uo302956: ")

try:
    # Conectar al servidor
    client.connect(
        'localhost',
        username='uo302956',
        password=clave
    )

    # Abrir conexion SFTP
    sftp = client.open_sftp()

    # Solicitar carpeta remota
    carpeta_remota = input(
        "Carpeta remota que quieres descargar (Enter para tu carpeta personal): "
    ).strip()

    if carpeta_remota == "":
        carpeta_remota = "."

    # Crear carpeta local para las descargas
    carpeta_local = "descargas_sftp"
    os.makedirs(carpeta_local, exist_ok=True)

    print("\nArchivos encontrados:")

    # Obtener listado con sus atributos
    listado = sftp.listdir_attr(carpeta_remota)

    for elemento in listado:

        # Descargar solamente archivos normales, no directorios
        if stat.S_ISREG(elemento.st_mode):

            ruta_remota = carpeta_remota.rstrip("/") + "/" + elemento.filename
            ruta_local = os.path.join(carpeta_local, elemento.filename)

            print("Descargando:", elemento.filename)

            sftp.get(ruta_remota, ruta_local)

    print("\nDescarga finalizada.")
    print("Los archivos están en:", carpeta_local)

    sftp.close()

except Exception as error:
    print("\nSe ha producido un error:", error)

finally:
    client.close()
