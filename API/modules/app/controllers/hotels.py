import os

from flask import request, jsonify, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity

from modules.app import MONGO
from bson.json_util import dumps

from modules.logger import logger

MODULE_HOTELS = Blueprint('hotel', __name__, url_prefix='/hotel')

ROOT_PATH = os.environ.get('ROOT_PATH')
LOG = logger.get_root_logger(__name__, filename=os.path.join(ROOT_PATH, 'output.log'))

@MODULE_HOTELS.route('/', methods=['GET', 'POST', 'DELETE', 'PUT'])
@jwt_required
def hotel():
    user = get_jwt_identity()
    if request.method == 'GET':
        query = request.args
        data = MONGO.db.hotels.find(query)
        LOG.debug(data)
        return dumps(data, skipkeys=True, allow_nan=True, indent=3), 200

    data = request.get_json()
    if request.method == 'POST':
        if data.get('Nom', None) is not None and data.get('Description', None) is not None \
                and data.get('Address', None) is not None and data.get('Telephone', None) is not None\
                and data.get('Chambres', None) is not None and data.get('Services', None) is not None \
                and data.get('PolitiquePrix', None) is not None and data.get('Reservations', None) is not None:
            db_response = MONGO.db.hotels.find_one({'Nom': data['Nom']})
            LOG.debug(db_response)
            if db_response:
                return jsonify({'ok': False, 'message': 'Hotel name already used! '}), 409
            else:
                data['Proprietaire'] = user['email']
                insert = MONGO.db.hotels.insert_one(data)
                LOG.debug(insert)
                return jsonify({'ok': True, 'message': 'Hotel created successfully! '}), 200
        elif data.get('query', {}) != {}:
            update = MONGO.db.hotels.update_one(data['query'], {'$push': data.get('payload', {})})
            LOG.debug(update)
            return jsonify({'ok': True, 'message': 'Element added '}), 200
        else:
            return jsonify({'ok': False, 'message': 'Bad request parameters! '}), 400

    if request.method == 'DELETE':
        if data.get('Nom', None) is not None:
            hotelUser = MONGO.db.hotels.find_one({'Nom': data['Nom'], 'Proprietaire': user['email']})
            LOG.debug(hotelUser)
            if hotelUser:
                db_response = MONGO.db.hotels.delete_one({'Nom': data['Nom']})
                LOG.debug(db_response)
                if db_response.deleted_count == 1:
                    return jsonify({'ok': True, 'message': 'Hotel deleted '}), 200
                else:
                    return jsonify({'ok': False, 'message': 'Hotel not found'}), 409
            else:
                return jsonify({'ok': False, 'message': 'You not authorize!'}), 401
        elif data.get('query', {}) != {}:
            hotelUser = MONGO.db.hotels.find_one({'Nom': data['query']['Nom'], 'Proprietaire': user['email']})
            LOG.debug(hotelUser)
            if hotelUser:
                updateone = MONGO.db.hotels.update_one(data['query'], {'$pull': data.get('payload', {})})
                LOG.debug(updateone)
                return jsonify({'ok': True, 'message': 'Element deleted'}), 200
            else:
                return jsonify({'ok': False, 'message': 'You not authorize!'}), 401
        else:
            return jsonify({'ok': False, 'message': 'Bad request parameters!'}), 400

    if request.method == 'PUT':
        if data.get('query', {}) != {} and data['query'].get('Nom', None) is not None:
            hotelUser = MONGO.db.hotels.find_one({'Nom': data['query']['Nom'], 'Proprietaire': user['email']})
            LOG.debug(hotelUser)
            if hotelUser:
                update2 = MONGO.db.hotels.update_one(data['query'], {'$set': data.get('payload', {})})
                LOG.debug(update2)
                return jsonify({'ok': True, 'message': 'hotel updated'}), 200
            else:
                return jsonify({'ok': False, 'message': 'You not authorize!'}), 401
        else:
            return jsonify({'ok': False, 'message': 'Bad request parameters!'}), 400