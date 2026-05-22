import os
from flask_admin import Admin
from .models import db, User, Character, Planet, Favorite
from flask_admin.contrib.sqla import ModelView


def setup_admin(app):
    app.secret_key = os.getenv('FLASK_APP_KEY', 'sample key')
    app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
    admin = Admin(app, name='Star Wars Admin', template_mode='bootstrap3')

    # Añadimos los modelos correspondientes a Star Wars
    admin.add_view(ModelView(User, db.session))
    admin.add_view(ModelView(Character, db.session))
    admin.add_view(ModelView(Planet, db.session))
    admin.add_view(ModelView(Favorite, db.session))
