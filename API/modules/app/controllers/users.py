import os
from flask import request, jsonify, Blueprint
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_raw_jwt

from modules.app import MONGO, BCRYPT, JWT, BLACKLIST
from bson.json_util import dumps
from modules.app.jsonschema import validate_user
from modules.logger import logger

MODULE_USERS = Blueprint('user', __name__, url_prefix='/user')

ROOT_PATH = os.environ.get('ROOT_PATH')
LOG = logger.get_root_logger(__name__, filename=os.path.join(ROOT_PATH, 'output.log'))

@MODULE_USERS.route('/', methods=['GET', 'POST', 'DELETE', 'PUT'])
@jwt_required
def user():
    user = get_jwt_identity()
    if request.method == 'GET':
        data = MONGO.db.users.find()
        LOG.debug(data)
        return dumps(data, skipkeys=True, allow_nan=True, indent=999), 200

    data = request.get_json()
    if request.method == 'POST':
        if data.get('name', None) is not None and data.get('email', None) is not None \
                and data.get('password', None) is not None:
            db_response = MONGO.db.users.find_one({'email': data['email']})
            LOG.debug(db_response)
            if db_response:
                return jsonify({'ok': True, 'message': 'Email already used!'}), 409
            else:
                inseruser = MONGO.db.users.insert_one(data)
                LOG.debug(inseruser)
                return jsonify({'ok': True, 'message': 'User created successfully!'}), 200
        else:
            return jsonify({'ok': False, 'message': 'Bad request parameters!'}), 400

    if request.method == 'DELETE':
        if user.get('email', None) is not None:
            db_response = MONGO.db.users.delete_one({'email': user['email']})
            LOG.debug(db_response)
            deletemany = MONGO.db.hotels.delete_many({'Proprietaire': user['email']})
            LOG.debug(deletemany)
            updatemany = MONGO.db.hotels.update_many({}, {'$pull': {'Reservations': {'Client': user['email']}}})
            LOG.debug(updatemany)
            if db_response.deleted_count == 1:
                logout()
                return jsonify({'ok': True, 'message': 'User deleted. Please Register'}), 200
            else:
                return jsonify({'ok': False, 'message': 'User not found'}), 409
        else:
            return jsonify({'ok': False, 'message': 'Bad request parameters!'}), 400

    if request.method == 'PUT':
        if data.get('query', None) is not None:
            data['query']['email'] = user['email']
            if data['query'].get('email', None) is not None:
                if data['payload'].get('password', None) is not None:
                    data['payload']['password'] = BCRYPT.generate_password_hash(data['payload']['password'])
                updateone = MONGO.db.users.update_one(data['query'], {'$set': data.get('payload', {})})
                LOG.debug(updateone)
                logout()
            return jsonify({'ok': True, 'message': 'User updated. Please Reconnect'}), 200
        else:
            return jsonify({'ok': False, 'message': 'Bad request parameters!'}), 400

@MODULE_USERS.route('/register', methods=['POST'])
def register():
    data = validate_user(request.get_json())
    if data['ok']:
        data = data['data']
        user = MONGO.db.users.find_one({'email': data['email']}, {"_id": 0})
        LOG.debug(user)
        if user:
            return jsonify({'ok': False, 'message': 'Email already used!'}), 409
        else:
            data['password'] = BCRYPT.generate_password_hash(data['password'])
            insert = MONGO.db.users.insert_one(data)
            LOG.debug(insert)
            return jsonify({'ok': True, 'message': 'User created successfully!'}), 200
    else:
        return jsonify({'ok': False, 'message': 'Bad request parameters: {}'
                       .format(data['message'])}), 400

@MODULE_USERS.route('/auth', methods=['POST'])
def auth_user():
    data = validate_user(request.get_json())
    if data['ok']:
        data = data['data']
        user = MONGO.db.users.find_one({'email': data['email']}, {"_id": 0})
        LOG.debug(user)
        if user and BCRYPT.check_password_hash(user['password'], data['password']):
            del user['password']
            '''logout()'''
            access_token = create_access_token(identity=data)
            user['token'] = access_token
            return jsonify({'ok': True, 'data': user}), 200
        else:
            return jsonify({'ok': False, 'message': 'invalid email or password'}), 401
    else:
        return jsonify({'ok': False, 'message': 'Bad request parameters: {}'.format(data['message'])}), 400

@MODULE_USERS.route('/logout', methods=['DELETE'])
@jwt_required
def logout():
    jti = get_raw_jwt()['jti']
    BLACKLIST.add(jti)
    return jsonify({"msg": "Successfully logged out. Please reconnect"}), 200

@JWT.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return jti in BLACKLIST

@JWT.unauthorized_loader
def unauthorized_response(callback):
    return jsonify({'ok': False, 'message': 'Missing Authorization Header'}), 401
