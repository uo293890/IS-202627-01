from flask import request, abort, jsonify
from .. import db
from . import api
from ..models import Amigo

# GET /api/amigo/<id>
@api.route("/amigo/<int:id>")
def get_amigo(id):
    amigo = Amigo.query.get_or_404(id)
    amigodict = {'id': amigo.id, 'name': amigo.name, 'lati': amigo.lati, 'longi': amigo.longi}
    return jsonify(amigodict)

# GET /api/amigo/byName/<name>
@api.route("/amigo/byName/<name>")
def get_amigo_by_name(name):
    amigo = Amigo.query.filter_by(name=name).first()
    if not amigo:
        abort(404, "No se encuentra ningún amigo con ese nombre")
    amigodict = {'id': amigo.id, 'name': amigo.name, 'lati': amigo.lati, 'longi': amigo.longi}
    return jsonify(amigodict)

# EJERCICIO 5.2.5: GET /api/amigos
@api.route("/amigos")
def list_amigos():
    amigos = Amigo.query.all()
    lista = [{'id': a.id, 'name': a.name, 'lati': a.lati, 'longi': a.longi} for a in amigos]
    return jsonify(lista)

# PUT /api/amigo/<id>
@api.route("/amigo/<int:id>", methods=["PUT"])
def edit_amigo(id):
    amigo = Amigo.query.get_or_404(id)
    if not request.json:
        abort(422, "No se ha enviado JSON")
    
    name = request.json.get("name")
    lati = request.json.get("lati")
    longi = request.json.get("longi")

    if name: amigo.name = name
    if lati: amigo.lati = lati
    if longi: amigo.longi = longi

    if name or lati or longi:
        db.session.commit()

    amigodict = {"id": amigo.id, "name": amigo.name, "longi": amigo.longi, "lati": amigo.lati}
    return jsonify(amigodict)

# EJERCICIO 5.2.7: DELETE /api/amigo/<id>
@api.route("/amigo/<int:id>", methods=["DELETE"])
def delete_amigo(id):
    amigo = Amigo.query.get_or_404(id)
    db.session.delete(amigo)
    db.session.commit()
    return ('', 204)

# POST /api/amigos
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

    amigo = Amigo(name=name, lati=lati, longi=longi)
    db.session.add(amigo)
    db.session.commit()

    amigodict = {"id": amigo.id, "name": amigo.name, "longi": amigo.longi, "lati": amigo.lati}
    return jsonify(amigodict)