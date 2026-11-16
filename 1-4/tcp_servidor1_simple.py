"""Ejercicio 1: recv(5) lee hasta cinco bytes, no necesariamente cinco."""
import os
import socket
import sys
import time

puerto = int(sys.argv[1]) if len(sys.argv) > 1 else 9999
retardo = float(os.environ.get("RETARDO_LECTURA", "0"))
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as escucha:
    escucha.bind(("", puerto))
    escucha.listen(5)
    while True:
        print("Esperando un cliente", flush=True)
        datos_socket, origen = escucha.accept()
        with datos_socket:
            print("Nuevo cliente:", origen, flush=True)
            time.sleep(retardo)
            while True:
                datos = datos_socket.recv(5)
                if not datos:
                    print("Conexion cerrada por el cliente", flush=True)
                    break
                mensaje = datos.decode("ascii")
                if mensaje == "FINAL":
                    print("Recibido mensaje de finalizacion", flush=True)
                    break
                print("Recibido:", repr(mensaje), flush=True)
