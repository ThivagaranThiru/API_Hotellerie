# API Hôtelerie

Le porteur du projet, une grande chaîne d'hôtellerie, souhaite mettre en place un système unique de réservation pour tous les hôtels et tous les canaux de ventes (téléphonique, accueil, site internet, application mobile).

L'objectif est de mettre en place une API de réservation hôtelière avec les fonctionnalités suivantes : Réservation de chambres, nombre de personnes par chambre réservée, petit-déjeuner, annulation des réservations, garage, lit bébé, wifi ...

Les Besoins (cf Présentation.pdf):

- Un système de réservation de chambre, commun à tous ces hôtels (ex : une API pour tous les hôtels).

- Un CRUD pour les chambres par hôtels.

- Un CRUD sur la gestion des prix des chambres (selon les catégories de chambre (suite,
standard, ...), des services additionnels et la politique des prix).

- Une confirmation par mail pour une réservation de chambre.

- Ajouter un nouveau hôtel avec ces mêmes fonctionnalités.

- Un CRUD Utilisateur et un système d'Authentification	


API and SDK Documentation : /Swagger Mock & Documentation/html2-documentation-generated/index.html

API Mock : https://app.swaggerhub.com/apis/MyBookingServices/DevOps_Cloud/1.0.0#trial

           https://app.swaggerhub.com/apis-docs/MyBookingServices/DevOps_Cloud/1.0.0#/


Technologies utilisées : Python3, Framework Flask (flask_pymongo, flask_mail, flask_jwt_extended & flask_bcryp), MongoDB, Swagger, Postman, PyTest (Test Unitaire) et Newman (Test Fonctionnel).




