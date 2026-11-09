from flask import request, abort, jsonify

from .. import db
from . import api
from ..models import Amigo


@api.route("/amigo/<int:id>")
def get_amigo(id):

    amigo = Amigo.query.get_or_404(id)

    amigodict = {
        'id': amigo.id,
        'name': amigo.name,
        'lati': amigo.lati,
        'longi': amigo.longi,
        'device': amigo.device
    }

    return jsonify(amigodict)


@api.route("/amigo/byName/<name>")
def get_amigo_by_name(name):

    amigo = Amigo.query.filter_by(name=name).first()

    if not amigo:
        abort(404, "No se encuentra ningún amigo con ese nombre")

    amigodict = {
        'id': amigo.id,
        'name': amigo.name,
        'lati': amigo.lati,
        'longi': amigo.longi,
        'device': amigo.device
    }

    return jsonify(amigodict)


@api.route("/amigos")
def list_amigos():

    amigos = Amigo.query.all()

    lista = []

    for amigo in amigos:

        amigodict = {
            'id': amigo.id,
            'name': amigo.name,
            'lati': amigo.lati,
            'longi': amigo.longi,
            'device': amigo.device
        }

        lista.append(amigodict)

    return jsonify(lista)


@api.route("/amigo/<int:id>", methods=["PUT"])
def edit_amigo(id):

    amigo = Amigo.query.get_or_404(id)

    if not request.json:
        abort(422, "No se ha enviado JSON")

    name = request.json.get("name")
    lati = request.json.get("lati")
    longi = request.json.get("longi")
    device = request.json.get("device")

    if name:
        amigo.name = name

    if lati:
        amigo.lati = lati

    if longi:
        amigo.longi = longi

    # Aceptamos también la cadena vacía
    if device is not None:
        amigo.device = device

    if name or lati or longi or device is not None:
        db.session.commit()

    amigodict = {
        "id": amigo.id,
        "name": amigo.name,
        "longi": amigo.longi,
        "lati": amigo.lati,
        "device": amigo.device
    }

    return jsonify(amigodict)


@api.route("/amigo/<int:id>", methods=["DELETE"])
def delete_amigo(id):

    amigo = Amigo.query.get_or_404(id)

    db.session.delete(amigo)
    db.session.commit()

    return ('', 204)


@api.route("/amigos", methods=["POST"])
def new_amigo():

    if not request.json:
        abort(422, "No se ha enviado JSON")

    name = request.json.get("name")

    if not name:
        abort(422, "El JSON no incluye el campo 'name'")

    amigo = Amigo.query.filter_by(name=name).first()

    if amigo:
        abort(422, "Ya existe un amigo con ese nombre")

    lati = request.json.get("lati", "0")
    longi = request.json.get("longi", "0")
    device = request.json.get("device")

    amigo = Amigo(
        name=name,
        lati=lati,
        longi=longi,
        device=device
    )

    db.session.add(amigo)
    db.session.commit()

    amigodict = {
        "id": amigo.id,
        "name": amigo.name,
        "longi": amigo.longi,
        "lati": amigo.lati,
        "device": amigo.device
    }

    return jsonify(amigodict)


@api.route("/devices")
def list_devices():
    """
    Retorna la lista de dispositivos no nulos ni vacíos
    """

    amigos = Amigo.query.all()

    devices = []

    for amigo in amigos:
        if amigo.device:
            devices.append(amigo.device)

    return jsonify(devices)