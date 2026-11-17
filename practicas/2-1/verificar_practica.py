#!/usr/bin/env python3
"""Verificación de Nginx, Flask, Gunicorn y MariaDB.

--capturas pausa entre bloques. --apt incluye la comprobación manual de
instalación y retirada de Nginx en Ubuntu y requiere --capturas.
--mantener conserva los tres contenedores de la arquitectura final.
"""
import argparse
import contextlib
import datetime
import http.client
import io
import json
import os
from pathlib import Path
import platform
import shlex
import signal
import socket
import subprocess
import sys
import time

BASE = Path(__file__).resolve().parent
EVIDENCIAS = BASE / 'memoria/evidencias'
VENV = Path.home() / 'flaskenv/bin'
CONTENEDORES = []
PROCESOS = []
RESULTADOS = {}
PAUSA = False
IMAGEN = 'gunicornflask:1.0'
CLAVE = 'claveroot'  # Credencial de laboratorio del guion; solo para esta prueba.
DB_FINAL = 'is21_mariadb_persistente'


def ejecutar(args, esperado=0, mostrar=True, limite=60, cwd=BASE):
    print('$ ' + shlex.join(str(x) for x in args), flush=True)
    r = subprocess.run(args, cwd=cwd, text=True, stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT, timeout=limite)
    if mostrar:
        print(r.stdout.rstrip(), flush=True)
    assert r.returncode == esperado, (r.returncode, r.stdout)
    return r


def comprobar(condicion, texto):
    assert condicion, texto
    print('CORRECTO: ' + texto, flush=True)


def peticion(url, esperado=200, mostrar=True):
    from urllib.parse import urlsplit
    u = urlsplit(url)
    c = http.client.HTTPConnection(u.hostname, u.port or 80, timeout=8)
    c.request('GET', u.path or '/', headers={'User-Agent': 'IS21-Verificacion'})
    r = c.getresponse()
    cuerpo = r.read()
    cabeceras = dict(r.getheaders())
    if mostrar:
        print('GET', url, '->', r.status)
        for clave in ('Server', 'Content-Type', 'Content-Length'):
            if clave in cabeceras:
                print(clave + ':', cabeceras[clave])
        texto = cuerpo.decode('utf8', errors='replace')
        print('Cuerpo:', repr(texto[:180]))
    comprobar(r.status == esperado, 'estado HTTP ' + str(esperado))
    c.close()
    return cuerpo, cabeceras


def esperar_http(puerto):
    limite = time.monotonic() + 30
    while time.monotonic() < limite:
        try:
            c = http.client.HTTPConnection('127.0.0.1', puerto, timeout=1)
            c.request('GET', '/')
            r = c.getresponse()
            r.read()
            c.close()
            if r.status == 200:
                return
        except (OSError, http.client.HTTPException):
            time.sleep(0.2)
    raise TimeoutError('No arranca el puerto ' + str(puerto))


def cerrado(puerto):
    with socket.socket() as s:
        s.settimeout(0.5)
        comprobar(s.connect_ex(('127.0.0.1', puerto)) != 0,
                  'no hay un servicio publicado en localhost:' + str(puerto))


def lanzar(args):
    nombre = args[args.index('--name') + 1]
    r = subprocess.run(['docker', 'inspect', nombre], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    comprobar(r.returncode != 0, 'nombre disponible: ' + nombre)
    ejecutar(['docker', 'run', '-d', '--rm', *args])
    CONTENEDORES.append(nombre)
    return nombre


def detener(nombre):
    ejecutar(['docker', 'stop', '-t', '2', nombre])
    if nombre in CONTENEDORES:
        CONTENEDORES.remove(nombre)


def proceso(args, nombre):
    print('$ ' + shlex.join(str(x) for x in args), flush=True)
    log = (EVIDENCIAS / (nombre + '_servidor.log')).open('w', encoding='utf8')
    p = subprocess.Popen(args, cwd=BASE / 'hola_flask', stdout=log,
                         stderr=subprocess.STDOUT, start_new_session=True)
    PROCESOS.append((p, log))
    esperar_http(5000)
    comprobar(p.poll() is None, nombre + ' permanece en ejecucion')
    return p


def parar_procesos():
    for p, log in PROCESOS:
        if p.poll() is None:
            os.killpg(p.pid, signal.SIGTERM)
            try:
                p.wait(8)
            except subprocess.TimeoutExpired:
                os.killpg(p.pid, signal.SIGKILL)
                p.wait()
        log.close()
    PROCESOS.clear()


def entorno():
    ejecutar(['date', '--iso-8601=seconds'])
    print('Equipo:', platform.node(), 'Python:', platform.python_version())
    ejecutar(['docker', 'version', '--format', 'Cliente {{.Client.Version}} Servidor {{.Server.Version}}'])
    ejecutar(['docker', 'images', '--format', '{{.Repository}}:{{.Tag}} | {{.Size}}', 'nginx'])
    ejecutar(['docker', 'images', '--format', '{{.Repository}}:{{.Tag}} | {{.Size}}', 'mariadb'])
    ejecutar(['docker', 'network', 'inspect', 'pruebas', '--format', '{{range .IPAM.Config}}{{.Subnet}}{{end}}'])


def nginx_apt():
    ejecutar(['nginx', '-v'])
    r = ejecutar(['nginx', '-V'], mostrar=False)
    (EVIDENCIAS / '01_nginx_compilacion.txt').write_text(r.stdout, encoding='utf8')
    ejecutar(['systemctl', 'is-active', 'nginx'])
    ejecutar(['ss', '-ltn', '( sport = :80 )'])
    print('Configuracion de Ubuntu:')
    for linea in Path('/etc/nginx/sites-enabled/default').read_text().splitlines():
        if 'root /var/www/html' in linea:
            print(linea.strip())
    cuerpo, _ = peticion('http://127.0.0.1/')
    comprobar(b'IS21_RAIZ_VAR_WWW' in cuerpo, 'el cambio de /var/www/html se ve por HTTP')
    print('Ultimas peticiones del registro:')
    print('\n'.join(Path('/var/log/nginx/access.log').read_text().splitlines()[-3:]))
    print('Antes del bloque siguiente, restaurar el indice y retirar los paquetes nginx de Ubuntu.')


def nginx_retirado():
    r = subprocess.run(['dpkg-query', '-W', '-f=${db:Status-Abbrev}', 'nginx'],
                       text=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    print('Estado del paquete nginx:', repr(r.stdout.strip()))
    comprobar(not r.stdout.startswith('ii'), 'nginx ya no esta instalado con apt')
    cerrado(80)
    ejecutar(['ss', '-ltn', '( sport = :80 )'])


def nginx_privado():
    n = lanzar(['--name', 'is21_nginx_inicial', '--network', 'pruebas', 'nginx'])
    ip = ejecutar(['docker', 'inspect', n, '--format',
                  '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}'], mostrar=False).stdout.strip()
    print('IP privada de nginx:', ip)
    cuerpo, _ = peticion('http://' + ip + '/', mostrar=False)
    comprobar(b'Welcome to nginx!' in cuerpo, 'se recibe la pagina incluida en la imagen')
    (EVIDENCIAS / 'nginx_index_original.html').write_bytes(cuerpo)
    pagina_error, _ = peticion('http://' + ip + '/50x.html', mostrar=False)
    destino = BASE / 'html/50x.html'
    if destino.exists():
        comprobar(destino.read_bytes() == pagina_error, '50x.html coincide con la imagen')
    else:
        destino.write_bytes(pagina_error)
        print('Guardado html/50x.html desde la imagen de nginx.')
    r = ejecutar(['docker', 'exec', n, 'nginx', '-T'], mostrar=False)
    print('\n'.join(x.strip() for x in r.stdout.splitlines() if 'root ' in x or 'listen ' in x)[:700])
    ejecutar(['docker', 'exec', n, 'nginx', '-v'])
    cerrado(80)
    detener(n)


def sitios():
    r = subprocess.run(['docker', 'inspect', 'servidor_nginx'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    comprobar(r.returncode != 0, 'servidor_nginx no pertenece a otra ejecucion')
    ejecutar(['bash', 'lanzar_nginx.sh'])
    CONTENEDORES.append('servidor_nginx')
    esperar_http(80)
    esperar_http(81)
    for puerto, marca in [(80, b'sitio 1'), (81, b'sitio 2')]:
        cuerpo, _ = peticion('http://127.0.0.1:' + str(puerto) + '/')
        comprobar(marca in cuerpo, 'contenido propio del sitio en el puerto ' + str(puerto))
    peticion('http://127.0.0.1/noexisto', 404)
    peticion('http://127.0.0.1/50x.html')
    r = ejecutar(['docker', 'logs', 'servidor_nginx'], mostrar=False)
    print('Log del contenedor:\n' + '\n'.join(r.stdout.splitlines()[-4:]))


def seguridad():
    ejecutar(['docker', 'exec', 'servidor_nginx', 'nginx', '-t'])
    conf = ejecutar(['docker', 'exec', 'servidor_nginx', 'nginx', '-T'], mostrar=False).stdout
    claves = ['server_tokens', 'client_max_body_size', 'client_header_timeout',
              'client_body_timeout', 'keepalive_timeout', 'send_timeout']
    print('\n'.join(x.strip() for x in conf.splitlines() if not x.lstrip().startswith('#') and any(k in x for k in claves)))
    _, cabeceras = peticion('http://127.0.0.1/noexisto', 404, mostrar=False)
    comprobar(cabeceras.get('Server') == 'nginx', 'la cabecera Server no incluye la version')
    c = http.client.HTTPConnection('127.0.0.1', 80, timeout=5)
    c.putrequest('POST', '/')
    c.putheader('Content-Length', str(4096 * 1024 + 1))
    c.endheaders()
    r = c.getresponse()
    print('Solicitud con Content-Length mayor de 4096k ->', r.status)
    comprobar(r.status == 413, 'se rechaza un cuerpo que supera el limite configurado')
    c.close()


def flask_desarrollo():
    ejecutar([str(VENV / 'python'), '-c',
              "import flask; from importlib.metadata import version; print('Flask',version('flask')); print(flask.__file__)"])
    proceso([str(VENV / 'flask'), '--app', 'hola_flask', 'run', '--host=0.0.0.0',
             '--port=5000', '--no-reload'], '06_flask_desarrollo')
    cuerpo, _ = peticion('http://127.0.0.1:5000/')
    comprobar(b'<i>' in cuerpo and 'Flask' in cuerpo.decode(), 'la respuesta es HTML con cursiva')


def gunicorn_host():
    parar_procesos()
    p = proceso([str(VENV / 'gunicorn'), '-b', '0.0.0.0:5000', '-w', '4', 'hola_flask:app'], '07_gunicorn')
    peticion('http://127.0.0.1:5000/')
    limite = time.monotonic() + 10
    while time.monotonic() < limite:
        estado = subprocess.run(['ps', '--ppid', str(p.pid), '-o', 'pid,args'],
                                text=True, stdout=subprocess.PIPE)
        if len(estado.stdout.strip().splitlines()) == 5:
            break
        time.sleep(0.1)
    r = ejecutar(['ps', '--ppid', str(p.pid), '-o', 'pid,args'])
    comprobar(len(r.stdout.strip().splitlines()) == 5, 'el proceso maestro tiene cuatro workers')


def construir():
    parar_procesos()
    r = ejecutar(['docker', 'build', '-t', IMAGEN, '.'], mostrar=False, limite=240)
    (EVIDENCIAS / '08_build_detalle.txt').write_text(r.stdout, encoding='utf8')
    print('Construccion inicial:\n' + '\n'.join(r.stdout.splitlines()[-8:]))
    r = ejecutar(['docker', 'build', '-t', IMAGEN, '.'], mostrar=False, limite=120)
    print('Segunda construccion: pasos CACHED =', r.stdout.count('CACHED'))
    (EVIDENCIAS / '08_build_cache.txt').write_text(r.stdout, encoding='utf8')
    comprobar('CACHED' in r.stdout, 'la segunda construccion reutiliza las capas')
    lanzar(['--name', 'is21_flask_publicado', '--network', 'pruebas', '-p', '5050:5000', IMAGEN])
    esperar_http(5050)
    peticion('http://127.0.0.1:5050/')
    ejecutar(['docker', 'ps', '--filter', 'name=is21_flask_publicado', '--format', '{{.Names}} | {{.Ports}}'])


def proxy():
    # Al reanudar tras reiniciar la VM, --rm puede haberlo eliminado.
    existe = subprocess.run(['docker', 'inspect', 'is21_flask_publicado'],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if existe.returncode == 0:
        detener('is21_flask_publicado')
    lanzar(['--name', 'hola-flask', '--network', 'pruebas', IMAGEN])
    limite = time.monotonic() + 25
    while True:
        try:
            cuerpo, _ = peticion('http://127.0.0.1/hola', mostrar=False)
            break
        except (OSError, AssertionError):
            if time.monotonic() > limite:
                raise
            time.sleep(0.4)
    comprobar(b'<i>' in cuerpo, '/hola devuelve el HTML de Flask')
    peticion('http://127.0.0.1/hola/')
    a, _ = peticion('http://127.0.0.1/noexisto', 404, mostrar=False)
    b, _ = peticion('http://127.0.0.1/hola/mundo', 404)
    comprobar(b'nginx' in a and b'was not found' in b and a != b, 'se distinguen los 404 de Nginx y de Flask')
    cerrado(5000)
    cerrado(5050)
    ejecutar(['docker', 'ps', '--format', '{{.Names}} | {{.Ports}}'])


def iniciar_db(nombre, persistente=False):
    args = ['--name', nombre, '--network', 'pruebas', '-e', 'MARIADB_ROOT_PASSWORD=' + CLAVE]
    if persistente:
        args += ['--network-alias', 'mariadb', '-v', str(BASE / 'basedatos_verificacion') + ':/var/lib/mysql']
    lanzar([*args, 'mariadb'])
    limite = time.monotonic() + 150
    while time.monotonic() < limite:
        r = subprocess.run(['docker', 'exec', '-e', 'MYSQL_PWD=' + CLAVE, nombre,
                            'mariadb-admin', '--protocol=tcp', '-h', '127.0.0.1', '-u', 'root', 'ping', '--silent'],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if r.returncode == 0:
            return
        time.sleep(1)
    raise TimeoutError('MariaDB no acepta conexiones TCP')


def sql(nombre, consulta):
    return ejecutar(['docker', 'run', '--rm', '--network', 'pruebas', '-e', 'MYSQL_PWD=' + CLAVE,
                     'mariadb', 'mariadb', '--host', nombre, '--user', 'root', '--batch',
                     '--skip-column-names', '--execute', consulta], limite=30)


def mariadb_temporal():
    n = 'is21_mariadb_temporal'
    iniciar_db(n)
    sql(n, 'SELECT VERSION(); SHOW DATABASES; CREATE DATABASE practica21_temporal;')
    ejecutar(['docker', 'top', n])
    cerrado(3306)
    detener(n)
    iniciar_db(n)
    r = sql(n, "SELECT SCHEMA_NAME FROM information_schema.SCHEMATA WHERE SCHEMA_NAME='practica21_temporal';")
    comprobar(not r.stdout.strip(), 'la nueva instancia sin bind mount no conserva la base temporal')
    detener(n)


def persistencia():
    iniciar_db(DB_FINAL, True)
    marca = 'IS21_' + datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    sql(DB_FINAL, "CREATE DATABASE IF NOT EXISTS practica21; USE practica21; "
        "CREATE TABLE IF NOT EXISTS evidencia (id INT PRIMARY KEY, texto VARCHAR(80)); "
        "INSERT INTO evidencia VALUES (1,'%s') ON DUPLICATE KEY UPDATE texto=VALUES(texto); SELECT * FROM evidencia;" % marca)
    ejecutar(['docker', 'inspect', DB_FINAL, '--format', '{{range .Mounts}}{{.Type}} | {{.Source}} -> {{.Destination}}{{end}}'])
    detener(DB_FINAL)
    iniciar_db(DB_FINAL, True)
    r = sql(DB_FINAL, 'SELECT * FROM practica21.evidencia;')
    comprobar(marca in r.stdout, 'la fila sigue presente tras eliminar y recrear el contenedor')
    ejecutar(['ls', '-ld', str(BASE / 'basedatos_verificacion')])


def final():
    ejecutar(['docker', 'ps', '--format', '{{.Names}} | {{.Image}} | {{.Ports}}'])
    for url in ['http://127.0.0.1/', 'http://127.0.0.1:81/', 'http://127.0.0.1/hola']:
        peticion(url)
    sql(DB_FINAL, 'SELECT * FROM practica21.evidencia;')
    cerrado(3306)
    print('Nginx sirve estaticos y actua como proxy; Flask y MariaDB usan la red pruebas.')


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
        print('\033[2J\033[H', end='', flush=True)
    with (EVIDENCIAS / (nombre + '.txt')).open('w', encoding='utf8') as archivo:
        with contextlib.redirect_stdout(Duplicar(sys.stdout, archivo)):
            print('INGENIERIA DE SERVICIOS | Practica 2.1 | ' + titulo + '\n')
            funcion()
            print('\nBLOQUE VERIFICADO: ' + nombre, flush=True)
    RESULTADOS[nombre] = 'correcto'
    (EVIDENCIAS / 'resultados.json').write_text(json.dumps({
        'fecha': datetime.datetime.now().astimezone().isoformat(), 'bloques': RESULTADOS},
        ensure_ascii=False, indent=2), encoding='utf8')
    if PAUSA:
        (EVIDENCIAS / '.captura_lista').write_text(nombre, encoding='utf8')
        input('Captura preparada. Pulsa Intro para continuar...')
        (EVIDENCIAS / '.captura_lista').unlink(missing_ok=True)


def main():
    global PAUSA
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--capturas', action='store_true')
    p.add_argument('--apt', action='store_true')
    p.add_argument('--mantener', action='store_true')
    p.add_argument('--desde', help='reanudar a partir del identificador de un bloque')
    args = p.parse_args()
    if args.apt and not args.capturas:
        p.error('--apt requiere --capturas para retirar el servicio entre los bloques 01 y 02')
    PAUSA = args.capturas
    EVIDENCIAS.mkdir(parents=True, exist_ok=True)
    if args.desde and (EVIDENCIAS / 'resultados.json').exists():
        RESULTADOS.update(json.loads((EVIDENCIAS / 'resultados.json').read_text())['bloques'])
    pasos = [('00_entorno', 'Entorno', entorno)]
    if args.apt:
        pasos += [('01_nginx_apt', 'Nginx instalado en Ubuntu', nginx_apt),
                  ('02_nginx_retirado', 'Retirada del servicio de Ubuntu', nginx_retirado)]
    pasos += [
        ('03_nginx_privado', 'Nginx en una red privada', nginx_privado),
        ('04_dos_sitios', 'Dos sitios y pagina 404', sitios),
        ('05_configuracion', 'Configuracion opcional de Nginx', seguridad),
        ('06_flask', 'Flask en el entorno virtual', flask_desarrollo),
        ('07_gunicorn', 'Gunicorn con cuatro workers', gunicorn_host),
        ('08_imagen_flask', 'Construccion y publicacion en 5050', construir),
        ('09_proxy', 'Nginx como proxy inverso', proxy),
        ('10_mariadb_temporal', 'MariaDB sin almacenamiento propio', mariadb_temporal),
        ('11_persistencia', 'Persistencia tras recrear MariaDB', persistencia),
        ('12_arquitectura', 'Arquitectura final', final),
    ]
    terminado = False
    if args.desde:
        nombres = [x[0] for x in pasos]
        if args.desde not in nombres:
            p.error('bloque no encontrado: ' + args.desde)
        pasos = pasos[nombres.index(args.desde):]
    try:
        for nombre, titulo, funcion in pasos:
            bloque(nombre, titulo, funcion)
        terminado = True
        print('Todos los bloques de verificacion han terminado correctamente.')
    finally:
        parar_procesos()
        conservar = {'servidor_nginx', 'hola-flask', DB_FINAL} if terminado and args.mantener else set()
        for nombre in CONTENEDORES:
            if nombre not in conservar:
                subprocess.run(['docker', 'rm', '-f', nombre], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        (EVIDENCIAS / '.captura_lista').unlink(missing_ok=True)


if __name__ == '__main__':
    main()
