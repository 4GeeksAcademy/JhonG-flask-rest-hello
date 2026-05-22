import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from src.utils import APIException, generate_sitemap
from src.admin import setup_admin
from src.models import db, User, Character, Planet, Favorite

app = Flask(__name__)
app.url_map.strict_slashes = False

# Configuración de base de datos adaptada a tu entorno
db_url = os.getenv("DATABASE_URL", "sqlite:////tmp/test.db")
app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Manejo de errores globales
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# Generar el mapa del sitio inicial
@app.route('/')
def sitemap():
    return generate_sitemap(app)

# --- ENDPOINTS OBLIGATORIOS DE STAR WARS ---

# 1. GET /people (Todos los personajes)
@app.route('/people', methods=['GET'])
def get_all_characters():
    characters = Character.query.all()
    return jsonify([char.serialize() for char in characters]), 200

# 2. GET /people/<int:people_id> (Un solo personaje)
@app.route('/people/<int:people_id>', methods=['GET'])
def get_one_character(people_id):
    char = Character.query.get(people_id)
    if not char:
        return jsonify({"msg": "Personaje no encontrado"}), 404
    return jsonify(char.serialize()), 200

# 3. GET /planets (Todos los planetas)
@app.route('/planets', methods=['GET'])
def get_all_planets():
    planets = Planet.query.all()
    return jsonify([plan.serialize() for plan in planets]), 200

# 4. GET /planets/<int:planet_id> (Un solo planeta)
@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_one_planet(planet_id):
    plan = Planet.query.get(planet_id)
    if not plan:
        return jsonify({"msg": "Planeta no encontrado"}), 404
    return jsonify(plan.serialize()), 200

# 5. GET /users (Todos los usuarios)
@app.route('/users', methods=['GET'])
def get_all_users():
    users = User.query.all()
    return jsonify([u.serialize() for u in users]), 200

# 6. GET /users/favorites (Favoritos del usuario actual con ID 1)
@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    current_user_id = 1
    favs = Favorite.query.filter_by(user_id=current_user_id).all()
    return jsonify([f.serialize() for f in favs]), 200

# 7. POST /favorite/planet/<int:planet_id> (Añadir planeta favorito)
@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    current_user_id = 1
    if not Planet.query.get(planet_id):
        return jsonify({"msg": "El planeta no existe"}), 404
    
    exists = Favorite.query.filter_by(user_id=current_user_id, planet_id=planet_id).first()
    if exists:
        return jsonify({"msg": "Ya es un favorito"}), 400

    new_fav = Favorite(user_id=current_user_id, planet_id=planet_id)
    db.session.add(new_fav)
    db.session.commit()
    return jsonify({"msg": "Planeta agregado a favoritos"}), 201

# 8. POST /favorite/people/<int:people_id> (Añadir personaje favorito)
@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_character(people_id):
    current_user_id = 1
    if not Character.query.get(people_id):
        return jsonify({"msg": "El personaje no existe"}), 404
    
    exists = Favorite.query.filter_by(user_id=current_user_id, character_id=people_id).first()
    if exists:
        return jsonify({"msg": "Ya es un favorito"}), 400

    new_fav = Favorite(user_id=current_user_id, character_id=people_id)
    db.session.add(new_fav)
    db.session.commit()
    return jsonify({"msg": "Personaje agregado a favoritos"}), 201

# 9. DELETE /favorite/planet/<int:planet_id> (Eliminar planeta favorito)
@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    current_user_id = 1
    fav = Favorite.query.filter_by(user_id=current_user_id, planet_id=planet_id).first()
    if not fav:
        return jsonify({"msg": "Favorito no encontrado"}), 404
    db.session.delete(fav)
    db.session.commit()
    return jsonify({"msg": "Planeta eliminado de favoritos"}), 200

# 10. DELETE /favorite/people/<int:people_id> (Eliminar personaje favorito)
@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_character(people_id):
    current_user_id = 1
    fav = Favorite.query.filter_by(user_id=current_user_id, character_id=people_id).first()
    if not fav:
        return jsonify({"msg": "Favorito no encontrado"}), 404
    db.session.delete(fav)
    db.session.commit()
    return jsonify({"msg": "Personaje eliminado de favoritos"}), 200

if __name__ == '__main__':
    PORT = int(os.getenv('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=True)