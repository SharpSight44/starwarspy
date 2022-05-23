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
from models import Favorites
from models import Account
from argon2 import PasswordHasher 
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, JWTManager

ph = PasswordHasher()



app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "very-long-secret-nobody-know"  # Change this "super secret" with something else!
jwt = JWTManager(app)

app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

#1st step /register  #2. /login (token generated/assigned) 
# 3. /accounts (insert token in Header of GET request ) accesses  Unique USER Data

#Perfect /register Choose an Email and Password CREATES New USER & hashes Pwd---------------------------------------------
@app.route('/register', methods=['POST'])
def register():
    payload = request.get_json()

    user = User(
        email=payload['email'], 
        password=ph.hash(payload['password']), 
        is_active=True
    )

    db.session.add(user)
    db.session.commit()

    return "user registered", 200

#PERFECT /login Requires Correct Registered Email and Password - Produces & Returns a TOKEN-------------------------
@app.route('/login', methods=['POST'])
def login():
    payload = request.get_json()

    user = User.query.filter(User.email == payload['email']).first()
    if user is None:
        return 'failed-auth', 401

    try:
        ph.verify(user.password, payload['password'])
    except: 
        return 'failed-auth', 401

    token = create_access_token(identity=user.id)
    
    return jsonify({ 'token': token })

#PERFECT /accounts REQUIRES Token in Header (Token identifies(USER) and displays data unique to them )-----------------
@app.route('/accounts', methods=['GET'])
@jwt_required()
def accounts():
    user_id = get_jwt_identity()

    user = User.query.get(user_id)
    accounts = Account.query.filter(Account.user_id==user_id).all()

    account_info = { 
        "accounts": [x.serialize() for x in accounts],
        "user": user.serialize()
    }

    return jsonify(account_info)



# Handle/serialize errors like a JSON object--------------------------------------------------------------
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

#Perfect, /people "GET" Fetches Data from Characters Table -----------------------------------------------
@app.route('/people', methods=['GET'])
def handle_people():
    people = Characters.query.all()

    response = []
    for p in people:
        response.append(p.serialize())
    
    return jsonify(response)
#//?????????????????????????????????????????????????IDK Yet????????????????????????????????
@app.route('/people/<int:people_id>', methods=['GET'])
def handle_people_id():
    people = Characters.query.all()

    response = []
    for p in people:
        response.append(p.serialize())
    
    return jsonify(response)

#Perfect /planets "GET" Fetches DATA from Planets Table -------------------------------------------------
@app.route('/planets', methods=['GET'])
def handle_planets():
    table = Planets.query.all()
    info = list(map(lambda x: x.serialize(),table ) )
    return jsonify(info), 200

#WORKING PERFECT -  /people "POST" Creates a NEW Character and Adds to DATABSE  returns "Success only which is fine for now"
@app.route('/people', methods=['POST'])
def handle_people_post():
    payload_people = request.get_json()
    info_people = Characters(name=payload_people["name"], hair=payload_people["hair"], ships=payload_people["ships"])
    db.session.add(info_people)
    db.session.commit()
    return "Successfully Added", 200
#WORKING PERFECT -  /planets "POST" Creates a NEW Planet and Adds to DATABSE  returns "Success only which is fine for now"
@app.route('/planets', methods=['POST'])
def handle_planets_post():
    payload = request.get_json()
    info = Planets(name=payload["name"], population=payload["population"], climate=payload["climate"])
    db.session.add(info)
    db.session.commit()
    return "Successfully Added", 200



# @app.route('/planets/<int:planet_id>', methods=['GET'])
# def handle_planet_id():
#     json_text = jsonify(todos)
#     return json_text, 200

@app.route('/users', methods=['GET'])
def handle_users():
    user = User.query.all()

    response = []
    for x in user:
        response.append(x.serialize())
    
    return jsonify(response)

@app.route('/users/favorites', methods=['GET'])
def handle_users_favorites():
    fav = Favorites.query.all()

    response = []
    for x in fav:
        response.append(x.serialize())
    
    return jsonify(response)


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
