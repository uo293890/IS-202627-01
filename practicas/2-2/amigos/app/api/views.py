from flask import request, abort, jsonify
from .. import db
from . import api
from ..models import Amigo
from ..validacion import validar, guardar


def datos_json():
    datos = request.get_json(silent=True)
    if not isinstance(datos, dict) or not datos:
        abort(422, "Se requiere un objeto JSON no vacio")
    return datos

# GET /api/amigo/<id>
@api.route("/amigo/<int:id>")
def get_amigo(id):
    amigo = Amigo.query.get_or_404(id)
    return jsonify({
        'id': amigo.id,
        'name': amigo.name,
        'lati': amigo.lati,
        'longi': amigo.longi,
        'device': amigo.device or ''
    })

# GET /api/amigo/byName/<name>
@api.route("/amigo/byName/<name>")
def get_amigo_by_name(name):
    amigo = Amigo.query.filter_by(name=name).first()
    if not amigo:
        abort(404, "No se encuentra ningún amigo con ese nombre")
    return jsonify({
        'id': amigo.id,
        'name': amigo.name,
        'lati': amigo.lati,
        'longi': amigo.longi,
        'device': amigo.device or ''
    })

# GET /api/amigos
@api.route("/amigos")
def list_amigos():
    amigos = Amigo.query.all()
    lista = [{
        'id': a.id,
        'name': a.name,
        'lati': a.lati,
        'longi': a.longi,
        'device': a.device or ''
    } for a in amigos]
    return jsonify(lista)

# GET /api/devices
@api.route("/devices")
def list_devices():
    amigos = Amigo.query.filter(Amigo.device.isnot(None), Amigo.device != "").all()
    devices = [a.device for a in amigos]
    return jsonify(devices)

# PUT /api/amigo/<id>
@api.route("/amigo/<int:id>", methods=["PUT"])
def edit_amigo(id):
    amigo = Amigo.query.get_or_404(id)
    datos = datos_json()
    validar(datos, amigo=amigo)
    
    name = datos.get("name")
    lati = datos.get("lati")
    longi = datos.get("longi")
    device = datos.get("device")

    if name is not None: amigo.name = name
    if lati is not None: amigo.lati = lati
    if longi is not None: amigo.longi = longi
    if 'device' in datos: amigo.device = device

    guardar()

    return jsonify({
        "id": amigo.id,
        "name": amigo.name,
        "lati": amigo.lati,
        "longi": amigo.longi,
        "device": amigo.device or ''
    })

# DELETE /api/amigo/<id>
@api.route("/amigo/<int:id>", methods=["DELETE"])
def delete_amigo(id):
    amigo = Amigo.query.get_or_404(id)
    db.session.delete(amigo)
    db.session.commit()
    return ('', 204)

# POST /api/amigos
@api.route("/amigos", methods=["POST"])
def new_amigo():
    datos = datos_json()
    validar(datos, nuevo=True)
    name = datos['name']
    lati = datos.get("lati", "0")
    longi = datos.get("longi", "0")
    device = datos.get("device")

    amigo = Amigo(name=name, lati=lati, longi=longi, device=device)
    db.session.add(amigo)
    guardar()

    return jsonify({
        "id": amigo.id,
        "name": amigo.name,
        "lati": amigo.lati,
        "longi": amigo.longi,
        "device": amigo.device or ''
    })
