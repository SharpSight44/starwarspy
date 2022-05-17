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
from models import db, User
from models import Characters
from models import Planets

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

todos = [ { "label": "My first task", "done": False } ]
# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/people', methods=['GET'])
def handle_people():
    json_text = jsonify(todos)
    return json_text, 200

@app.route('/people/<int:people_id>', methods=['GET'])
def handle_people_id():
    json_text = jsonify(todos)
    return json_text, 200

@app.route('/planets', methods=['GET'])
def handle_planets():
    table = Planets.query.all()
    info = list(map(lambda x: x.serialize(),table ) )
    return jsonify(info), 200

@app.route('/people', methods=['POST'])
def handle_people_post():
    payload_people = request.get_json()
    info_people = Characters(name=payload_people["name"], home=payload_people["home"], ships=payload_people["ships"])
    return jsonify(info_people), 200

@app.route('/planets', methods=['POST'])
def handle_planets_post():
    payload = request.get_json()
    info = Planets(name=payload["name"], population=payload["population"], climate=payload["climate"])
    db.session.add(info)
    db.session.commit()
    return "success", 200

# @app.route('/planets/<int:planet_id>', methods=['GET'])
# def handle_planet_id():
#     json_text = jsonify(todos)
#     return json_text, 200

@app.route('/users', methods=['GET'])
def handle_users():
    json_text = jsonify(todos)
    return json_text, 200

@app.route('/users/favorites', methods=['GET'])
def handle_users_favorites():
    json_text = jsonify(todos)
    return json_text, 200


@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_new_fav_planet():
    payload = request.get_json(force=True)
    todos.append(payload)
    
    return jsonify(todos)

@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_new_fav_people():
    payload = request.get_json(force=True)
    todos.append(payload)
    
    return jsonify(todos)

@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_fav_planet(position):
    
    todos.pop(position)
    return "all set"    

@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_fav_people(position):
    
    todos.pop(position)
    return "all set"





# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
