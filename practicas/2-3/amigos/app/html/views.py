from flask import render_template, redirect, url_for, request, abort

from . import html
from .. import db
from ..models import Amigo


@html.route("/amigos")
def tabla_amigos():

    amigos = Amigo.query.all()

    return render_template(
        "tabla_amigos.html",
        amigos=amigos
    )


@html.route("/delete_amigo/<int:id>")
def delete_amigo(id):

    amigo = Amigo.query.get_or_404(id)

    db.session.delete(amigo)
    db.session.commit()

    return redirect(url_for('html.tabla_amigos'))


@html.route("/edit_amigo/<int:id>")
def edit_amigo(id):

    amigo = Amigo.query.get_or_404(id)

    return render_template(
        "edit_amigo.html",
        amigo=amigo
    )


@html.route("/new_amigo/")
def new_amigo():

    return render_template(
        "edit_amigo.html",
        amigo=None
    )


@html.route("/save_amigo", methods=["POST"])
def save_amigo():

    id = request.form.get("id")

    if id is None or id == "":

        # Crear un amigo nuevo
        name = request.form.get("name")

        if not name:
            abort(422)

        lati = request.form.get("lati", "0")
        longi = request.form.get("longi", "0")
        device = request.form.get("device", "")

        amigo = Amigo(
            name=name,
            lati=lati,
            longi=longi,
            device=device
        )

        db.session.add(amigo)
        db.session.commit()

    else:

        # Modificar un amigo existente
        amigo = Amigo.query.get_or_404(int(id))

        name = request.form.get("name")

        if name:
            amigo.name = name

        lati = request.form.get("lati")

        if lati:
            amigo.lati = lati

        longi = request.form.get("longi")

        if longi:
            amigo.longi = longi

        # El dispositivo puede ser una cadena vacía
        device = request.form.get("device")

        if device is not None:
            amigo.device = device

        db.session.commit()

    return redirect(url_for("html.tabla_amigos"))