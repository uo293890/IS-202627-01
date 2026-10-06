from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import app_config

db = SQLAlchemy()

def create_app(config_name):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')
    db.init_app(app)
    
    # Soporte para migraciones
    migrate = Migrate(app, db)
    from app import models

    @app.route("/")
    def prueba():
        return "¡Hola Flask con MariaDB!"

    # NUEVA RUTA
    @app.route('/amigos')
    def lista_amigos():
        # Consultamos todos los amigos en la base de datos
        from app.models import Amigo
        amigos = Amigo.query.all()
        
        # Le pasamos la variable 'amigos' a la plantilla HTML
        return render_template('tabla_amigos.html', amigos=amigos)

    return app