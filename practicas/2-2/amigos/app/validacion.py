"""Validacion compartida por los formularios y la API del laboratorio."""
from flask import abort
from sqlalchemy.exc import IntegrityError
from . import db
from .models import Amigo


def validar(datos, amigo=None, nuevo=False):
    if nuevo or 'name' in datos:
        nombre = datos.get('name')
        if not isinstance(nombre, str) or not nombre.strip() or len(nombre) > 32:
            abort(422, "El nombre es obligatorio y admite hasta 32 caracteres")
        existente = Amigo.query.filter_by(name=nombre).first()
        if existente is not None and (amigo is None or existente.id != amigo.id):
            abort(422, "Ya existe un amigo con ese nombre")
    for campo in ('lati', 'longi'):
        if campo in datos and (not isinstance(datos[campo], str) or len(datos[campo]) > 32):
            abort(422, "Las coordenadas deben ser cadenas de hasta 32 caracteres")
    if 'device' in datos and datos['device'] is not None:
        if not isinstance(datos['device'], str) or len(datos['device']) > 4096:
            abort(422, "El dispositivo admite hasta 4096 caracteres")


def guardar():
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        abort(422, "Los datos incumplen una restriccion de la base de datos")
