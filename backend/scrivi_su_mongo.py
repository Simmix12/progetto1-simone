import os
import math
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
import urllib.parse
from dataclasses import dataclass, asdict
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# --- 1. CONFIGURAZIONE ---

app = Flask(__name__)
CORS(app)

USERNAME_DA_ATLAS = "simone_writer"
PASSWORD_DA_ATLAS = "EMTBPD3eTXfhq6pp"
HOST_DA_ATLAS = "cluster0.j5px3lo.mongodb.net"
encoded_password = urllib.parse.quote_plus(PASSWORD_DA_ATLAS)
uri = f"mongodb+srv://{USERNAME_DA_ATLAS}:{encoded_password}@{HOST_DA_ATLAS}/?retryWrites=true&w=majority&appName=Cluster0"

try:
    client = MongoClient(uri)
    client.admin.command('ping')
    print("✅ Connessione a MongoDB riuscita!")
except Exception as e:
    print(f"❌ ERRORE di connessione a MongoDB: {e}")
    exit()

db = client['db1']
prodotti_collection = db['prodotti']
scontrini_collection = db['scontrini']
# Collezione per gli utenti
utenti_collection = db['utenti']


# --- 2. MODELLI ---
ALIQUOTE_IVA = { "Alimentari": 4.0, "Medicinali": 10.0, "Altro": 22.0 }
@dataclass
class Prodotto:
    id: str
    nome: str
    prezzo_lordo: float
    categoria: str
@dataclass
class VoceScontrino:
    nome_prodotto: str
    quantita: int
    prezzo_totale: float
@dataclass
class Scontrino:
    voci: list[VoceScontrino]
    totale_iva: float
    totale_complessivo: float
    data_creazione: str


# --- 3. LOGICA DI CALCOLO ---
class CalcolatoreScontrino:
    def _arrotonda_a_0_05(self, prezzo):
        return math.floor(prezzo * 20) / 20.0
    def calcola_prezzo_finale_singolo(self, prodotto: Prodotto):
        aliquota = ALIQUOTE_IVA.get(prodotto.categoria, 22.0)
        prezzo_ivato = prodotto.prezzo_lordo * (1 + aliquota / 100)
        return self._arrotonda_a_0_05(prezzo_ivato)
    def genera_scontrino(self, carrello: list[dict]):
        voci_scontrino = []
        totale_complessivo = 0.0
        totale_lordo_complessivo = 0.0
        for item in carrello:
            prodotto_id = item.get('id')
            quantita = item.get('quantita')
            prodotto_doc = prodotti_collection.find_one({"_id": ObjectId(prodotto_id)})
            if not prodotto_doc:
                raise ValueError(f"Prodotto con ID {prodotto_id} non trovato.")
            prodotto = Prodotto(id=str(prodotto_doc["_id"]), nome=prodotto_doc["nome"], prezzo_lordo=prodotto_doc["prezzo_lordo"], categoria=prodotto_doc["categoria"])
            prezzo_unitario_finale = self.calcola_prezzo_finale_singolo(prodotto)
            prezzo_riga = round(prezzo_unitario_finale * quantita, 2)
            voci_scontrino.append(VoceScontrino(nome_prodotto=prodotto.nome, quantita=quantita, prezzo_totale=prezzo_riga))
            totale_complessivo += prezzo_riga
            totale_lordo_complessivo += prodotto.prezzo_lordo * quantita
        totale_iva = round(totale_complessivo - totale_lordo_complessivo, 2)
        scontrino_generato = Scontrino(voci=voci_scontrino, totale_iva=totale_iva, totale_complessivo=round(totale_complessivo, 2), data_creazione=datetime.now().isoformat())
        scontrino_dict = asdict(scontrino_generato)
        scontrini_collection.insert_one(scontrino_dict)
        print(f"✅ Scontrino salvato su MongoDB con successo!")
        return scontrino_generato


# --- 4. ROTTE DELL'API ---
calcolatore = CalcolatoreScontrino()

@app.route('/api/prodotti', methods=['GET'])
def get_prodotti():
    prodotti_list = []
    for p in prodotti_collection.find({}):
        prodotti_list.append({ "id": str(p["_id"]), "nome": p["nome"], "prezzo_lordo": p["prezzo_lordo"] })
    return jsonify(prodotti_list)

@app.route('/api/prodotti', methods=['POST'])
def add_prodotto():
    data = request.json
    if not data or 'nome' not in data or 'prezzo_lordo' not in data:
        return jsonify({"errore": "Dati mancanti."}), 400
    try:
        nuovo_prodotto = { "nome": data["nome"], "prezzo_lordo": float(data["prezzo_lordo"]), "categoria": data.get("categoria", "Altro") }
        result = prodotti_collection.insert_one(nuovo_prodotto)
        nuovo_prodotto["id"] = str(result.inserted_id)
        del nuovo_prodotto["_id"]
        return jsonify(nuovo_prodotto), 201
    except Exception as e:
        return jsonify({"errore": str(e)}), 500

# ##############################################
# # ROTTA PER LA REGISTRAZIONE
# ##############################################
@app.route('/api/register', methods=['POST'])
def registra_utente():
    """Gestisce la registrazione di un nuovo utente."""
    data = request.json
    # 1. Validazione base dei dati
    if not data or 'username' not in data or 'password' not in data or 'email' not in data:
        return jsonify({"errore": "Username, email e password sono richiesti."}), 400

    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    # 2. Controllo duplicati (username o email)
    if utenti_collection.find_one({"username": username}):
        return jsonify({"errore": f"L'utente '{username}' esiste già."}), 409 # 409 Conflict
    
    if utenti_collection.find_one({"email": email}):
        return jsonify({"errore": f"L'email '{email}' è già in uso."}), 409

    try:
        # 3. Hash della password per la sicurezza
        password_hash = generate_password_hash(password, method='pbkdf2:sha256')

        nuovo_utente = {
            "username": username,
            "email": email,
            "password_hash": password_hash,
            "data_registrazione": datetime.now()
        }

        # 4. Salvataggio su MongoDB
        result = utenti_collection.insert_one(nuovo_utente)
        
        # 5. Risposta di successo (Logga automaticamente l'utente)
        return jsonify({
            "messaggio": "Registrazione effettuata con successo!",
            "utente": {
                "id": str(result.inserted_id),
                "username": username
            }
        }), 201 # 201 Created
        
    except Exception as e:
        print(f"Errore in fase di registrazione: {e}")
        return jsonify({"errore": "Errore interno durante la creazione dell'account."}), 500


# ##############################################
# # ROTTA PER IL LOGIN
# ##############################################
@app.route('/api/login', methods=['POST'])
def login_utente():
    """Gestisce il tentativo di login."""
    data = request.json
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"errore": "Username e password sono richiesti."}), 400

    username = data.get('username')
    password = data.get('password')

    utente_db = utenti_collection.find_one({"username": username})

    # Controlla se l'utente esiste E se la password hashata corrisponde
    if utente_db and check_password_hash(utente_db['password_hash'], password):
        # Login successful!
        return jsonify({
            "messaggio": "Login effettuato con successo!",
            "utente": {
                "id": str(utente_db["_id"]),
                "username": utente_db["username"]
            }
        })
    else:
        # Utente non trovato o password errata
        return jsonify({"errore": "Credenziali non valide. Riprova o crea un account."}), 401

@app.route('/api/scontrino', methods=['POST'])
def handle_scontrino():
    carrello_data = request.json
    try:
        scontrino_calcolato = calcolatore.genera_scontrino(carrello_data)
        return jsonify(asdict(scontrino_calcolato))
    except (ValueError, TypeError) as e:
        return jsonify({"errore": str(e)}), 400
    except Exception as e:
        print(f"Errore non gestito: {e}")
        return jsonify({"errore": "Errore interno del server"}), 500


# --- 5. POPOLAMENTO INIZIALE ---

def popola_db_mongo():
    if prodotti_collection.count_documents({}) == 0:
        print("Collezione 'prodotti' vuota. Popolamento in corso...")
        prodotti_da_inserire = [
            {"nome": "Pane Casereccio", "prezzo_lordo": 2.41, "categoria": "Alimentari"},
            {"nome": "Agenda 2024", "prezzo_lordo": 15.50, "categoria": "Altro"},
            {"nome": "Oki (antidol.)", "prezzo_lordo": 4.99, "categoria": "Medicinali"},
            {"nome": "Latte Intero 1L", "prezzo_lordo": 1.59, "categoria": "Alimentari"},
            {"nome": "Termometro Digitale", "prezzo_lordo": 8.90, "categoria": "Medicinali"},
            {"nome": "Shampoo Neutro", "prezzo_lordo": 3.80, "categoria": "Altro"},
        ]
        prodotti_collection.insert_many(prodotti_da_inserire)
        print("✅ Database MongoDB popolato con prodotti di esempio.")
    else:
        print("Database MongoDB ('prodotti') già popolato.")

def popola_utenti_mongo():
    """Crea un utente di esempio se la collezione è vuota."""
    if utenti_collection.count_documents({}) == 0:
        print("Collezione 'utenti' vuota. Popolamento in corso...")
        utenti_da_inserire = [
            {
                "username": "mario.rossi",
                "email": "mario.rossi@example.com",
                # La password è "password123". generate_password_hash la cripta.
                "password_hash": generate_password_hash("password123", method='pbkdf2:sha256')
            },
            {
                "username": "anna.verdi",
                "email": "anna.verdi@example.com",
                "password_hash": generate_password_hash("qwerty", method='pbkdf2:sha256')
            }
        ]
        utenti_collection.insert_many(utenti_da_inserire)
        print("✅ Database MongoDB popolato con utenti di esempio.")
    else:
        print("Database MongoDB ('utenti') già popolato.")


if __name__ == '__main__':
    popola_db_mongo()
    popola_utenti_mongo()
    print("Avvio del server Flask su http://127.0.0.1:5000")
    app.run(debug=True)