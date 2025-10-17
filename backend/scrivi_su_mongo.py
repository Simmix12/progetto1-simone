import os
import math
import json
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
import urllib.parse
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
import requests
import google.generativeai as genai


#Carica le variabili d'ambiente (file .env)
load_dotenv()

# Creazione di un'istanza dell'applicazione Flask. '__name__' 
# 'static_folder' e 'static_url_path' configurano come servire i file statici (es. immagini, CSS).
app = Flask(__name__, static_folder='static', static_url_path='/static')
# abilitazione cors, permettendo al frontend (su un altro dominio) di fare richieste all'API.
CORS(app)

USERNAME_DA_ATLAS = "simone_writer"
PASSWORD_DA_ATLAS = "EMTBPD3eTXfhq6pp"
HOST_DA_ATLAS = "cluster0.j5px3lo.mongodb.net"
# Codifica la password per connessione (es. sostituisce '@' con '%40').
encoded_password = urllib.parse.quote_plus(PASSWORD_DA_ATLAS)

uri = f"mongodb+srv://{USERNAME_DA_ATLAS}:{encoded_password}@{HOST_DA_ATLAS}/?retryWrites=true&w=majority&appName=Cluster0"


try: #connesione a mongo
    client = MongoClient(uri)
    client.admin.command('ping')
    print("✅ Connessione a MongoDB riuscita!")
except Exception as e:
    print(f"❌ ERRORE di connessione a MongoDB: {e}")
    exit()


db = client['db1']
prodotti_collection = db['prodotti']
scontrini_collection = db['scontrini']
utenti_collection = db['utenti']
newsletter_collection = db['newsletter']

#configurazione gemini
try:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if not GEMINI_API_KEY:
        raise ValueError("Chiave API di Gemini non trovata. Assicurati di aver creato un file .env")

    # configurazione della libreria 'genai' con la chiave API fornita.
    genai.configure(api_key=GEMINI_API_KEY)
    #scelta modello da utilizzare
    model = genai.GenerativeModel('gemini-1.5-flash')
    print("✅ Modello AI Gemini (1.5 Flash) configurato con successo!")
except Exception as e:
    print(f"❌ ERRORE di configurazione Gemini: {e}")
    exit()

# --- MODELLI ---
# Definiamo  un dizionario per l'iva
ALIQUOTE_IVA = {"Alimentari": 4.0, "Medicinali": 10.0, "Altro": 22.0}


@dataclass
class Prodotto:
    # Definisce gli attributi della classe 'Prodotto' con i rispettivi tipi.
    id: str  
    nome: str  
    prezzo_lordo: float  
    categoria: str  
    immagine_url: str = "" 
    descrizione: str = ""  


@dataclass
class VoceScontrino:
   
    nome_prodotto: str  
    quantita: int  
    prezzo_totale: float  


@dataclass
class Scontrino:
    
    voci: List[VoceScontrino]  
    totale_iva: float  
    totale_complessivo: float  
    data_creazione: str  
    user_id: str  

class CalcolatoreScontrino:
    
    def _arrotonda_a_0_05(self, prezzo):
        # Moltiplica per 20, tronca all'intero inferiore, e poi divide per 20. Es: 1.28 -> 1.25.
        return math.floor(prezzo * 20) / 20.0

   
    def calcola_prezzo_finale_singolo(self, prodotto: Prodotto):
        # Ottiene l'aliquota IVA dal dizionario. Se la categoria non esiste, usa il 22% come default.
        aliquota = ALIQUOTE_IVA.get(prodotto.categoria, 22.0)
        prezzo_ivato = prodotto.prezzo_lordo * (1 + aliquota / 100)
        return self._arrotonda_a_0_05(prezzo_ivato)

    def genera_scontrino(self, carrello: List[dict], user_id: str):
        voci_scontrino = []  # Lista per le righe dello scontrino.
        totale_complessivo = 0.0  
        totale_lordo_complessivo = 0.0 

        if not carrello:
           
            raise ValueError("Il carrello non può essere vuoto.")

        # Itera su ogni elemento (prodotto e quantità) presente nel carrello.
        for item in carrello:
            # Estrae la quantità dall'dizionario dell'item.
            quantita = item.get('quantita')

            # Controlla che tutte le chiavi necessarie siano presenti nell'item del carrello.
            if not all(k in item for k in ['id', 'nome', 'prezzo_lordo', 'categoria', 'quantita']):
                # Se mancano dati, solleva un errore.
                raise ValueError("Dati del prodotto incompleti nel carrello.")
            
            # Crea un'istanza della classe 'Prodotto' con i dati presi dal carrello.
            prodotto = Prodotto(
                id=item.get('id'),
                nome=item.get('nome'),
                prezzo_lordo=item.get('prezzo_lordo'),
                categoria=item.get('categoria')
            )
            
            # Calcola il prezzo finale per una singola unità del prodotto.
            prezzo_unitario_finale = self.calcola_prezzo_finale_singolo(prodotto)
            # Calcola il prezzo totale per la riga (prezzo unitario * quantità) e lo arrotonda a 2 cifre decimali.
            prezzo_riga = round(prezzo_unitario_finale * quantita, 2)

            # Aggiunge una nuova 'VoceScontrino' alla lista delle voci.
            voci_scontrino.append(VoceScontrino(
                nome_prodotto=prodotto.nome, 
                quantita=quantita, 
                prezzo_totale=prezzo_riga
            ))

            # Aggiorna il totale complessivo dello scontrino.//aggiunta iva per prodotto
            totale_complessivo += prezzo_riga
            # Aggiorna il totale lordo (senza IVA) per calcolare l'IVA totale alla fine.
            totale_lordo_complessivo += prodotto.prezzo_lordo * quantita

        # Calcola l'IVA totale come differenza tra totale finale e totale lordo, e arrotonda.
        totale_iva = round(totale_complessivo - totale_lordo_complessivo, 2)
        
        # Crea l'oggetto 'Scontrino' finale con tutti i dati calcolati.
        scontrino_generato = Scontrino(
            voci=voci_scontrino,
            totale_iva=totale_iva,
            totale_complessivo=round(totale_complessivo, 2),
            data_creazione=datetime.now().isoformat(), # Ottiene la data/ora attuale in formato standard.
            user_id=user_id
        )

        # Converte l'oggetto 'Scontrino' in un dizionario per poterlo salvare su MongoDB.
        scontrino_dict = asdict(scontrino_generato)
        # Inserisce il dizionario dello scontrino nella collection 'scontrini' del database.
        scontrini_collection.insert_one(scontrino_dict)
        
        print(f"✅ Scontrino per l'utente {user_id} salvato su MongoDB con successo!")
        return scontrino_generato#oggetto scontrino


#  calcolatore che verrà usata dalle rotte API.
calcolatore = CalcolatoreScontrino()


@app.route('/api/prodotti', methods=['GET'])

def get_prodotti():
    # Inizializza una lista vuota 
    prodotti_list = []
    # Itera su ogni documento trovato nella collection 'prodotti'.
    for p in prodotti_collection.find({}):
        # Aggiunge alla lista un dizionario con i dati del prodotto
        prodotti_list.append({
            "id": str(p["_id"]), # Converte l'ObjectId di MongoDB in una stringa.
            "nome": p["nome"],
            "prezzo_lordo": p["prezzo_lordo"],
            "categoria": p.get("categoria", "Altro"), # Usa 'Altro' se non è specificata.
            "immagine_url": p.get("immagine_url", ""), # Usa una stringa vuota se l'URL non è specificato.
            "descrizione": p.get("descrizione", "Nessuna descrizione disponibile per questo prodotto.") # Usa una descrizione di default.
        })
    # Restituisce la lista di prodotti in formato JSON.
    return jsonify(prodotti_list)


@app.route('/api/prodotti', methods=['POST'])

def add_prodotto():
    #ottiene dati
    data = request.json
    # Controlla se i dati necessari  sono presenti.
    if not data or 'nome' not in data or 'prezzo_lordo' not in data:
        
        return jsonify({"errore": "Dati mancanti."}), 400
    
    try:
        # Crea un dizionario per il nuovo prodotto con i dati ricevuti.
        nuovo_prodotto = {
            "nome": data["nome"],
            "prezzo_lordo": float(data["prezzo_lordo"]),
            "categoria": data.get("categoria", "Altro"),
            "immagine_url": data.get("immagine_url", ""),
            "descrizione": data.get("descrizione", "")
        }
       
        result = prodotti_collection.insert_one(nuovo_prodotto)
        # Aggiunge l'ID generato da MongoDB al dizionario del prodotto.
        nuovo_prodotto["id"] = str(result.inserted_id)
        # Restituisce i dati del prodotto appena creato con uno status 201 (Created).
        return jsonify({
            "id": nuovo_prodotto["id"],
            "nome": nuovo_prodotto["nome"],
            "prezzo_lordo": nuovo_prodotto["prezzo_lordo"],
            "categoria": nuovo_prodotto["categoria"],
            "immagine_url": nuovo_prodotto["immagine_url"],
            "descrizione": nuovo_prodotto["descrizione"]
        }), 201
    
    except Exception as e:
        
        return jsonify({"errore": str(e)}), 500

@app.route('/api/register', methods=['POST'])
def registra_utente():
    # Ottiene i dati 
    data = request.json
    
    if not data or 'username' not in data or 'password' not in data or 'email' not in data:
        return jsonify({"errore": "Username, email e password sono richiesti."}), 400

    # Estrae i dati dalla richiesta.
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if utenti_collection.find_one({"username": username}):
        return jsonify({"errore": f"L'utente '{username}' esiste già."}), 409

    if utenti_collection.find_one({"email": email}):
        return jsonify({"errore": f"L'email '{email}' è già in uso."}), 409
    
    # Inizia il blocco per la creazione dell'utente.
    try:
        # Crea un hash sicuro della password.
        password_hash = generate_password_hash(password, method='pbkdf2:sha256')
        # Crea il dizionario del nuovo utente da inserire nel DB.
        nuovo_utente = {
            "username": username,
            "email": email,
            "password_hash": password_hash, # Salva l'hash, non la password in chiaro.
            "data_registrazione": datetime.now()
        }
        result = utenti_collection.insert_one(nuovo_utente)
        #resistituisce messaggio di successo
        return jsonify({
            "messaggio": "Registrazione effettuata con successo!",
            "utente": {
                "id": str(result.inserted_id),
                "username": username,
                "email": email
            }
        }), 201
    # Gestisce eventuali errori durante il processo.
    except Exception as e:
        print(f"Errore in fase di registrazione: {e}")
        return jsonify({"errore": "Errore interno durante la creazione dell'account."}), 500

@app.route('/api/login', methods=['POST'])
def login_utente():
    # Ottiene i dati JSON.
    data = request.json
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"errore": "Username e password sono richiesti."}), 400

    # Estrae username e password.
    username = data.get('username')
    password = data.get('password')
    # Cerca l'utente nel database tramite l'username.
    utente_db = utenti_collection.find_one({"username": username})

    # Controlla se l'utente è stato trovato e se la password fornita corrisponde all'hash salvato.
    if utente_db and check_password_hash(utente_db['password_hash'], password):
        return jsonify({
            "messaggio": "Login effettuato con successo!",
            "utente": {
                "id": str(utente_db["_id"]),
                "username": utente_db["username"],
                "email": utente_db.get("email")
            }
        })
    else:
        return jsonify({"errore": "Credenziali non valide. Riprova o crea un account."}), 401

@app.route('/api/profilo/<user_id>', methods=['GET'])
def get_profilo(user_id):
    try:
        utente = utenti_collection.find_one({"_id": ObjectId(user_id)})
        if not utente:
            return jsonify({"errore": "Utente non trovato"}), 404

        # Estrae i dati del profilo dall'oggetto utente
        profilo_data = utente.get("profilo", {})
        return jsonify(profilo_data)

    # Gestisce eventuali eccezioni.
    except Exception as e:
        return jsonify({"errore": str(e)}), 500

@app.route('/api/profilo/<user_id>', methods=['PUT'])
def update_profilo(user_id):
    try:
        #ottiene dati
        data = request.json
        if not data:
            return jsonify({"errore": "Nessun dato fornito per l'aggiornamento."}), 400

        # Dizionario per contenere i campi da aggiornare
        update_fields = {}
        #inserimento campi
        campi_permessi = {
            "nome": "profilo.nome", "cognome": "profilo.cognome",
            "via": "profilo.indirizzo.via", "citta": "profilo.indirizzo.citta",
            "cap": "profilo.indirizzo.cap", "provincia": "profilo.indirizzo.provincia",
            "lat": "profilo.geolocalizzazione.lat", "lon": "profilo.geolocalizzazione.lon"
        }
        # Itera sui dati ricevuti (chiave, valore).
        for key, value in data.items():
            # Controlla se la chiave è una di quelle permesse per l'aggiornamento.
            if key in campi_permessi:
                # Se è permessa, la aggiunge al dizionario dei campi da aggiornare.
                update_fields[campi_permessi[key]] = value

        if not update_fields:
            return jsonify({"errore": "Nessun campo valido fornito per l'aggiornamento."}), 400
        
        # Controlla se è stato fornito almeno un campo dell'indirizzo.
        if any(k in data for k in ["via", "citta", "cap", "provincia"]):
            # Compone la stringa dell'indirizzo completo per la geolocalizzazione.
            indirizzo_completo = f"{data.get('via', '')}, {data.get('citta', '')}, {data.get('cap', '')}, {data.get('provincia', '')}"

            nominatim_url = "https://nominatim.openstreetmap.org/search"
            # Parametri per la richiesta dell'indirizzo
            params = {'q': indirizzo_completo, 'format': 'json'}
            # L'header 'User-Agent' è richiesto dalla policy di Nominatim per identificare l'applicazione.
            headers = {'User-Agent': 'MioEcommerceApp/1.0 (mioemail@example.com)'}
            
            #
            try:
                # Effettua richiesta Nominatim.
                response = requests.get(nominatim_url, params=params, headers=headers)
                # eccezione se la risposta ha un codice di stato di errore
                response.raise_for_status()
                # Converte la risposta JSON in un oggetto Python.
                results = response.json()
                #se ci sono risultati
                if results:
                    # prende il risultato più rilevante (di solito è il primo)
                    location = results[0]
                    # Aggiunge latitudine e longitudine al dizionario dei campi da aggiornare.
                    update_fields["profilo.geolocalizzazione.lat"] = float(location["lat"])
                    update_fields["profilo.geolocalizzazione.lon"] = float(location["lon"])
                    print(f"✅ Geolocalizzazione (Nominatim) riuscita per {indirizzo_completo}")
                #non trovato
                else:
                    print(f"⚠️ Geolocalizzazione (Nominatim) fallita per {indirizzo_completo}: Indirizzo non trovato.")
            except requests.exceptions.RequestException as e:
                print(f"❌ Errore nella chiamata a Nominatim: {e}")

        # aggiornamento su mongo
        result = utenti_collection.update_one(
            {"_id": ObjectId(user_id)}, # trova utente
            {"$set": update_fields} # aggiornamento 
        )

        # Controlla se un documento è stato effettivamente trovato e aggiornato.
        if result.matched_count == 0:
            return jsonify({"errore": "Utente non trovato."}), 404

        # Recupera l'utente aggiornato per restituire i nuovi dati del profilo.
        utente_aggiornato = utenti_collection.find_one({"_id": ObjectId(user_id)})
        # Estrae il profilo aggiornato.
        profilo_aggiornato = utente_aggiornato.get("profilo", {})

        # Restituisce un messaggio di successo e il profilo aggiornato.
        return jsonify({
            "messaggio": "Profilo aggiornato con successo!",
            "profilo": profilo_aggiornato
        })

    # Gestisce qualsiasi altra eccezione.
    except Exception as e:
        return jsonify({"errore": str(e)}), 500

@app.route('/api/profilo/<user_id>/change-password', methods=['PUT'])
def change_password(user_id):
    try: #ottieni dati
        data = request.json
        current_password = data.get('current_password')
        new_password = data.get('new_password')

        
        if not current_password or not new_password:
            return jsonify({"errore": "Password attuale e nuova sono richieste."}), 400

        # Cerca l'utente nel database.
        utente = utenti_collection.find_one({"_id": ObjectId(user_id)})
        if not utente:
            return jsonify({"errore": "Utente non trovato."}), 404
        #controllo pass fornite
        if not check_password_hash(utente['password_hash'], current_password):
            return jsonify({"errore": "La password attuale non è corretta."}), 403
        
        new_password_hash = generate_password_hash(new_password, method='pbkdf2:sha256')
        utenti_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"password_hash": new_password_hash}}
        )

        return jsonify({"messaggio": "Password aggiornata con successo!"})

    except Exception as e:
        print(f"Errore durante il cambio password: {e}")
        return jsonify({"errore": "Si è verificato un errore interno."}), 500

@app.route('/api/scontrino', methods=['POST'])
def handle_scontrino():
    data = request.json
    # Estrae i dati del carrello e l'ID dell'utente.
    carrello_data = data.get('carrello')
    user_id = data.get('userId')

    if not carrello_data or not user_id:
        return jsonify({"errore": "Dati del carrello o ID utente mancanti."}), 400

    try:
        #  generare lo scontrino.
        scontrino_calcolato = calcolatore.genera_scontrino(carrello_data, user_id)
        return jsonify(asdict(scontrino_calcolato))
    # Gestisce errori //es carrello vuoto
    except (ValueError, TypeError) as e:
        return jsonify({"errore": str(e)}), 400
    except Exception as e:
        print(f"Errore non gestito: {e}")
        return jsonify({"errore": "Errore interno del server"}), 500

@app.route('/api/chat', methods=['POST'])
def handle_chat():
    data = request.json
    #messaggio utente
    if not data or 'message' not in data:
        return jsonify({"error": "Messaggio mancante"}), 400

    # Estrae il messaggio dell'utente.
    user_message = data['message']
    # Imposta una risposta di default in caso di errore.
    ai_response = "Spiacente, si è verificato un errore."

    # Inizia un blocco try per l'interazione con l'AI.
    try:
        intent_prompt = f"""
        Analizza la richiesta dell'utente e classificala. Rispondi SOLO con un oggetto JSON.
        Le intenzioni possibili sono: "cerca_prodotto", "elenca_categoria", "info_generica".
        Le categorie possibili sono: "Alimentari", "Medicinali", "Altro".
        Estrai il nome del prodotto o della categoria se presenti.
        Esempi:
        - "avete le mele?" -> {{"intenzione": "cerca_prodotto", "nome": "mela"}}
        - "mostrami i medicinali" -> {{"intenzione": "elenca_categoria", "categoria": "Medicinali"}}
        - "ciao come stai?" -> {{"intenzione": "info_generica"}}
        Richiesta utente: "{user_message}"
        """
        #invio prompt
        intent_response = model.generate_content(intent_prompt)
        # Pulisce la risposta del modello per estrarre solo la stringa JSON (rimuove ```json e spazi).
        intent_json_str = intent_response.text.strip().replace("```json", "").replace("```", "")
        # Converte la stringa JSON in un dizionario Python.
        intent_data = json.loads(intent_json_str)

        # Estrae l'intenzione identificata.
        intenzione = intent_data.get("intenzione")

        # Inizializza una stringa per contenere i dati recuperati dal database, che serviranno da contesto per l'AI.
        context_data = ""
        # Se l'intenzione è cercare un prodotto e il nome è stato estratto...
        if intenzione == "cerca_prodotto" and "nome" in intent_data:
            # ...crea una query per MongoDB che cerca il nome in modo case-insensitive ($options: "i").
            query = {"nome": {"$regex": intent_data["nome"], "$options": "i"}}
            # Esegue la query e converte il risultato in una lista.
            prodotti_trovati = list(prodotti_collection.find(query))
            
            # Se sono stati trovati prodotti...
            if prodotti_trovati:
                # ...costruisce una stringa di contesto con le informazioni dei prodotti.
                context_data = "Informazioni sui prodotti trovati nel database:\n"
                for p in prodotti_trovati:
                    context_data += f"- Nome: {p['nome']}, Prezzo: {p['prezzo_lordo']:.2f}€, Descrizione: {p.get('descrizione', 'N/D')}\n"
            # Se non sono stati trovati prodotti...
            else:
                # ...imposta un messaggio di contesto appropriato.
                context_data = "Nessun prodotto trovato con quel nome nel database."
        
        # Se l'intenzione è elencare una categoria e la categoria è stata estratta...
        elif intenzione == "elenca_categoria" and "categoria" in intent_data:
            # ...crea una query per cercare tutti i prodotti di quella categoria.
            query = {"categoria": intent_data["categoria"]}
            # Esegue la query.
            prodotti_trovati = list(prodotti_collection.find(query))
            # Se sono stati trovati prodotti...
            if prodotti_trovati:
                # ...costruisce la stringa di contesto con l'elenco dei prodotti.
                context_data = f"Elenco dei prodotti nella categoria '{intent_data['categoria']}':\n"
                for p in prodotti_trovati:
                    context_data += f"- {p['nome']} a {p['prezzo_lordo']:.2f}€\n"
            # Se la categoria è vuota...
            else:
                # ...imposta il messaggio di contesto corrispondente.
                context_data = f"Nessun prodotto trovato nella categoria '{intent_data['categoria']}'."
        
        # Se è stato creato un contesto (cioè se sono state trovate informazioni nel DB)...
        if context_data:
            # ...costruisce un secondo prompt per Gemini, più specifico.
            final_prompt = f"""
            Sei un assistente virtuale amichevole di un e-commerce.
            Usa ESCLUSIVAMENTE le seguenti informazioni di contesto per rispondere alla domanda dell'utente.
            Non inventare informazioni.
            Contesto:
            {context_data}
            Domanda dell'utente: "{user_message}"
            """
            # Invia il prompt finale al modello.
            final_response = model.generate_content(final_prompt)
            # La risposta dell'AI sarà il testo generato dal modello.
            ai_response = final_response.text
        # Se non c'è contesto (es. richiesta generica come "ciao")...
        else:
            # ...invia un prompt generico al modello.
            final_prompt = f"Rispondi in modo conciso e diretto come un assistente virtuale per un sito di e-commerce. Domanda dell'utente: '{user_message}'"
            final_response = model.generate_content(final_prompt)
            ai_response = final_response.text

        # Restituisce la risposta dell'AI al frontend.
        return jsonify({"reply": ai_response})

    # Gestisce eventuali errori durante il processo.
    except Exception as e:
        print(f"❌ ERRORE durante la chiamata a Gemini o elaborazione: {e}")
        return jsonify({"error": "Errore nella comunicazione con l'assistente AI"}), 500

@app.route('/api/ordini/<user_id>', methods=['GET'])
def get_ordini_utente(user_id):
    try:
       #trova scontrini apaprtenenti ad un utente e gli ordina dal più nuovo al più vecchio
        ordini_cursor = scontrini_collection.find({"user_id": user_id}).sort("data_creazione", -1)
        ordini_list = []
        # Itera su ogni documento (ordine) restituito dalla query.
        for ordine in ordini_cursor:
            # Converte l'ObjectId in una stringa, necessario per la serializzazione in JSON.
            ordine['_id'] = str(ordine['_id'])
            # Aggiunge l'ordine alla lista.
            ordini_list.append(ordine)
        # Restituisce la lista degli ordini in formato JSON.
        return jsonify(ordini_list)

    # Gestisce eventuali errori.
    except Exception as e:
        print(f"❌ Errore nel recupero degli ordini per l'utente {user_id}: {e}")
        return jsonify({"errore": "Errore interno del server durante il recupero degli ordini."}), 500

# --- GESTIONE FAVICON ---
# Definisce una rotta per '/favicon.ico', richiesta automaticamente dai browser.
@app.route('/favicon.ico')
def favicon():
    # Inizia un blocco 'try' per gestire l'eventuale assenza del file.
    try:
        # Prova a inviare il file 'favicon.ico' dalla cartella statica definita nell'istanza di Flask.
        return app.send_static_file('favicon.ico')
    # Se si verifica un errore (es. FileNotFoundError)...
    except:
        # ...restituisce una risposta vuota con status 204 (No Content) per evitare errori 404 nel log.
        return '', 204

# Definisce una rotta per un'alternativa comune, '/favicon.png'.
@app.route('/favicon.png')
def favicon_png():
    # Inizia un blocco 'try'.
    try:
        # Prova a inviare il file 'favicon.png' dalla cartella statica.
        return app.send_static_file('favicon.png')
    # Se il file non viene trovato...
    except:
        # ...restituisce una risposta vuota con status 204.
        return '', 204

# --- POPOLAMENTO INIZIALE ---
# Definisce una funzione per popolare il database con prodotti di esempio all'avvio.
def popola_db_mongo():
    # Controlla se ci sono già dei documenti nella collection 'prodotti'.
    if prodotti_collection.count_documents({}) > 0:
        # Se la collection non è vuota, la svuota per garantire un ambiente di test pulito.
        prodotti_collection.delete_many({})
        # Stampa un messaggio per informare della pulizia.
        print("🧹 Collezione 'prodotti' pulita.")

    # Controlla di nuovo se la collection è vuota (per sicurezza o se era già vuota).
    if prodotti_collection.count_documents({}) == 0:
        # Stampa un messaggio che informa dell'inizio del popolamento.
        print("Collezione 'prodotti' vuota. Popolamento in corso...")
        # Definisce una lista di dizionari, ognuno rappresentante un prodotto da inserire.
        prodotti_da_inserire = [
            # ... (contenuto della lista dei prodotti, omesso per brevità)
            {"nome": "Pane Casereccio", "prezzo_lordo": 2.41, "categoria": "Alimentari", "immagine_url": "pane.jpg", "descrizione": "Descrizione del pane..."},
            {"nome": "Latte Intero 1L", "prezzo_lordo": 1.59, "categoria": "Alimentari", "immagine_url": "latte.jpg", "descrizione": "Descrizione del latte..."},
            # ... Aggiungere qui tutti gli altri prodotti della lista originale
            {"nome": "Batterie Alcaline AA (4 pz)", "prezzo_lordo": 3.90, "categoria": "Altro", "immagine_url": "batterie.jpg", "descrizione": "Descrizione delle batterie..."}
        ]
        # Inserisce tutti i prodotti della lista nel database con un'unica operazione.
        prodotti_collection.insert_many(prodotti_da_inserire)
        # Stampa un messaggio di conferma.
        print("✅ Database MongoDB popolato con prodotti di esempio (lista estesa).")
    # Se la collection era già popolata e non è stata pulita (logica non raggiunta con il codice attuale, ma per completezza)...
    else:
        # ...stampa un messaggio che informa che non è stato fatto nulla.
        print("Database MongoDB ('prodotti') già popolato.")

# Definisce una funzione per popolare il database con utenti di esempio.
def popola_utenti_mongo():
    # Controlla se la collection 'utenti' è vuota.
    if utenti_collection.count_documents({}) == 0:
        # Se è vuota, stampa un messaggio e procede al popolamento.
        print("Collezione 'utenti' vuota. Popolamento in corso...")
        # Definisce una lista di utenti di esempio, con le password già hashate.
        utenti_da_inserire = [
            {"username": "mario.rossi", "email": "mario.rossi@example.com", "password_hash": generate_password_hash("password123", method='pbkdf2:sha256')},
            {"username": "anna.verdi", "email": "anna.verdi@example.com", "password_hash": generate_password_hash("qwerty", method='pbkdf2:sha256')}
        ]
        utenti_collection.insert_many(utenti_da_inserire)
        print("✅ Database MongoDB popolato con utenti di esempio.")
    else:
        print("Database MongoDB ('utenti') già popolato.")

if __name__ == '__main__':
    popola_db_mongo()
    popola_utenti_mongo()
    print("Avvio del server Flask su [http://127.0.0.1:5000](http://127.0.0.1:5000)")
    app.run(debug=True)