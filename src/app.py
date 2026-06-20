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
from models import db, User, Person, Planets, Favorites
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
# from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace(
        "postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object


@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints


@app.route('/')
def sitemap():
    return generate_sitemap(app)


def getVal(request_body, fields):
    values = []
    for field in fields:
        value = request_body.get(field)
        if value is None or value == "":
            raise APIException(
                f"Se debe proveer un valor para {field}", status_code=400)
        values.append(value)
    return values


@app.route("/users", methods=["GET"])
def get_users():
    try:
        query = select(User)
        users = db.session.scalars(query).all()
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify([item.serialize() for item in users]), 200


@app.route("/users", methods=["POST"])
def create_user():

    body = request.get_json()
    if body is None:
        return jsonify({"error": "El cuerpo de la petición debe ser un JSON válido"}), 400

    email, password, name, last_name = getVal(
        body, ["email", "password", "name", "last_name"])

    user = User(email=email,
                password=password,
                name=name,
                last_name=last_name)

    try:
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "El correo electrónico ya está registrado"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error inesperado: {str(e)}"}), 500

    return jsonify({"msg": "Creando usuario 😻",
                    "user": user.serialize()
                    }), 201


@app.route("/users/favorites")
def get_user_favorites():
    try:
        query = select(Favorites)
        favorites = db.session.scalars(query).all()
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify([item.serialize() for item in favorites]), 200


@app.route("/people", methods=["GET"])
def get_people():
    try:
        query = select(Person)
        person = db.session.scalars(query).all()
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify([item.serialize() for item in person]), 200


@app.route("/people/<int:people_id>", methods=["GET"])
def get_people_id(people_id):
    try:
        person = db.session.get(Person, people_id)
        if not person:
            return jsonify({"error": "Person not found"}), 404
        return jsonify(person.serialize()), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/planets", methods=["GET"])
def get_planets():
    try:
        query = select(Planets)
        planets = db.session.scalars(query).all()
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify([item.serialize() for item in planets]), 200


@app.route("/planets/<int:planets_id>", methods=["GET"])
def get_planets_id(planets_id):
    try:
        planets = db.session.get(Planets, planets_id)
        if not planets:
            return jsonify({"error": "Planets not found"}), 404
        return jsonify(planets.serialize()), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/favorite/planet/<int:planet_id>", methods=["POST"])
def add_favorite_planet(planet_id):
    body = request.get_json()
    user_id = body.get("user_id") if body else None
    if not user_id:
        return jsonify({"error": "Se debe proveer un valor para user_id"}), 400
    try:
        planet_exists = db.session.get(Planets, planet_id)
        if not planet_exists:
            return jsonify({"error": f"El planeta con id {planet_id} no existe"}), 404
        user_exists = db.session.get(User, user_id)
        if not user_exists:
            return jsonify({"error": f"El usuario con id {user_id} no existe"}), 404

        new_favorite = Favorites(user_id=user_id, planet_id=planet_id)

        db.session.add(new_favorite)
        db.session.commit()
        db.session.refresh(new_favorite)

    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Este planeta ya se encuentra en los favoritos de este usuario"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error en el servidor: {str(e)}"}), 500

    return jsonify({
        "msg": "Planeta agregado a favoritos 😻",
        "favorite": new_favorite.serialize()
    }), 201


@app.route("/favorite/people/<int:people_id>", methods=["POST"])
def add_favorite_person(people_id):
    body = request.get_json()
    user_id = body.get("user_id") if body else None
    if not user_id:
        return jsonify({"error": "Se debe proveer un valor para user_id"}), 400
    try:
        person_exists = db.session.get(Person, people_id)
        if not person_exists:
            return jsonify({"error": f"La persona con id {people_id} no existe"}), 404
        user_exists = db.session.get(User, user_id)
        if not user_exists:
            return jsonify({"error": f"El usuario con id {user_id} no existe"}), 404

        new_favorite = Favorites(user_id=user_id, person_id=people_id)

        db.session.add(new_favorite)
        db.session.commit()
        db.session.refresh(new_favorite)

    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Esta persona ya se encuentra en los favoritos de este usuario"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error en el servidor: {str(e)}"}), 500

    return jsonify({
        "msg": "Persona agregada a favoritos 😻",
        "favorite": new_favorite.serialize()
    }), 201


@app.route("/favorite/planet/<int:planet_id>", methods=["DELETE"])
def remove_favorite_planet(planet_id):
    body = request.get_json()
    user_id = body.get("user_id") if body else None
    if not user_id:
        return jsonify({"error": "Se debe proveer un valor para user_id"}), 400
    try:
        query = select(Favorites).where(Favorites.user_id == user_id, Favorites.planet_id == planet_id)
        favorite = db.session.scalars(query).first()
        if not favorite:
            return jsonify({"error": f"El planeta con id {planet_id} no se encuentra en los favoritos del usuario con id {user_id}"}), 404

        db.session.delete(favorite)
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error en el servidor: {str(e)}"}), 500

    return jsonify({
        "msg": "Planeta eliminado de favoritos 😻"
    }), 200


@app.route("/favorite/people/<int:people_id>", methods=["DELETE"])
def remove_favorite_person(people_id):
    body = request.get_json()
    user_id = body.get("user_id") if body else None
    if not user_id:
        return jsonify({"error": "Se debe proveer un valor para user_id"}), 400
    try:
        query = select(Favorites).where(Favorites.user_id == user_id, Favorites.person_id == people_id)
        favorite = db.session.scalars(query).first()
        if not favorite:
            return jsonify({"error": f"La persona con id {people_id} no se encuentra en los favoritos del usuario con id {user_id}"}), 404

        db.session.delete(favorite)
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error en el servidor: {str(e)}"}), 500

    return jsonify({
        "msg": "Persona eliminada de favoritos 😻"
    }), 200


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=True)
