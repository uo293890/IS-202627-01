import paramiko
import time
import getpass

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.WarningPolicy())
password = getpass.getpass("Clave del usuario alumno: ")
client.connect('localhost', username='uo302956', password=password) 
print("Conectado!!")

# Ejecutar comando remoto, redireccionando sus salidas
stdin, stdout, stderr = client.exec_command('ls')

# Mostrar resultado de la ejecución (rstrip quita los retornos de carro)
for line in stdout:
    print(line.rstrip())
time.sleep(1)  # Dar tiempo a que se vacie el buffer
client.close()


##VAMOS POR EL EJER9