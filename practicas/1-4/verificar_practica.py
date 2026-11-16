#!/usr/bin/env python3
"""Ejecuta los ejercicios TCP sin modificar los archivos existentes.

--capturas pausa entre bloques. --esperar-windows espera una comprobación
externa nueva contra el puerto publicado 9090. No requiere módulos externos.
"""
import argparse
import contextlib
import datetime
import io
import json
import os
from pathlib import Path
import platform
import shlex
import socket
import struct
import subprocess
import sys
import tempfile
import time

BASE = Path(__file__).resolve().parent
EVIDENCIAS = BASE / "memoria/evidencias"
CONTENEDORES = []
REDES = []
RESULTADOS = {}
PAUSA = False
WINDOWS = False
NOMBRE = "is14_oche"


def ejecutar(args, entrada=None, esperado=0, mostrar=True, limite=30):
    print("$ " + shlex.join(str(x) for x in args), flush=True)
    r = subprocess.run(args, cwd=BASE, input=entrada, text=True,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=limite)
    if mostrar:
        print(r.stdout.rstrip(), flush=True)
    assert r.returncode == esperado, (r.returncode, r.stdout)
    return r


def comprobar(condicion, texto):
    assert condicion, texto
    print("CORRECTO: " + texto, flush=True)


@contextlib.contextmanager
def servidor(nombre, puerto, retardo=0):
    # El retardo se inyecta únicamente en la ejecución de prueba. El código
    # fuente del alumno permanece intacto, incluido el ejercicio 5 existente.
    codigo = (
        "import socket,time,runpy,sys; "
        "original=socket.socket.accept; "
        "retardo=float(sys.argv[1]); "
        "socket.socket.accept=lambda self: (lambda r: (time.sleep(retardo),r)[1])(original(self)); "
        "sys.argv=sys.argv[2:]; runpy.run_path(sys.argv[0],run_name='__main__')"
    )
    print("Servidor:", nombre, "puerto", puerto, "retardo tras accept:", retardo, "s", flush=True)
    with tempfile.TemporaryFile(mode="w+", encoding="utf8") as log:
        p = subprocess.Popen([sys.executable, "-u", "-c", codigo, str(retardo), nombre, str(puerto)],
                             cwd=BASE, stdout=log, stderr=subprocess.STDOUT)
        time.sleep(0.25)
        comprobar(p.poll() is None, "el servidor arranca")
        try:
            yield log
        finally:
            p.terminate()
            try:
                p.wait(3)
            except subprocess.TimeoutExpired:
                p.kill()
                p.wait()
            log.seek(0)
            salida = log.read().strip()
            if salida:
                print("Salida del servidor:\n" + salida, flush=True)


def cliente(nombre, puerto, esperado=0, entrada=None, ip="127.0.0.1"):
    return ejecutar([sys.executable, "-u", nombre, ip, str(puerto)], entrada, esperado)


def enviar_trozos(puerto, trozos, espera=0.12):
    with socket.create_connection(("127.0.0.1", puerto), timeout=5) as s:
        for trozo in trozos:
            print("sendall:", repr(trozo), flush=True)
            s.sendall(trozo)
            time.sleep(espera)
        s.shutdown(socket.SHUT_WR)
    time.sleep(0.2)


def entorno():
    ejecutar(["date", "--iso-8601=seconds"])
    print("Equipo:", platform.node(), "Python:", platform.python_version())
    ejecutar(["docker", "version", "--format", "Cliente {{.Client.Version}} Servidor {{.Server.Version}}"])
    ejecutar(["docker", "network", "inspect", "pruebas", "--format", "{{range .IPAM.Config}}{{.Subnet}}{{end}}"])
    print("Se conservan los seis programas existentes de los ejercicios 2, 5 y 7.")


def ejercicio1():
    with servidor("tcp_servidor1_simple.py", 20101) as log:
        cliente("tcp_cliente1_simple.py", 20101)
        time.sleep(0.1)
        log.seek(0)
        salida = log.read()
        comprobar(salida.count("Recibido: 'ABCDE'") == 5 and "finalizacion" in salida,
                  "llegan cinco bloques ABCDE y se reconoce FINAL")


def ejercicio2():
    with servidor("tcp_servidor1_simple.py", 20102):
        enviar_trozos(20102, [b"A", b"BC", b"DE", b"FINAL"])
    with servidor("tcp_servidor2_recvall.py", 20103) as log:
        enviar_trozos(20103, [b"A", b"BC", b"DE", b"FINAL"])
        log.seek(0)
        comprobar("Recibido: ABCDE" in log.read(), "recvall reconstruye ABCDE a partir de tres envios")
        cliente("tcp_cliente2_sendall.py", 20103)
        time.sleep(0.1)


def experimento_abcd():
    with servidor("tcp_servidor1_simple.py", 20104, 1):
        print("Cinco mensajes ABCD: 20 bytes antes de FINAL.")
        enviar_trozos(20104, [b"ABCD" * 5 + b"FINAL"], espera=1.2)
    with servidor("tcp_servidor2_recvall.py", 20105, 1) as log:
        print("Tres mensajes ABCD: 12 bytes antes de FINAL.")
        enviar_trozos(20105, [b"ABCD" * 3 + b"FINAL"], espera=1.2)
        log.seek(0)
        salida = log.read()
        comprobar("CDFIN" in salida and "Recibido FINAL" not in salida,
                  "la marca FINAL queda partida y no se reconoce")


def ejercicio3():
    with servidor("tcp_servidor3_oche_simplista.py", 20106):
        r = cliente("tcp_cliente3_oche.py", 20106)
        comprobar(all(x in r.stdout for x in ["ONU", "SOD", "SERT"]),
                  "la version simplista funciona con envios y respuestas intercalados")


def experimento_oche():
    with servidor("tcp_servidor3_oche_simplista.py", 20107, 1):
        r = cliente("tcp_cliente3_oche_envia_seguido.py", 20107, esperado=1)
        comprobar("SERT\\n\\rSOD\\n\\rONU" in r.stdout and "Timeout" in r.stdout,
                  "un solo recv agrupa las tres lineas y el siguiente agota el plazo")


def probar_lineas(puerto):
    mensajes = ["mañana", "X" * 160, ""]
    with socket.create_connection(("127.0.0.1", puerto), timeout=5) as s, s.makefile("rb") as f:
        datos = b"".join((m + "\r\n").encode("utf8") for m in mensajes)
        # Se parte la representación multibyte de la ñ entre dos escrituras.
        posicion = datos.index(b"\xc3") + 1
        s.sendall(datos[:posicion])
        time.sleep(0.12)
        s.sendall(datos[posicion:])
        for mensaje in mensajes:
            r = f.readline()
            comprobar(r == (mensaje[::-1] + "\r\n").encode("utf8"),
                      "respuesta correcta: %d caracteres, %d bytes" % (len(mensaje), len(mensaje.encode("utf8"))))


def ejercicio4():
    with servidor("tcp_servidor4_oche_mejorado.py", 20108, 1):
        cliente("tcp_cliente4_oche_mejorado.py", 20108)
        probar_lineas(20108)


def ejercicio5():
    with servidor("tcp_servidor5_oche_readline.py", 20109, 1):
        cliente("tcp_cliente5_oche_readline.py", 20109)
        probar_lineas(20109)


def ejercicio6():
    with servidor("tcp_servidor6_oche_len.py", 20110):
        r = cliente("tcp_cliente6_oche_len.py", 20110)
        comprobar("anañam" in r.stdout and "dos" in r.stdout and "''" in r.stdout,
                  "se aceptan UTF-8, saltos de linea internos y mensaje vacio")
        with socket.create_connection(("127.0.0.1", 20110), timeout=5) as s, s.makefile("rb") as f:
            for parte in [b"7", b"\nma\xc3", b"\xb1ana"]:
                print("Fragmento enviado:", repr(parte))
                s.sendall(parte)
                time.sleep(0.1)
            n = int(f.readline())
            respuesta = f.read(n)
            comprobar(respuesta.decode("utf8") == "anañam", "se reconstruyen cabecera y cuerpo fragmentados")


def ejercicio7():
    for formato in [">H", "<H"]:
        print("struct.pack(%r, 15) = %r" % (formato, struct.pack(formato, 15)))
    print("struct.unpack('>H', b'\\x00\\x10') =", struct.unpack(">H", b"\x00\x10"))
    with servidor("tcp_servidor7_opcional.py", 20111):
        r = cliente("tcp_cliente7_opcional.py", 20111, entrada="mañana\n")
        comprobar("anañam" in r.stdout, "el cliente y servidor existentes invierten UTF-8 correctamente")
        with socket.create_connection(("127.0.0.1", 20111), timeout=5) as s:
            for parte in [b"\x00", b"\x07ma\xc3", b"\xb1ana"]:
                print("Fragmento enviado:", repr(parte))
                s.sendall(parte)
                time.sleep(0.1)
            with s.makefile("rb") as f:
                n = struct.unpack(">H", f.read(2))[0]
                comprobar(f.read(n).decode("utf8") == "anañam", "recvall tolera cabecera binaria y UTF-8 fragmentados")
    try:
        struct.pack(">H", 65536)
    except struct.error:
        print("CORRECTO: >H admite longitudes de 0 a 65535, no 65536.")


def lanzar_docker(publicar=False):
    r = subprocess.run(["docker", "inspect", NOMBRE], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    comprobar(r.returncode != 0, "el nombre del contenedor esta disponible")
    args = ["docker", "run", "-d", "--rm", "--name", NOMBRE, "--network", "pruebas"]
    if publicar:
        args += ["-p", "9090:9999"]
    args += ["-v", str(BASE) + ":/app:ro", "python:3.7", "python", "-u", "/app/tcp_servidor5_oche_readline.py"]
    ejecutar(args)
    CONTENEDORES.append(NOMBRE)
    time.sleep(0.3)


def detener_docker():
    ejecutar(["docker", "stop", "-t", "1", NOMBRE])
    r = subprocess.run(["docker", "inspect", NOMBRE], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    comprobar(r.returncode != 0, "--rm elimina el contenedor tras detenerlo")
    CONTENEDORES.remove(NOMBRE)


def docker_interno():
    lanzar_docker()
    ejecutar(["docker", "run", "--rm", "--network", "pruebas", "-v", str(BASE) + ":/app:ro",
              "python:3.7", "python", "/app/tcp_cliente5_oche_readline.py", NOMBRE, "9999"])
    detener_docker()


def docker_publicado():
    lanzar_docker(True)
    ejecutar(["docker", "ps", "--filter", "name=" + NOMBRE,
              "--format", "{{.Names}} | {{.Ports}}"])
    cliente("tcp_cliente5_oche_readline.py", 9090, ip="localhost")
    if WINDOWS:
        archivo = EVIDENCIAS / "11_cliente_windows.txt"
        (EVIDENCIAS / ".esperando_windows").write_text("9090", encoding="utf8")
        print("Esperando la ejecucion real del cliente desde Windows...", flush=True)
        limite = time.monotonic() + 240
        while not archivo.exists():
            if time.monotonic() > limite:
                raise TimeoutError("No se recibio la evidencia externa de Windows")
            time.sleep(0.5)
        texto = archivo.read_text(encoding="utf8")
        print(texto, flush=True)
        comprobar(all(x in texto for x in ["ONU", "SOD", "SERT"]), "Windows accede al servicio publicado en Ubuntu:9090")
        (EVIDENCIAS / ".esperando_windows").unlink()
    else:
        print("La comprobacion desde Windows se realiza aparte con --esperar-windows.")


def docker_otra_red():
    red = "is14_externa_verificacion"
    r = subprocess.run(["docker", "network", "inspect", red], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    comprobar(r.returncode != 0, "la red temporal no existia")
    ejecutar(["docker", "network", "create", red])
    REDES.append(red)
    codigo = "import socket; print('IP del cliente en otra red:',socket.gethostbyname(socket.gethostname()))"
    ejecutar(["docker", "run", "--rm", "--network", red, "python:3.7", "python", "-c", codigo])
    ip_host = ejecutar(["hostname", "-I"], mostrar=False).stdout.split()[0]
    ejecutar(["docker", "run", "--rm", "--network", red, "-v", str(BASE) + ":/app:ro", "python:3.7",
              "python", "/app/tcp_cliente5_oche_readline.py", ip_host, "9090"])
    print("Se prueba otra subred Docker en la misma VM; Windows aporta la prueba entre equipos.")
    detener_docker()


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


def bloque(nombre, titulo, funcion):
    if PAUSA:
        print("\033[2J\033[H", end="", flush=True)
    with (EVIDENCIAS / (nombre + ".txt")).open("w", encoding="utf8") as archivo:
        with contextlib.redirect_stdout(Duplicar(sys.stdout, archivo)):
            print("INGENIERIA DE SERVICIOS | Practica 1.4 | " + titulo + "\n", flush=True)
            funcion()
            print("\nBLOQUE VERIFICADO: " + nombre, flush=True)
    RESULTADOS[nombre] = "correcto"
    (EVIDENCIAS / "resultados.json").write_text(json.dumps({
        "fecha": datetime.datetime.now().astimezone().isoformat(), "bloques": RESULTADOS},
        ensure_ascii=False, indent=2), encoding="utf8")
    if PAUSA:
        (EVIDENCIAS / ".captura_lista").write_text(nombre, encoding="utf8")
        input("Captura preparada. Pulsa Intro para continuar...")
        (EVIDENCIAS / ".captura_lista").unlink(missing_ok=True)


def main():
    global PAUSA, WINDOWS
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capturas", action="store_true")
    parser.add_argument("--esperar-windows", action="store_true")
    args = parser.parse_args()
    PAUSA, WINDOWS = args.capturas, args.esperar_windows
    EVIDENCIAS.mkdir(parents=True, exist_ok=True)
    if WINDOWS:
        (EVIDENCIAS / "11_cliente_windows.txt").unlink(missing_ok=True)
    pasos = [
        ("00_entorno", "Entorno", entorno),
        ("01_bloques_fijos", "Ejercicio 1 Bloques de cinco bytes", ejercicio1),
        ("02_recvall", "Ejercicio 2 Fragmentacion del flujo", ejercicio2),
        ("03_abcd", "Experimento ABCD y alineacion", experimento_abcd),
        ("04_oche_simple", "Ejercicio 3 OCHE simplista", ejercicio3),
        ("05_lineas_agrupadas", "Experimento Tres lineas juntas", experimento_oche),
        ("06_delimitador", "Ejercicio 4 Lectura byte a byte", ejercicio4),
        ("07_readline", "Ejercicio 5 Readline", ejercicio5),
        ("08_longitud_ascii", "Ejercicio 6 Longitud ASCII", ejercicio6),
        ("09_longitud_binaria", "Ejercicio 7 Longitud binaria", ejercicio7),
        ("10_docker_interno", "Docker Red privada y nombre DNS", docker_interno),
        ("11_puerto_publicado", "Docker Puerto publicado 9090", docker_publicado),
        ("12_otra_subred", "Docker Cliente desde otra subred", docker_otra_red),
    ]
    try:
        for nombre, titulo, funcion in pasos:
            bloque(nombre, titulo, funcion)
        print("Los trece bloques de verificacion han terminado correctamente.")
    finally:
        for nombre in CONTENEDORES:
            subprocess.run(["docker", "rm", "-f", nombre], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for nombre in REDES:
            subprocess.run(["docker", "network", "rm", nombre], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for nombre in [".captura_lista", ".esperando_windows"]:
            (EVIDENCIAS / nombre).unlink(missing_ok=True)


if __name__ == "__main__":
    main()
