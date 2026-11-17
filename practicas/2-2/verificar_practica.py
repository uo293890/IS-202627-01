#!/usr/bin/env python3
"""Pruebas reales de Amigos sobre una base de laboratorio independiente.

Requiere basedatos en pruebas, con amigosdb/amigosuser del guion,
montado EXCLUSIVAMENTE en basedatos_verificacion, y ~/flaskenv.
--preparar ejecuta las pruebas de esquema sobre una base vacia.
--capturas pausa tras cada bloque; --desde permite reanudar.
Los tres servicios finales quedan activos para revisarlos.
"""
import argparse
import contextlib
import datetime
import http.client as cliente_http
import io
import json
import os
from pathlib import Path
import shlex
import socket
import subprocess
import sys
import tempfile
import textwrap
import time
from urllib.parse import urlencode

BASE = Path(__file__).resolve().parent
APP = BASE / 'amigos'
EV = BASE / 'memoria/evidencias'
VENV = Path.home() / 'flaskenv/bin'
ENV = dict(os.environ, DEPLOYMENT_MODE='production')
PROCESO = None
LOG = None
RESULTADOS = {}
PAUSA = False


def run(args, cwd=APP, env=None, timeout=120, corto=False):
    print('$ ' + shlex.join(map(str, args)), flush=True)
    r = subprocess.run(args, cwd=cwd, env=env or ENV, text=True,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout)
    print(('\n'.join(r.stdout.splitlines()[-12:]) if corto else r.stdout).rstrip(), flush=True)
    assert r.returncode == 0, r.stdout
    return r.stdout


def ok(condicion, mensaje):
    assert condicion, mensaje
    print('CORRECTO: ' + mensaje, flush=True)


def py(codigo):
    return run([str(VENV/'python'), '-c',
                'from lanzar import app\nfrom app import db\nfrom app.models import Amigo\n'
                'from sqlalchemy import inspect, text, insert, select\nwith app.app_context():\n'
                + textwrap.indent(textwrap.dedent(codigo).strip(), '    ')])


def sql(consulta):
    return run(['docker', 'run', '--rm', '--network', 'pruebas', '-e', 'MYSQL_PWD=amigospass',
                'mariadb', 'mariadb', '-h', 'basedatos', '-u', 'amigosuser', 'amigosdb',
                '--batch', '--skip-column-names', '--execute', consulta])


def http(metodo, ruta, datos=None, form=None, esperado=200, puerto=5000, bruto=None):
    headers = {}
    cuerpo = None
    if datos is not None:
        cuerpo = json.dumps(datos)
        headers['Content-Type'] = 'application/json'
    if form is not None:
        cuerpo = urlencode(form)
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
    if bruto is not None:
        cuerpo = bruto
    c = cliente_http.HTTPConnection('127.0.0.1', puerto, timeout=15)
    c.request(metodo, ruta, body=cuerpo, headers=headers)
    r = c.getresponse()
    body = r.read().decode('utf8')
    print(f'{metodo} :{puerto}{ruta} -> {r.status}; Content-Type: {r.getheader("Content-Type")}')
    if r.getheader('Location'):
        print('Location:', r.getheader('Location'))
    if datos is not None:
        print('JSON enviado:', repr(datos)[:160])
    print('Cuerpo:', repr(body)[:230])
    ok(r.status == esperado, 'estado HTTP ' + str(esperado))
    c.close()
    return json.loads(body) if body and 'application/json' in (r.getheader('Content-Type') or '') else body


def esperar(puerto, ruta='/html/amigos'):
    for _ in range(100):
        try:
            c = cliente_http.HTTPConnection('127.0.0.1', puerto, timeout=1)
            c.request('GET', ruta)
            r = c.getresponse(); r.read(); c.close()
            if r.status == 200:
                return
        except (OSError, cliente_http.HTTPException):
            pass
        time.sleep(.2)
    raise TimeoutError('Servicio no disponible: ' + str(puerto))


def cerrado(puerto):
    with socket.socket() as s:
        s.settimeout(.5)
        ok(s.connect_ex(('127.0.0.1', puerto)) != 0, 'puerto anfitrion sin publicar: ' + str(puerto))


def entorno():
    run(['date', '--iso-8601=seconds'])
    run(['hostname', '-I'])
    run([str(VENV/'python'), '-c', "from importlib.metadata import version\nfor p in ['flask','flask-sqlalchemy','flask-migrate','pymysql','httpie','gunicorn']: print(p,version(p))"])
    run(['docker', 'version', '--format', '{{.Server.Version}}'])
    ok(Path(BASE/'basedatos_verificacion').is_dir(), 'almacenamiento de pruebas independiente')


def base_vacia():
    info = json.loads(subprocess.check_output(['docker', 'inspect', 'basedatos']))[0]
    run(['docker', 'inspect', 'basedatos', '--format', '{{range .Mounts}}{{.Source}} -> {{.Destination}}{{end}}'])
    # Fallar antes de hacer downgrade o insertar si alguien monta su base anterior.
    mounts = [m for m in info['Mounts'] if m['Destination'] == '/var/lib/mysql']
    ok(len(mounts) == 1 and Path(mounts[0]['Source']).resolve() == (BASE/'basedatos_verificacion').resolve(),
       'basedatos usa exclusivamente basedatos_verificacion')
    tablas = sql('SHOW TABLES;')
    ok(not tablas.strip(), 'base nueva sin tablas; no se usa ninguna base anterior')
    cerrado(3306)


def inicial():
    run([str(VENV/'flask'), '--app', 'lanzar', 'db', 'upgrade', 'e753fcc1a838'])
    sql('SHOW TABLES; DESCRIBE amigos; SELECT version_num FROM alembic_version;')
    run([str(VENV/'flask'), '--app', 'lanzar', 'db', 'downgrade', 'base'])
    ok('amigos' not in sql('SHOW TABLES;').splitlines(), 'downgrade de la tabla vacia; sin datos que perder')
    run([str(VENV/'flask'), '--app', 'lanzar', 'db', 'upgrade', 'e753fcc1a838'])
    py('''
        db.session.execute(insert(Amigo).values(name='Manolito', lati='0', longi='0'))
        db.session.execute(insert(Amigo).values(name='Luis', lati='0', longi='0'))
        db.session.commit()
        print(db.session.execute(select(Amigo.id, Amigo.name, Amigo.lati, Amigo.longi)).all())
    ''')


def migracion_device():
    nuevas = list((APP/'migrations/versions').glob('*device*.py'))
    if not nuevas:
        run([str(VENV/'flask'), '--app', 'lanzar', 'db', 'migrate', '-m', 'anadir device a amigos'])
        nuevas = list((APP/'migrations/versions').glob('*device*.py'))
    ok(len(nuevas) == 1, 'una migracion incremental de device')
    contenido = nuevas[0].read_text()
    print(contenido)
    ok('drop_table' not in contenido and 'add_column' in contenido and 'device' in contenido,
       'la migracion agrega la columna sin borrar ni renombrar la tabla amigos')
    run([str(VENV/'flask'), '--app', 'lanzar', 'db', 'upgrade'])
    py('''
        amigos = Amigo.query.order_by(Amigo.id).all()
        assert [a.name for a in amigos] == ['Manolito', 'Luis']
        assert all(a.device is None for a in amigos)
        print([(repr(a), a.device) for a in amigos])
        print([(c['name'], str(c['type']), c['nullable']) for c in inspect(db.engine).get_columns('amigos')])
    ''')
    run([str(VENV/'flask'), '--app', 'lanzar', 'db', 'current'])
    py('''
        from alembic.migration import MigrationContext
        from alembic.autogenerate import compare_metadata
        with db.engine.connect() as conexion:
            diferencias = compare_metadata(MigrationContext.configure(conexion), db.metadata)
        print('Diferencias entre el esquema y el modelo:', diferencias)
        assert not diferencias
    ''')


def desarrollo():
    global PROCESO, LOG
    cerrado(5000)
    LOG = (EV/'04_flask_servidor.log').open('w')
    env = dict(ENV, DEPLOYMENT_MODE='development')
    args = [str(VENV/'flask'), '--app', 'lanzar', 'run', '--host=0.0.0.0', '--no-reload', '--no-debugger']
    print('$ ' + shlex.join(args))
    PROCESO = subprocess.Popen(args, cwd=APP, env=env, stdout=LOG, stderr=subprocess.STDOUT)
    esperar(5000)
    http('GET', '/html/amigos')
    http('GET', '/api/amigos')
    py("print('SELECT 1:', db.session.execute(text('SELECT 1')).scalar()); print(app.url_map)")


def formularios():
    http('GET', '/html/new_amigo/', esperado=200)
    http('POST', '/html/save_amigo', form={'id':'','name':'PruebaFormulario','lati':'43.36','longi':'-5.85','device':'movil-html'}, esperado=302)
    amigo = http('GET', '/api/amigo/byName/PruebaFormulario')
    ruta = '/html/edit_amigo/' + str(amigo['id'])
    body = http('GET', ruta)
    ok('movil-html' in body, 'formulario de edicion precargado')
    http('POST', '/html/save_amigo', form={'id':amigo['id'],'name':amigo['name'],'lati':'43.37','longi':'-5.86','device':''}, esperado=302)
    ok(http('GET', '/api/amigo/'+str(amigo['id']))['device'] == '', 'el formulario guarda el dispositivo vacio')
    http('POST', '/html/save_amigo', form={'name':'Manolito'}, esperado=422)
    http('POST', '/html/save_amigo', form={'name':''}, esperado=422)
    body = http('GET', '/html/edit_amigo/1')
    ok('>None<' not in body and 'value="None"' not in body, 'un dispositivo NULL se muestra como campo vacio')
    http('GET', '/html/delete_amigo/'+str(amigo['id']), esperado=302)
    http('GET', '/api/amigo/'+str(amigo['id']), esperado=404)


def lecturas_api():
    amigos = http('GET', '/api/amigos')
    ok(len(amigos) == 2, 'lista de dos amigos iniciales')
    http('GET', '/api/amigo/1')
    http('GET', '/api/amigo/byName/manolito')
    http('GET', '/api/amigo/999999', esperado=404)
    http('GET', '/api/amigo/byName/NoExisteIS22', esperado=404)
    run([str(VENV/'http'), '--ignore-stdin', '--pretty=none', 'GET', 'localhost:5000/api/amigo/1'])


def altas_api():
    a = http('POST', '/api/amigos', datos={'name':'Javier'})
    ok(a['lati'] == a['longi'] == '0' and a['device'] == '', 'valores predeterminados del nuevo amigo')
    http('POST', '/api/amigos', datos={'name':'Javier'}, esperado=422)
    http('POST', '/api/amigos', datos={'lati':'1'}, esperado=422)
    http('POST', '/api/amigos', datos={}, esperado=422)
    http('POST', '/api/amigos', bruto='sin JSON', esperado=422)
    http('POST', '/api/amigos', datos=['no es objeto'], esperado=422)
    http('POST', '/api/amigos', datos={'name':'N'*33}, esperado=422)
    http('POST', '/api/amigos', datos={'name':'TrasErrores','lati':'1','longi':'2'})


def dispositivos():
    a = http('GET', '/api/amigo/byName/Javier'); ruta = '/api/amigo/'+str(a['id'])
    http('PUT', ruta, datos={'lati':'12','device':'token-is22'})
    ok(http('GET','/api/devices') == ['token-is22'], 'devices excluye NULL y cadenas vacias')
    largo = 'X'*4096
    ok(len(http('PUT',ruta,datos={'device':largo})['device']) == 4096, 'se guardan y recuperan 4096 caracteres')
    http('PUT',ruta,datos={'device':'X'*4097},esperado=422)
    http('PUT',ruta,datos={'name':'Manolito'},esperado=422)
    http('PUT',ruta,datos={'name':''},esperado=422)
    http('PUT',ruta,datos={'device':''})
    ok(http('GET','/api/devices') == [], 'PUT con cadena vacia limpia el dispositivo')
    http('PUT',ruta,bruto='sin JSON',esperado=422)


def bajas_api():
    a=http('GET','/api/amigo/byName/TrasErrores'); ruta='/api/amigo/'+str(a['id'])
    ok(http('DELETE',ruta,esperado=204) == '', 'DELETE 204 sin cuerpo')
    http('DELETE',ruta,esperado=404)
    http('PUT','/api/amigo/999999',datos={'device':'x'},esperado=404)
    http('PATCH','/api/amigos',esperado=405)


def parar_desarrollo():
    global PROCESO, LOG
    if PROCESO is not None:
        PROCESO.terminate(); PROCESO.wait(15); PROCESO=None
    if LOG is not None:
        LOG.close(); LOG=None


def imagen():
    parar_desarrollo()
    # Conservar el tag previo antes de reconstruir la version del ejercicio.
    anterior=subprocess.run(['docker','image','inspect','amigos:2.0-anterior-is22'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    if anterior.returncode!=0:
        run(['docker','tag','amigos:2.0','amigos:2.0-anterior-is22'])
    out=run(['docker','build','-t','amigos:2.0','.'],corto=True,timeout=300)
    (EV/'10_build.txt').write_text(out)
    run(['docker','run','--rm','--entrypoint','python','amigos:2.0','-c',
         "import flask, sqlalchemy; from pathlib import Path; print('Flask',flask.__version__); print('SQLAlchemy',sqlalchemy.__version__); assert not Path('/amigos/instance/config.py').exists(); print('Imagen sin configuracion local de secretos')"])
    run(['docker','run','-d','--rm','--network','pruebas','--name','amigos',
         '-e','DEPLOYMENT_MODE=production','-e','DATABASE_URI=mysql+pymysql://amigosuser:amigospass@basedatos/amigosdb','amigos:2.0'])
    run(['docker','run','-d','--rm','--network','pruebas','--name','nginx','-p','80:80',
         '-v',str(BASE/'sitios_nginx')+':/etc/nginx/conf.d:ro','nginx'])
    esperar(80)
    http('GET','/html/amigos',puerto=80)
    http('GET','/api/amigos',puerto=80)
    cerrado(5000); cerrado(3306)
    run(['docker','top','amigos'])


def persistencia():
    anterior=http('GET','/api/amigos',puerto=80)
    run(['docker','stop','-t','10','basedatos'])
    run(['docker','run','-d','--rm','--name','basedatos','--network','pruebas',
         '-e','MYSQL_ROOT_PASSWORD=claveroot','-e','MYSQL_USER=amigosuser',
         '-e','MYSQL_DATABASE=amigosdb','-e','MYSQL_PASSWORD=amigospass',
         '-v',str(BASE/'basedatos_verificacion')+':/var/lib/mysql','mariadb'])
    # Reiniciar los workers renueva sus conexiones a la instancia recreada.
    for _ in range(90):
        r=subprocess.run(['docker','exec','-e','MYSQL_PWD=amigospass','basedatos','mariadb','-uamigosuser','amigosdb','-e','SELECT 1'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        if r.returncode==0:break
        time.sleep(1)
    else:raise TimeoutError('MariaDB no disponible')
    run(['docker','restart','amigos'])
    esperar(80)
    ok(http('GET','/api/amigos',puerto=80)==anterior,'los amigos sobreviven a recrear MariaDB')


def limpieza():
    # Solo datos de esta base independiente. El guion pide vaciar los tokens.
    ip=subprocess.check_output(['docker','inspect','basedatos','--format','{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}']).decode().strip()
    ENV['DATABASE_URI']='mysql+pymysql://amigosuser:amigospass@'+ip+'/amigosdb'
    py("for amigo in Amigo.query.all(): amigo.device=''\ndb.session.commit()\nprint([(a.name, a.device) for a in Amigo.query.all()])")
    ok(http('GET','/api/devices',puerto=80)==[],'sin tokens de prueba para la futura practica Android')
    http('GET','/html/amigos',puerto=80)
    run(['docker','ps','--format','{{.Names}} | {{.Image}} | {{.Ports}}'])
    sql('SELECT id,name,lati,longi,LENGTH(device) FROM amigos; SELECT version_num FROM alembic_version;')


class Duplicar(io.TextIOBase):
    def __init__(self, pantalla, archivo):self.pantalla,self.archivo=pantalla,archivo
    def write(self,s):self.pantalla.write(s);self.archivo.write(s);return len(s)
    def flush(self):self.pantalla.flush();self.archivo.flush()


def main():
    global PAUSA
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--capturas',action='store_true');p.add_argument('--preparar',action='store_true')
    p.add_argument('--desde')
    a=p.parse_args(); PAUSA=a.capturas
    EV.mkdir(parents=True,exist_ok=True)
    inspeccion=json.loads(subprocess.check_output(['docker','inspect','basedatos']))[0]
    mounts=[m for m in inspeccion['Mounts'] if m['Destination']=='/var/lib/mysql']
    assert len(mounts)==1 and Path(mounts[0]['Source']).resolve()==(BASE/'basedatos_verificacion').resolve(), 'Se requiere la base independiente de verificacion'
    ip=subprocess.check_output(['docker','inspect','basedatos','--format','{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}']).decode().strip()
    ENV['DATABASE_URI']='mysql+pymysql://amigosuser:amigospass@'+ip+'/amigosdb'
    pasos=[('00_entorno',entorno)]
    if a.preparar:pasos += [('01_base_vacia',base_vacia),('02_migracion_inicial',inicial),('03_migracion_device',migracion_device)]
    pasos += [('04_desarrollo',desarrollo),('05_formularios',formularios),('06_lecturas_api',lecturas_api),('07_altas_api',altas_api),('08_dispositivos',dispositivos),('09_bajas_api',bajas_api),('10_contenedores',imagen),('11_persistencia',persistencia),('12_limpieza',limpieza)]
    if a.desde:
        if (EV/'resultados.json').exists():RESULTADOS.update(json.loads((EV/'resultados.json').read_text())['bloques'])
        nombres=[n for n,f in pasos];pasos=pasos[nombres.index(a.desde):]
    try:
        for nombre,funcion in pasos:
            if PAUSA:print('\033[2J\033[H',end='',flush=True)
            with (EV/(nombre+'.txt')).open('w',encoding='utf8') as archivo:
                with contextlib.redirect_stdout(Duplicar(sys.stdout,archivo)):
                    print('INGENIERIA DE SERVICIOS | Practica 2.2 | '+nombre+'\n',flush=True)
                    funcion();print('\nBLOQUE VERIFICADO: '+nombre,flush=True)
            RESULTADOS[nombre]='correcto'
            (EV/'resultados.json').write_text(json.dumps({'fecha':datetime.datetime.now().astimezone().isoformat(),'bloques':RESULTADOS},indent=2))
            if PAUSA:
                (EV/'.captura_lista').write_text(nombre)
                input('Captura preparada. Pulsa Intro para continuar...')
                (EV/'.captura_lista').unlink(missing_ok=True)
        print('Verificacion completada. Servicios finales activos.')
    finally:
        parar_desarrollo()
        (EV/'.captura_lista').unlink(missing_ok=True)


if __name__=='__main__':main()
