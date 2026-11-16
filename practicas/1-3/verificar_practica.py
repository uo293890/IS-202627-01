#!/usr/bin/env python3
"""Ejecuta los programas de la práctica y conserva las salidas reales.

Con --capturas se detiene tras cada bloque hasta pulsar Intro. No requiere
bibliotecas externas. Las pérdidas se simulan con semilla 1 para repetirlas.
"""
import argparse
import contextlib
import datetime
import io
import ipaddress
import json
import os
from pathlib import Path
import platform
import shlex
import socket
import subprocess
import sys
import tempfile
import time

BASE = Path(__file__).resolve().parent
EVIDENCIAS = BASE / "memoria" / "evidencias"
RESULTADOS = {}
PAUSA = False
CONTENEDORES = []
PREFIJO = "is13_verificacion_"


def ejecutar(args, entrada=None, esperado=0, mostrar=True, limite=90):
    print("$ " + shlex.join(str(a) for a in args), flush=True)
    if entrada is not None:
        print("Entrada: " + repr(entrada), flush=True)
    r = subprocess.run(args, cwd=BASE, input=entrada, text=True,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                       timeout=limite)
    if mostrar:
        print(r.stdout.rstrip(), flush=True)
    if esperado is not None:
        assert r.returncode == esperado, (r.returncode, r.stdout)
    return r


@contextlib.contextmanager
def servidor(nombre, puerto, semilla=None):
    if semilla is None:
        args = [sys.executable, "-u", nombre, str(puerto)]
    else:
        codigo = ("import random,runpy,sys; random.seed(1); "
                  "sys.argv=sys.argv[1:]; runpy.run_path(sys.argv[0],run_name='__main__')")
        args = [sys.executable, "-u", "-c", codigo, nombre, str(puerto)]
    print("Servidor: " + nombre + " puerto " + str(puerto)
          + ("; random.seed(1)" if semilla is not None else ""), flush=True)
    with tempfile.TemporaryFile(mode="w+", encoding="utf-8") as log:
        proceso = subprocess.Popen(args, cwd=BASE, stdout=log, stderr=subprocess.STDOUT)
        time.sleep(0.3)
        assert proceso.poll() is None, "El servidor no pudo arrancar"
        try:
            yield log
        finally:
            proceso.terminate()
            try:
                proceso.wait(3)
            except subprocess.TimeoutExpired:
                proceso.kill()
                proceso.wait()
            log.seek(0)
            salida = log.read()
            print("\nSalida del servidor:\n" + salida.rstrip(), flush=True)


def cliente(nombre, puerto, mensajes, ip="127.0.0.1", esperado=0, mostrar=True):
    return ejecutar([sys.executable, "-u", nombre, ip, str(puerto)],
                    "\n".join(mensajes + ["FIN", ""]), esperado, mostrar)


def comprobar(condicion, texto):
    assert condicion, texto
    print("CORRECTO: " + texto, flush=True)


def entorno():
    ejecutar(["date", "--iso-8601=seconds"])
    ejecutar(["uname", "-sr"])
    print("Python anfitrion: " + platform.python_version())
    ejecutar(["docker", "version", "--format", "Cliente {{.Client.Version}} Servidor {{.Server.Version}}"])
    ejecutar(["docker", "image", "ls", "--format", "{{.Repository}}:{{.Tag}}", "python"])
    ejecutar(["docker", "network", "inspect", "pruebas", "--format",
              "{{range .IPAM.Config}}{{.Subnet}}{{end}}"])


def ejercicio1():
    with servidor("udp_servidor1.py", 9999):
        ejecutar([sys.executable, "udp_cliente1.py"], "Hola por UDP\nEspana y niñez\nFIN\n")
        time.sleep(0.15)
    externo = EVIDENCIAS / "01_otra_maquina.txt"
    if externo.exists():
        print("\nPrueba adicional Windows -> VM (puerto 19991):")
        print(externo.read_text(encoding="utf-8").strip())
    else:
        print("La prueba entre dos maquinas se ejecuta por separado.")


def ejercicio2():
    with servidor("udp_servidor2_simula_perdidas.py", 19992, 1) as log:
        cliente("udp_cliente2_numera_mensajes.py", 19992,
                ["dato%02d" % i for i in range(1, 13)], mostrar=False)
        time.sleep(0.15)
        log.seek(0)
        salida = log.read()
        comprobar("Simulando" in salida and "Recibido" in salida,
                  "se observan perdidas simuladas y mensajes recibidos")


def ejercicio3():
    with servidor("udp_servidor3_con_ok.py", 19993, 1):
        r = cliente("udp_cliente3_espera_ok.py", 19993,
                    ["dato%d" % i for i in range(1, 7)])
        comprobar("confirmación" in r.stdout and "ERROR" in r.stdout,
                  "el cliente distingue confirmaciones y timeouts")


def ejercicio4():
    with servidor("udp_servidor3_con_ok.py", 19994, 1):
        r = cliente("udp_cliente4_reintenta.py", 19994, ["Reintento con el mismo numero"])
        comprobar("Timeout: 0.4s" in r.stdout and "Recibida" in r.stdout,
                  "reenvia con 0.1, 0.2 y 0.4 segundos hasta recibir OK")


def servidor_caido():
    r = cliente("udp_cliente4_reintenta.py", 19995, ["Sin servidor"], esperado=1)
    comprobar("Timeout: 1.6s" in r.stdout and "Inténtelo más tarde" in r.stdout,
              "abandona cuando el siguiente timeout seria 3.2 > 2 segundos")


def ejercicio5():
    with servidor("udp_servidor5_mejorado.py", 19996, 1) as log:
        cliente("udp_cliente5_mejorado.py", 19996, ["Cliente mejorado"])
        print("Prueba adicional: mismo datagrama dos veces desde el mismo socket.")
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.settimeout(0.15)
            for repeticion in range(2):
                for intento in range(20):
                    s.sendto(b"1:Duplicado controlado", ("127.0.0.1", 19996))
                    try:
                        respuesta, _ = s.recvfrom(1024)
                        comprobar(respuesta == b"OK:1", "el ACK identifica el paquete 1")
                        break
                    except socket.timeout:
                        pass
                else:
                    raise AssertionError("No se obtuvo ACK")
        time.sleep(0.1)
        log.seek(0)
        salida = log.read()
        comprobar("Ignorando duplicado" in salida,
                  "el servidor confirma duplicados sin repetir el procesamiento")
        comprobar(salida.count("Procesando nuevo paquete") == 2,
                  "dos clientes distintos pueden utilizar la secuencia 1")


def ejercicio6():
    with servidor("udp_servidor6_broadcast.py", 12345):
        r = ejecutar([sys.executable, "udp_cliente6_broadcast.py", "127.255.255.255"])
        comprobar("Servidor encontrado" in r.stdout and "HOLA: 127.0.0.1" in r.stdout,
                  "descubre el servicio por broadcast local y lo usa por unicast")


def docker_basico():
    ejecutar([sys.executable, "prueba.py"])
    ejecutar(["docker", "run", "--rm", "python:3.7", "python", "--version"])
    r = ejecutar(["docker", "run", "--rm", "python:3.7", "python", "prueba.py"], esperado=2)
    comprobar("No such file" in r.stdout, "sin volumen el contenedor no ve prueba.py")
    for imagen in ["python:3.7", "python:3.6"]:
        ejecutar(["docker", "run", "--rm", "-v", str(BASE) + ":/app:ro",
                  imagen, "python", "/app/prueba.py"])
    ejecutar(["docker", "run", "--rm", "python:3.7", "bash", "-c",
              "command -v python; rm /usr/local/bin/python; python --version"], esperado=127)
    ejecutar(["docker", "run", "--rm", "python:3.7", "python", "--version"])
    print("CORRECTO: borrar python en un contenedor no modifica la imagen.")


def lanzar_docker(sufijo, programa, red=None):
    nombre = PREFIJO + sufijo
    args = ["docker", "run", "-d", "--name", nombre]
    if red:
        args += ["--network", red]
    args += ["-v", str(BASE) + ":/app:ro", "python:3.7", "python", "-u", "/app/" + programa]
    ejecutar(args)
    CONTENEDORES.append(nombre)
    time.sleep(0.4)
    return nombre


def docker_udp():
    nombre = lanzar_docker("udp", "udp_servidor3_con_ok.py")
    ip = ejecutar(["docker", "inspect", nombre, "--format",
                   "{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}"], mostrar=False).stdout.strip()
    print("IP del servidor: " + ip)
    cliente("udp_cliente4_reintenta.py", 9999, ["Cliente de la VM"], ip)
    ejecutar(["docker", "run", "--rm", "-i", "-v", str(BASE) + ":/app:ro", "python:3.7",
              "python", "/app/udp_cliente4_reintenta.py", ip, "9999"], "Cliente en contenedor\nFIN\n")
    ejecutar(["docker", "exec", nombre, "ps", "-eo", "pid,args"])


def docker_dns():
    nombre = lanzar_docker("dns", "udp_servidor3_con_ok.py", "pruebas")
    ejecutar(["docker", "run", "--rm", "--network", "pruebas", "python:3.7", "python", "-c",
              "import socket; print(socket.gethostbyname(%r))" % nombre])
    ejecutar(["docker", "run", "--rm", "-i", "--network", "pruebas", "-v", str(BASE) + ":/app:ro",
              "python:3.7", "python", "/app/udp_cliente4_reintenta.py", nombre, "9999"],
              "Servidor por nombre DNS\nFIN\n")
    ejecutar(["docker", "logs", nombre])


def ejercicio7():
    # No reutilizar contenedores desconocidos ni borrar recursos de otras sesiones.
    for i in range(1, 4):
        r = subprocess.run(["docker", "container", "inspect", "server_hola_%d" % i],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        comprobar(r.returncode != 0, "server_hola_%d no existia antes de la prueba" % i)
    CONTENEDORES.extend(["server_hola_%d" % i for i in range(1, 4)])
    ejecutar(["bash", "udp_docker_lanzar_servidores.sh"])
    ejecutar(["docker", "inspect", "server_hola_1", "--format",
              "{{range .NetworkSettings.Networks}}IP={{.IPAddress}} prefijo={{.IPPrefixLen}}{{end}}"])
    r = ejecutar(["bash", "udp_docker_lanzar_cliente.sh"])
    comprobar(r.stdout.count("Servidor encontrado en:") == 3,
              "el cliente descubre exactamente tres servidores")
    comprobar("Respuesta final: HOLA:" in r.stdout,
              "el primer servidor devuelve la IP del cliente")
    # Repetir el arranque verifica que los scripts son reutilizables.
    ejecutar(["bash", "udp_docker_lanzar_servidores.sh"], mostrar=False)
    comprobar(True, "el segundo arranque conserva los tres servidores sin conflictos")


class Duplicar(io.TextIOBase):
    def __init__(self, original, archivo):
        self.original, self.archivo = original, archivo

    def write(self, texto):
        self.original.write(texto)
        self.archivo.write(texto)
        return len(texto)

    def flush(self):
        self.original.flush()
        self.archivo.flush()


def bloque(identificador, titulo, funcion):
    if PAUSA:
        print("\033[2J\033[H", end="", flush=True)
    nombre = identificador + ".txt"
    with (EVIDENCIAS / nombre).open("w", encoding="utf-8") as archivo:
        with contextlib.redirect_stdout(Duplicar(sys.stdout, archivo)):
            print("INGENIERIA DE SERVICIOS | Practica 1.3 | " + titulo)
            print("Usuario: " + os.environ.get("USER", "") + " | Equipo: " + platform.node())
            print()
            funcion()
            print("\nBLOQUE VERIFICADO: " + identificador, flush=True)
    RESULTADOS[identificador] = {"resultado": "correcto", "registro": nombre}
    (EVIDENCIAS / "resultados.json").write_text(
        json.dumps({"fecha": datetime.datetime.now().astimezone().isoformat(), "bloques": RESULTADOS},
                   ensure_ascii=False, indent=2), encoding="utf-8")
    if PAUSA:
        (EVIDENCIAS / ".captura_lista").write_text(identificador, encoding="utf-8")
        input("Captura preparada. Pulsa Intro para continuar...")
        (EVIDENCIAS / ".captura_lista").unlink(missing_ok=True)


def main():
    global PAUSA
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--capturas", action="store_true")
    args = p.parse_args()
    PAUSA = args.capturas
    EVIDENCIAS.mkdir(parents=True, exist_ok=True)
    bloques = [
        ("00_entorno", "Entorno de ejecucion", entorno),
        ("01_udp_basico", "Ejercicio 1 UDP basico", ejercicio1),
        ("02_perdidas", "Ejercicio 2 Perdidas y numeracion", ejercicio2),
        ("03_confirmaciones", "Ejercicio 3 Confirmaciones y timeout", ejercicio3),
        ("04_reintentos", "Ejercicio 4 Reintentos", ejercicio4),
        ("05_servidor_caido", "Ejercicio 4 Servidor ausente", servidor_caido),
        ("06_mejoras", "Ejercicio 5 Identificacion y duplicados", ejercicio5),
        ("07_broadcast_local", "Ejercicio 6 Broadcast local", ejercicio6),
        ("08_docker_basico", "Docker Imagenes y volumenes", docker_basico),
        ("09_docker_udp", "Docker UDP en la red bridge", docker_udp),
        ("10_docker_dns", "Docker Red propia y DNS", docker_dns),
        ("11_tres_servidores", "Ejercicio 7 Tres servidores", ejercicio7),
    ]
    try:
        for identificador, titulo, funcion in bloques:
            bloque(identificador, titulo, funcion)
        print("\nLos doce bloques de verificacion han terminado correctamente.")
    finally:
        for nombre in CONTENEDORES:
            subprocess.run(["docker", "rm", "-f", nombre], stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)
        (EVIDENCIAS / ".captura_lista").unlink(missing_ok=True)


if __name__ == "__main__":
    main()
