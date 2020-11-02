#Run 

Les commandes pour exécuter:

sudo systemctl start mongd
source venv/bien/activate
export FLASK_APP=/API/index.py
python3 index.py 

cd test_fonctionnel : 
sudo newman run MyBookingService.json

cd modules
python3 -m pytest -v tests/




