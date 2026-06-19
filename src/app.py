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
from models import db, User, Person, Planets
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


@app.route("/user", methods=["POST"])
def create_user():

    body = request.get_json()
    email, password, name, last_name = getVal(
        body, ["email", "password", "name", "last_name", "is_active"])

    user = User(email=email,
                password=password,
                name=name,
                last_name=last_name)

    try:
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"msg": "Creando usuario 😻",
                    "user": user.serialize()
                    }), 201


@app.route("/user")
def get_user():
    try:
        user = User.query.all()
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify([item.serialize() for item in user]), 200


@app.route("/people")
def get_people():
    try:
        person = Person.query.all()
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify([item.serialize() for item in person]), 200


@app.route("/people/<int:people_id>")
def get_people_id(people_id):
    try:
        person = Person.query.get(people_id)
        if not person:
            return jsonify({"error": "Person not found"}), 404
        return jsonify(person.serialize()), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/planets")
def get_planets():
    try:
        planets = Planets.query.all()

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify([item.serialize() for item in planets]), 200


@app.route("/planets/<int:planets_id>")
def get_planets_id(planets_id):
    try:
        planets = Planets.query.get(planets_id)
        if not planets:
            return jsonify({"error": "Planets not found"}), 404
        return jsonify(planets.serialize()), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=True)
