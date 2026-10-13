from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import app_config

db = SQLAlchemy()

def create_app(config_name):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')
    db.init_app(app)
    
    migrate = Migrate(app, db)
    from app import models

    @app.route('/amigos')
    def lista_amigos():
        from app.models import Amigo
        amigos = Amigo.query.all()
        return render_template('tabla_amigos.html', amigos=amigos)

    @app.route('/delete_amigo/<int:id>')
    def delete_amigo(id):
        from app.models import Amigo
        amigo = Amigo.query.get(id)
        if amigo:
            db.session.delete(amigo)
            db.session.commit()
        return redirect(url_for('lista_amigos'))

    @app.route('/new_amigo')
    def new_amigo():
        return render_template('amigo_form.html', amigo=None)

    @app.route('/edit_amigo/<int:id>')
    def edit_amigo(id):
        from app.models import Amigo
        amigo = Amigo.query.get(id)
        return render_template('amigo_form.html', amigo=amigo)

    @app.route('/save_amigo', methods=['POST'])
    def save_amigo():
        from app.models import Amigo
        amigo_id = request.form.get('id')
        name = request.form.get('name')
        lati = request.form.get('lati')
        longi = request.form.get('longi')
        
        if amigo_id: # Si hay ID, actualizamos el existente
            amigo = Amigo.query.get(amigo_id)
            amigo.name = name
            amigo.lati = lati
            amigo.longi = longi
        else: # Si no hay ID, creamos uno nuevo
            amigo = Amigo(name=name, lati=lati, longi=longi)
            db.session.add(amigo)
            
        db.session.commit()
        return redirect(url_for('lista_amigos'))

    return app