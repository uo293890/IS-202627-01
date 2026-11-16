#!/usr/bin/env python3
"""Comprueba contenedores detenidos y ping mediante el DNS de Docker."""
import contextlib
import subprocess
import sys
import verificar_practica as v

v.EVIDENCIAS.mkdir(parents=True, exist_ok=True)
nombre = v.PREFIJO + "ciclo"
with (v.EVIDENCIAS / "12_ciclo_y_ping.txt").open("w", encoding="utf-8") as log:
    with contextlib.redirect_stdout(v.Duplicar(sys.stdout, log)):
        print("\033[2J\033[H", end="")
        print("INGENIERIA DE SERVICIOS | Practica 1.3 | Ciclo de vida y ping\n")
        try:
            r = subprocess.run(["docker", "inspect", nombre], stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL)
            v.comprobar(r.returncode != 0, "el contenedor de prueba no existia")
            v.CONTENEDORES.append(nombre)
            v.ejecutar(["docker", "run", "--name", nombre, "python:3.7"])
            v.ejecutar(["docker", "ps", "-a", "--filter", "name=" + nombre,
                        "--format", "{{.Names}} | {{.Status}}"])
            v.comprobar(True, "python sin entrada termina y el contenedor queda detenido")
            v.ejecutar(["docker", "rm", nombre])
            servidor = v.lanzar_docker("ping", "udp_servidor3_con_ok.py", "pruebas")
            r = v.ejecutar(["docker", "run", "--rm", "--network", "pruebas", "python:3.7",
                            "bash", "-c", "apt-get update -qq && apt-get install -y -qq iputils-ping && ping -c 2 " + servidor],
                           mostrar=False, limite=180)
            print("Salida de ping (se omiten los mensajes de instalacion):")
            print("\n".join(r.stdout.splitlines()[-8:]))
            v.comprobar("2 received" in r.stdout and "0% packet loss" in r.stdout,
                        "el nombre del servidor se resuelve y responde a dos paquetes ICMP")
            print("\nBLOQUE VERIFICADO: 12_ciclo_y_ping")
        finally:
            for contenedor in v.CONTENEDORES:
                subprocess.run(["docker", "rm", "-f", contenedor],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
