# Importar la función create_app desde la carpeta app

from app import create_app
import os

# Usarlo para instanciar la aplicación
modo = os.getenv("DEPLOYMENT_MODE", "production")

app = create_app(modo)