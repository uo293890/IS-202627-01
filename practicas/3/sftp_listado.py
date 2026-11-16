import paramiko
import getpass
import base64

client = paramiko.SSHClient()

# Clave publica Ed25519 del servidor localhost
key = paramiko.Ed25519Key(
    data=base64.b64decode(
        b'AAAAC3NzaC1lZDI1NTE5AAAAIKtgafdhc316Q2PLR5AkJ4mYdweTCB8c2TRftFDkmrOK'
    )
)

# Registramos la clave para verificar el servidor
client.get_host_keys().add('localhost', 'ssh-ed25519', key)

clave = getpass.getpass("Clave del usuario uo302956: ")

client.connect(
    'localhost',
    username='uo302956',
    password=clave
)

sftp = client.open_sftp()

listado = sftp.listdir()

print("Contenido de la carpeta personal:")

for nombre in listado:
    print(nombre)

sftp.close()
client.close()
