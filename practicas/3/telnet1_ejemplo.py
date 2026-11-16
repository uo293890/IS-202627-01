import getpass
import telnetlib

HOST = "192.168.207.149"
user = input("Enter your remote account: ")
password = getpass.getpass()

tn = telnetlib.Telnet(HOST)

tn.read_until(b"login: ")
tn.write(user.encode('ascii') + b"\n")
if password:
    tn.read_until(b"Password: ")
    tn.write(password.encode('ascii') + b"\n")
## Si se queda congelado read untel %$ y ya esta
tn.write(b"cd /home\n")
tn.write(b"ls\n")
tn.write(b"exit\n")

print(tn.read_all().decode()) ## Quitmos el ascii
