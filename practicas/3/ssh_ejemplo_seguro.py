import paramiko
import time
import getpass
import base64

client = paramiko.SSHClient()

key = paramiko.Ed25519Key(data=base64.b64decode(b'AAAAC3NzaC1lZDI1NTE5AAAAIKtgafdhc316Q2PLR5AkJ4mYdweTCB8c2TRftFDkmrOK'))
client.get_host_keys().add('localhost', 'ssh-ed25519', key)

clave = getpass.getpass("Clave del usuario alumno: ")

client.connect('localhost', username='uo302956', password=clave)
print("Conectado!!")

stdin, stdout, stderr = client.exec_command('ls')

for line in stdout:
    print(line.rstrip())

time.sleep(1)
client.close()
