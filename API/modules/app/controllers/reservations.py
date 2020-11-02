import os

from flask import request, jsonify, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_mail import Message
from modules.app import MONGO, MAIL
from bson.json_util import dumps
from datetime import datetime
from modules.logger import logger
import calendar

MODULE_RESERVATIONS = Blueprint('reservation', __name__, url_prefix='/reservation')

ROOT_PATH = os.environ.get('ROOT_PATH')
LOG = logger.get_root_logger(__name__, filename=os.path.join(ROOT_PATH, 'output.log'))


@MODULE_RESERVATIONS.route('/', methods=['GET', 'POST', 'DELETE'])
@jwt_required
def reservation():
    user = get_jwt_identity()
    query = request.args
    db_response = MONGO.db.hotels.find_one(query)
    LOG.debug(db_response)
    if query.get('Nom', None) is not None and db_response:
        if request.method == 'GET':
            data = MONGO.db.hotels.find(query)
            LOG.debug(data)
            return dumps(data, skipkeys=True, allow_nan=True, indent=6), 200

        data = request.get_json()
        if request.method == 'POST':
            if data.get('Reservations', None) is not None and data['Reservations'].get('DateDebut', None) is not None \
                    and data['Reservations'].get('DateFin', None) is not None \
                    and data['Reservations'].get('Chambres', None) is not None \
                    and data['Reservations'].get('Services', None) is not None:
                solo = MONGO.db.hotels.find({'Nom': db_response['Nom']},
                                            {'PolitiquePrix': {'$elemMatch': {'Categorie': 'Solo'}}})
                LOG.debug(solo)
                nuitMJ = MONGO.db.hotels.find({'Nom': db_response['Nom']},
                                              {'PolitiquePrix': {
                                                  '$elemMatch': {'Categorie': 'Nuit Mercredi et Jeudi'}}})
                LOG.debug(nuitMJ)
                nuitVS = MONGO.db.hotels.find({'Nom': db_response['Nom']},
                                              {'PolitiquePrix': {
                                                  '$elemMatch': {'Categorie': 'Nuit Vendredi et Samedi'}}})
                LOG.debug(nuitVS)
                chambres = data['Reservations']['Chambres']
                services = data['Reservations']['Services']
                dateDebut = datetime.strptime(data['Reservations']['DateDebut'], '%d/%m/%Y')
                dateFin = datetime.strptime(data['Reservations']['DateFin'], '%d/%m/%Y')
                message = ''
                prix_total = 0
                for item in chambres:
                    categorie = item['Categorie']
                    nb_pers = int(item['Pers'])
                    chambre = MONGO.db.hotels.find({'Nom': db_response['Nom']},
                                                   {'Chambres': {'$elemMatch': {'Categorie': categorie}}})
                    LOG.debug(chambre)
                    if chambre[0].get('Chambres', None) is not None:
                        quantite = int(chambre[0]['Chambres'][0]['Quantite'])
                        max_pers = int(chambre[0]['Chambres'][0]['Max_Pers'])
                        prix = int(chambre[0]['Chambres'][0]['Prix($)'])
                        if quantite > 0:
                            if nb_pers <= max_pers:
                                dayD = calendar.day_name[dateDebut.weekday()]
                                dayF = calendar.day_name[dateFin.weekday()]
                                prix_total = prix_total + prix

                                if nuitVS[0].get('PolitiquePrix', None) is not None and \
                                        ((dayD == 'Friday' and dayF == 'Saturday') or
                                         (dayD == 'Saturday' and dayF == 'Sunday')):
                                    tauxNVS = int(nuitVS[0]['PolitiquePrix'][0]['Taux(%)'])
                                    prix_total = prix_total + (prix * (tauxNVS / 100))

                                if nuitMJ[0].get('PolitiquePrix', None) is not None and \
                                        ((dayD == 'Wednesday' and dayF == 'Thursday') or
                                         (dayD == 'Thursday' and dayF == 'Friday')):
                                    tauxNMJ = int(nuitMJ[0]['PolitiquePrix'][0]['Taux(%)'])
                                    prix_total = prix_total - (prix * (tauxNMJ / 100))

                                if nb_pers == 1 and solo[0].get('PolitiquePrix', None) is not None:
                                    tauxSolo = int(solo[0]['PolitiquePrix'][0]['Taux(%)'])
                                    prix_total = prix_total - (prix * (tauxSolo / 100))

                                qt = str(quantite - 1)
                                update = MONGO.db.hotels.update_one({'Nom': db_response['Nom'],
                                                            'Chambres.Categorie': categorie},
                                                           {'$set': {'Chambres.$.Quantite': qt}})
                                LOG.debug(update)
                            else:
                                message = message + 'Trop de personne pour cette chambre ' + categorie + '. '
                        else:
                            message = message + 'Nous avons plus cette chambre: ' + categorie + '. '
                    else:
                        message = message + ' Cette chambre ' + categorie + ' n existe pas' + '. '

                if prix_total > 0:
                    for element in services:
                        categori = element['Categorie']
                        service = MONGO.db.hotels.find({'Nom': db_response['Nom']},
                                                       {'Services': {'$elemMatch': {'Categorie': categori}}})
                        LOG.debug(service)
                        if service[0].get('Services', None) is not None:
                            quantit = int(service[0]['Services'][0]['Quantite'])
                            price = int(service[0]['Services'][0]['Prix($)'])
                            if quantit > 0:
                                prix_total = prix_total + price
                                qte = str(quantit - 1)
                                updateone = MONGO.db.hotels.update_one({'Nom': db_response['Nom'],
                                                            'Services.Categorie': categori},
                                                           {'$set': {'Services.$.Quantite': qte}})
                                LOG.debug(updateone)
                            else:
                                message = message + 'Nous avons plus ce service: ' + categori + '. '

                    nbJours = int(abs((dateFin - dateDebut).days))
                    prix_total = prix_total * nbJours
                    data['Reservations']['prix_total($)'] = str(prix_total)
                    data['Reservations']['NReservation'] = '1234'
                    data['Reservations']['Client'] = user['email']
                    new = MONGO.db.hotels.update_one(query, {'$push': data})
                    LOG.debug(new)
                    emailmsg = "We confirm your reservation Numero: 1234. "
                    msg = Message(emailmsg, recipients=[user['email']])
                    msg.body = "Welcome to MyBookingService. Your reservation are confirm. "
                    mail = MAIL.send(msg)
                    LOG.debug(mail)
                    return jsonify({'ok': True, 'message': message + 'You will receive mail confirmation. Total '
                                                                     'price: ' + str(prix_total) + '$. '}), 200
                else:
                    return jsonify({'ok': False, 'message': message + ' You reservation is empty. Please retry. '}), 409
            else:
                return jsonify({'ok': False, 'message': 'Bad request parameters! '}), 400

        if request.method == 'DELETE':
            if data.get('query', {}) != {}:
                data['query']['Reservations.Client'] = user['email']
                data['payload']['Reservations']['Client'] = user['email']
                data['query']['Nom'] = db_response['Nom']
                reservations = MONGO.db.hotels.find({'Nom': data['query']['Nom']},
                                                    {'Reservations': {'$elemMatch': data['payload']['Reservations']}})
                LOG.debug(reservations)
                if reservations[0].get('Reservations', None) is not None:
                    chambresRes = reservations[0]['Reservations'][0]['Chambres']
                    servicesRes = reservations[0]['Reservations'][0]['Services']

                    for cham in chambresRes:
                        room = MONGO.db.hotels.find({'Nom': data['query']['Nom']},
                                                    {'Chambres': {'$elemMatch': {'Categorie': cham['Categorie']}}})
                        LOG.debug(room)
                        quantiteNew = str(int(room[0]['Chambres'][0]['Quantite']) + 1)
                        hotelupdate = MONGO.db.hotels.update_one({'Nom': data['query']['Nom'],
                                                    'Chambres.Categorie': cham['Categorie']},
                                                   {'$set': {'Chambres.$.Quantite': quantiteNew}})
                        LOG.debug(hotelupdate)
                    for serv in servicesRes:
                        serviceOld = MONGO.db.hotels.find({'Nom': data['query']['Nom']},
                                                          {'Services': {
                                                              '$elemMatch': {'Categorie': serv['Categorie']}}})
                        LOG.debug(serviceOld)
                        quantiteNewSer = str(int(serviceOld[0]['Services'][0]['Quantite']) + 1)
                        qt = MONGO.db.hotels.update_one({'Nom': data['query']['Nom'],
                                                    'Services.Categorie': serv['Categorie']},
                                                   {'$set': {'Services.$.Quantite': quantiteNewSer}})
                        LOG.debug(qt)
                    delete = MONGO.db.hotels.update_one(data['query'], {'$pull': data.get('payload', {})})
                    LOG.debug(delete)
                    return jsonify({'ok': True, 'message': 'Reservation deleted. '}), 200
                else:
                    return jsonify({'ok': False, 'message': 'Reservation not existed. '}), 409
            else:
                return jsonify({'ok': False, 'message': 'Bad request parameters! '}), 400
    else:
        return jsonify({'ok': False, 'message': 'Hotel not found or paramaters not found in /reservation?Nom=??.'}), 409


@MODULE_RESERVATIONS.route('/byUser/', methods=['GET'])
@jwt_required
def reservationbyUser():
    user = get_jwt_identity()
    query = request.args
    if request.method == 'GET':
        db_response = MONGO.db.hotels.find_one(query)
        LOG.debug(db_response)
        if db_response:
            chambre = MONGO.db.hotels.find(query, {'Reservations': {'$elemMatch': {'Client': user['email']}}})
            LOG.debug(chambre)
            return dumps(chambre, skipkeys=True, allow_nan=True, indent=6), 200
        else:
            return jsonify({'ok': False, 'message': 'Hotel not found. '}), 409
    else:
        return jsonify({'ok': False, 'message': 'Bad request parameters! '}), 400
