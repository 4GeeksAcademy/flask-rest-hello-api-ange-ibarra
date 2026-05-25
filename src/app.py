"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, People, Planet, Favorite
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)



@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code



@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200


@app.route('/people', methods=['GET'])
def get_all_people():
    people = People.query.all()
    return jsonify([p.serialize() for p in people]), 200

@app.route('/people/<int:people_id>', methods=['GET'])
def get_one_person(people_id):
    person = People.query.get(people_id)
    if not person:
        return jsonify({"msg": "Personaje no encontrado"}), 404
    return jsonify(person.serialize()), 200

# --- ENDPOINTS PLANETS ---

@app.route('/planets', methods=['GET'])
def get_all_planets():
    planets = Planet.query.all()
    return jsonify([p.serialize() for p in planets]), 200

@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_one_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if not planet:
        return jsonify({"msg": "Planeta no encontrado"}), 404
    return jsonify(planet.serialize()), 200

# --- ENDPOINTS USUARIOS Y FAVORITOS ---

@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([u.serialize() for u in users]), 200

@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    
    favs = Favorite.query.filter_by(user_id=1).all()
    return jsonify([f.serialize() for f in favs]), 200

@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    
    new_fav = Favorite(user_id=1, planet_id=planet_id)
    db.session.add(new_fav)
    db.session.commit()
    return jsonify({"msg": "Planeta favorito añadido"}), 201

@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_people(people_id):
    new_fav = Favorite(user_id=1, people_id=people_id)
    db.session.add(new_fav)
    db.session.commit()
    return jsonify({"msg": "Personaje favorito añadido"}), 201

@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    fav = Favorite.query.filter_by(user_id=1, planet_id=planet_id).first()
    if fav:
        db.session.delete(fav)
        db.session.commit()
        return jsonify({"msg": "Favorito eliminado"}), 200
    return jsonify({"msg": "No se encontró el favorito"}), 404

@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_people(people_id):
    fav = Favorite.query.filter_by(user_id=1, people_id=people_id).first()
    if fav:
        db.session.delete(fav)
        db.session.commit()
        return jsonify({"msg": "Favorito eliminado"}), 200
    return jsonify({"msg": "No se encontró el favorito"}), 404

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)