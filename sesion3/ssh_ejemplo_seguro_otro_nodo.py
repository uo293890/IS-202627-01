import paramiko
import time
import getpass
import base64

client = paramiko.SSHClient()

key = paramiko.Ed25519Key(data=base64.b64decode(b'CLAVE_COMPANERO'))

client.get_host_keys().add(
    'SERVIDOR_COMPANERO',
    'ssh-ed25519',
    key
)

clave = getpass.getpass("Clave del usuario alumno: ")

client.connect(
    'SERVIDOR_COMPANERO',
    username='uoXXXXXX',
    password=clave
)

print("Conectado!!")

stdin, stdout, stderr = client.exec_command('ls')

for line in stdout:
    print(line.rstrip())

time.sleep(1)
client.close()
