from faker import Faker

fake = Faker('fr_FR')

name = fake.last_name()
email = fake.email()
password = fake.password()
number = fake.building_number()
HEADERS = ''
HEADERS1 = ''
hotel = {
    "Nom": "Hotel " + number,
    "Description": "Le Plaza Athenee avec ses 5 etoiles",
    "Address": "25, avenue Montaigne, 75008 Paris",
    "Telephone": "0153676665",
    "Chambres": [
        {
            "Categorie": "Suite",
            "Prix($)": "720",
            "Max_Pers": "3",
            "Indice": "S",
            "Quantite": "1"
        },
        {
            "Categorie": "Junior Suite",
            "Prix($)": "500",
            "Max_Pers": "2",
            "Indice": "JS",
            "Quantite": "1"
        },
        {
            "Categorie": "Chambre de luxe",
            "Prix($)": "300",
            "Max_Pers": "2",
            "Indice": "CD",
            "Quantite": "1"
        },
        {
            "Categorie": "Chambre standard",
            "Prix($)": "150",
            "Max_Pers": "2",
            "Indice": "CS",
            "Quantite": 2
        }
    ],
    "Services": [
        {
            "Categorie": "Place de garage",
            "Prix($)": "25",
            "Quantite": "3"
        },
        {
            "Categorie": "Lit bebe",
            "Prix($)": "0",
            "Quantite": "2"
        }
    ],
    "PolitiquePrix": [
        {
            "Categorie": "Nuit Vendredi et Samedi",
            "Facture": "Majorer",
            "Taux(%)": "15",
            "Indice": "NVS"
        },
        {
            "Categorie": "Nuit Mercredi et Jeudi",
            "Facture": "Minorer",
            "Taux(%)": "10",
            "Indice": "NMJ"
        },
        {
            "Categorie": "Solo",
            "Facture": "Minorer",
            "Taux(%)": "5",
            "Indice": "S"
        }
    ],
    "Reservations": [
    ]
}

reservation = {
    "Reservations": {
        "DateDebut": "22/07/2020",
        "DateFin": "23/07/2020",
        "Chambres": [
            {
                "Categorie": "Suite",
                "Pers": "1"
            },
            {
                "Categorie": "Junior Suite",
                "Pers": "1"
            }
        ],
        "Services": [
            {
                "Categorie": "Place de garage"
            }
        ]
    }
}


def test_register_users(client):
    response = client.post('user/register',
                           json={
                               'nom': name,
                               'email': email,
                               'password': password
                           })
    assert response.status_code == 200


def test_register_bad_request_users(client):
    response = client.post('user/register',
                           json={
                               'name': name,
                               'email': email,
                               'password': password
                           })
    assert response.status_code == 400


def test_register_email_exist_users(client):
    response = client.post('user/register',
                           json={
                               'nom': name,
                               'email': email,
                               'password': password
                           })
    assert response.status_code == 409


def test_auth_user(client):
    response = client.post('user/auth',
                           json={
                               'email': email,
                               'password': password
                           })

    token = response.json['data']['token']
    global HEADERS
    HEADERS = {
        'Authorization': 'Bearer {}'.format(token)
    }
    assert response.status_code == 200


def test_auth_bad_request_user(client):
    response = client.post('user/auth',
                           json={
                               'mail': email,
                               'password': password
                           })

    assert response.status_code == 400


def test_auth_user_invalid_user(client):
    response = client.post('user/auth',
                           json={
                               'email': email,
                               'password': 'password'
                           })

    assert response.status_code == 401


def test_get_unauthorized_user(client):
    response = client.get('user/')

    assert response.status_code == 401


def test_get_user(client):
    response = client.get('user/', headers=HEADERS)

    assert response.status_code == 200


def test_put_bad_request_user(client):
    response = client.put('user/',
                          json={
                              "queryc": {
                              },
                              "payload": {
                                  'password': 'password'
                              }
                          },
                          headers=HEADERS)

    assert response.status_code == 400


def test_post_hotel(client):
    response = client.post('hotel/', json=hotel, headers=HEADERS)

    assert response.status_code == 200


def test_post_exist_hotel(client):
    response = client.post('hotel/', json=hotel, headers=HEADERS)

    assert response.status_code == 409


def test_post_element_hotel(client):
    response = client.post('hotel/', json={
        "query": {
            "Nom": "Hotel " + number
        },
        "payload": {
            "Services": {
                "Categorie": "Un lit en plus",
                "Price": "50$",
                "Quantite": "5"
            }
        }
    }, headers=HEADERS)

    assert response.status_code == 200


def test_put_element_hotel(client):
    response = client.put('hotel/', json={
        "query": {
            "Nom": "Hotel " + number,
            "Services.Categorie": "Place de garage"
        },
        "payload": {
            "Services.$.Quantite": "20"
        }
    }, headers=HEADERS)

    assert response.status_code == 200


def test_put_hotel(client):
    response = client.put('hotel/', json={
        "query": {
            "Nom": "Hotel " + number
        },
        "payload": {
            "Description": "La desciption a été modifié"
        }
    }, headers=HEADERS)

    assert response.status_code == 200


def test_delete_element_hotel(client):
    response = client.delete('hotel/', json={
        "query": {
            "Nom": "Hotel " + number,
            "Services.Categorie": "Lit bebe"
        },
        "payload": {
            "Services": {
                "Categorie": "Lit bebe"
            }
        }
    }, headers=HEADERS)

    assert response.status_code == 200


def test_get_unauthorized_hotel(client):
    response = client.get('hotel/')

    assert response.status_code == 401


def test_get_hotel(client):
    response = client.get('hotel/', headers=HEADERS)

    assert response.status_code == 200


def test_delete_unauthorized_hotel(client):
    response = client.delete('hotel/', json={"Nom": "Hotel 0"}, headers=HEADERS)

    assert response.status_code == 401


def test_logout_user(client):
    response = client.delete('user/logout', headers=HEADERS)

    assert response.status_code == 200


def test_register_client_users(client):
    response = client.post('user/register',
                           json={
                               'nom': 'test',
                               'email': 'thiruc_t@etna-alternance.net',
                               'password': 'client'
                           })
    assert response.status_code == 200


def test_auth_client_user(client):
    response = client.post('user/auth',
                           json={
                               'email': 'thiruc_t@etna-alternance.net',
                               'password': 'client'
                           })

    token = response.json['data']['token']
    global HEADERS1
    HEADERS1 = {
        'Authorization': 'Bearer {}'.format(token)
    }
    assert response.status_code == 200


def test_param_not_exit_reservation(client):
    response = client.get('reservation/', headers=HEADERS1)

    assert response.status_code == 409


def test_get_reservation(client):
    response = client.get('reservation/?Nom=Hotel ' + number, headers=HEADERS1)

    assert response.status_code == 200


def test_post_reservation(client):
    response = client.post('reservation/?Nom=Hotel ' + number, json=reservation, headers=HEADERS1)

    assert response.status_code == 200


def test_post_not_reservation(client):
    response = client.post('reservation/?Nom=Hotel ' + number, json=reservation, headers=HEADERS1)

    assert response.status_code == 409

def test_get_user_reservation(client):
    response = client.get('reservation/byUser/?Nom=Hotel ' + number, headers=HEADERS1)

    assert response.status_code == 200

def test_delete_not_exit_reservation(client):
    response = client.delete('reservation/?Nom=Hotel ' + number, json={
        "query": {
            "Reservations.NReservation": "12345"
        },
        "payload": {
            "Reservations": {
                "NReservation": "12345"
            }
        }
    }, headers=HEADERS1)

    assert response.status_code == 409

def test_delete_reservation(client):
    response = client.delete('reservation/?Nom=Hotel ' + number, json={
        "query": {
            "Reservations.NReservation": "1234"
        },
        "payload": {
            "Reservations": {
                "NReservation": "1234"
            }
        }
    }, headers=HEADERS1)

    assert response.status_code == 200

def test_delete_user(client):

    response = client.delete('user/', headers=HEADERS1)

    assert response.status_code == 200

def test_auth1_user(client):
    response = client.post('user/auth',
                           json={
                               'email': email,
                               'password': password
                           })

    token = response.json['data']['token']
    global HEADERS
    HEADERS = {
        'Authorization': 'Bearer {}'.format(token)
    }
    assert response.status_code == 200

def test_delete_hotel(client):
    response = client.delete('hotel/', json={"Nom": "Hotel " + number}, headers=HEADERS)

    assert response.status_code == 200

def test_put_user(client):
    response = client.put('user/',
                          json={
                              "query": {
                              },
                              "payload": {
                                  'password': 'password'
                              }
                          },
                          headers=HEADERS)

    assert response.status_code == 200
