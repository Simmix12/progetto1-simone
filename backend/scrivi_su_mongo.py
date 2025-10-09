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
import requests
import json 

# <-- PARTE AGGIUNTA 1: Import per Gemini e gestione .env file -->
import google.generativeai as genai
from dotenv import load_dotenv
# <-- FINE PARTE AGGINTA 1 -->

# --- 1. CONFIGURAZIONE ---

# <-- PARTE AGGIUNTA 2: Carica le variabili dal file .env -->
load_dotenv()
# <-- FINE PARTE AGGIUNTA 2 -->

app = Flask(__name__, static_folder='static', static_url_path='/static')
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
utenti_collection = db['utenti']
newsletter_collection = db['newsletter']  # <-- NUOVA COLLECTION

# <-- PARTE AGGIUNTA 3: Configurazione del modello AI Gemini -->
try:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if not GEMINI_API_KEY:
        raise ValueError("Chiave API di Gemini non trovata. Assicurati di aver creato un file .env")
    
    genai.configure(api_key=GEMINI_API_KEY)
    # --- MODIFICA: Utilizzo del modello 'gemini-2.0-flash' ---
    model = genai.GenerativeModel('gemini-2.0-flash')
    print("✅ Modello AI Gemini (2.0 Flash) configurato con successo!")
except Exception as e:
    print(f"❌ ERRORE di configurazione Gemini: {e}")
    exit()
# <-- FINE PARTE AGGIUNTA 3 -->


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
            quantita = item.get('quantita')
            
            if not all(k in item for k in ['id', 'nome', 'prezzo_lordo', 'categoria', 'quantita']):
                raise ValueError("Dati del prodotto incompleti nel carrello.")

            prodotto = Prodotto(
                id=item.get('id'),
                nome=item.get('nome'),
                prezzo_lordo=item.get('prezzo_lordo'),
                categoria=item.get('categoria')
            )

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

# === NUOVA ROTTA PER LA NEWSLETTER ===
@app.route('/api/newsletter/subscribe', methods=['POST'])
def subscribe_newsletter():
    try:
        data = request.json
        if not data or 'email' not in data:
            return jsonify({"error": "Email richiesta"}), 400

        email = data['email'].strip().lower()
        source = data.get('source', 'website_footer')

        # Validazione email
        import re
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            return jsonify({"error": "Indirizzo email non valido"}), 400

        # Controlla se l'email è già registrata
        existing_subscriber = newsletter_collection.find_one({"email": email})
        if existing_subscriber:
            return jsonify({"error": "Questa email è già iscritta alla newsletter"}), 409

        # Salva il nuovo iscritto
        new_subscriber = {
            "email": email,
            "source": source,
            "subscription_date": datetime.now(),
            "active": True,
            "ip_address": request.remote_addr
        }

        result = newsletter_collection.insert_one(new_subscriber)
        
        print(f"✅ Nuova iscrizione newsletter: {email}")

        return jsonify({
            "success": True,
            "message": "Iscrizione alla newsletter completata con successo!",
            "subscriber_id": str(result.inserted_id)
        }), 201

    except Exception as e:
        print(f"❌ Errore durante l'iscrizione alla newsletter: {e}")
        return jsonify({"error": "Errore interno del server durante l'iscrizione"}), 500

@app.route('/api/prodotti', methods=['GET'])
def get_prodotti():
    prodotti_list = []
    for p in prodotti_collection.find({}):
        prodotti_list.append({
            "id": str(p["_id"]),
            "nome": p["nome"],
            "prezzo_lordo": p["prezzo_lordo"],
            "categoria": p.get("categoria", "Altro"),
            "immagine_url": p.get("immagine_url", ""),
            "descrizione": p.get("descrizione", "Nessuna descrizione disponibile per questo prodotto.")
        })
    return jsonify(prodotti_list)

@app.route('/api/prodotti', methods=['POST'])
def add_prodotto():
    data = request.json
    if not data or 'nome' not in data or 'prezzo_lordo' not in data:
        return jsonify({"errore": "Dati mancanti."}), 400
    try:
        nuovo_prodotto = {
            "nome": data["nome"],
            "prezzo_lordo": float(data["prezzo_lordo"]),
            "categoria": data.get("categoria", "Altro"),
            "immagine_url": data.get("immagine_url", ""),
            "descrizione": data.get("descrizione", "")
        }
        result = prodotti_collection.insert_one(nuovo_prodotto)
        nuovo_prodotto["id"] = str(result.inserted_id)
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
    data = request.json
    if not data or 'username' not in data or 'password' not in data or 'email' not in data:
        return jsonify({"errore": "Username, email e password sono richiesti."}), 400

    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if utenti_collection.find_one({"username": username}):
        return jsonify({"errore": f"L'utente '{username}' esiste già."}), 409
    
    if utenti_collection.find_one({"email": email}):
        return jsonify({"errore": f"L'email '{email}' è già in uso."}), 409

    try:
        password_hash = generate_password_hash(password, method='pbkdf2:sha256')
        nuovo_utente = {
            "username": username,
            "email": email,
            "password_hash": password_hash,
            "data_registrazione": datetime.now()
        }
        result = utenti_collection.insert_one(nuovo_utente)
        return jsonify({
            "messaggio": "Registrazione effettuata con successo!",
            "utente": {
                "id": str(result.inserted_id),
                "username": username,
                "email": email
            }
        }), 201
    except Exception as e:
        print(f"Errore in fase di registrazione: {e}")
        return jsonify({"errore": "Errore interno durante la creazione dell'account."}), 500

@app.route('/api/login', methods=['POST'])
def login_utente():
    data = request.json
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"errore": "Username e password sono richiesti."}), 400

    username = data.get('username')
    password = data.get('password')
    utente_db = utenti_collection.find_one({"username": username})

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
        
        profilo_data = utente.get("profilo", {})
        return jsonify(profilo_data)

    except Exception as e:
        return jsonify({"errore": str(e)}), 500

@app.route('/api/profilo/<user_id>', methods=['PUT'])
def update_profilo(user_id):
    try:
        data = request.json
        if not data:
            return jsonify({"errore": "Nessun dato fornito per l'aggiornamento."}), 400
            
        update_fields = {}
        campi_permessi = {
            "nome": "profilo.nome", "cognome": "profilo.cognome",
            "via": "profilo.indirizzo.via", "citta": "profilo.indirizzo.citta",
            "cap": "profilo.indirizzo.cap", "provincia": "profilo.indirizzo.provincia",
            "lat": "profilo.geolocalizzazione.lat", "lon": "profilo.geolocalizzazione.lon"
        }
        for key, value in data.items():
            if key in campi_permessi:
                update_fields[campi_permessi[key]] = value

        if not update_fields:
            return jsonify({"errore": "Nessun campo valido fornito per l'aggiornamento."}), 400

        if any(k in data for k in ["via", "citta", "cap", "provincia"]):
            indirizzo_completo = f"{data.get('via', '')}, {data.get('citta', '')}, {data.get('cap', '')}, {data.get('provincia', '')}"
            
            nominatim_url = "https://nominatim.openstreetmap.org/search"
            params = {'q': indirizzo_completo, 'format': 'json'}
            headers = {'User-Agent': 'MioEcommerceApp/1.0 (mioemail@example.com)'}

            try:
                response = requests.get(nominatim_url, params=params, headers=headers)
                response.raise_for_status()
                results = response.json()

                if results:
                    location = results[0]
                    update_fields["profilo.geolocalizzazione.lat"] = float(location["lat"])
                    update_fields["profilo.geolocalizzazione.lon"] = float(location["lon"])
                    print(f"✅ Geolocalizzazione (Nominatim) riuscita per {indirizzo_completo}")
                else:
                    print(f"⚠️ Geolocalizzazione (Nominatim) fallita per {indirizzo_completo}: Indirizzo non trovato.")
            except requests.exceptions.RequestException as e:
                print(f"❌ Errore nella chiamata a Nominatim: {e}")

        result = utenti_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_fields}
        )

        if result.matched_count == 0:
            return jsonify({"errore": "Utente non trovato."}), 404

        utente_aggiornato = utenti_collection.find_one({"_id": ObjectId(user_id)})
        profilo_aggiornato = utente_aggiornato.get("profilo", {})

        return jsonify({
            "messaggio": "Profilo aggiornato con successo!",
            "profilo": profilo_aggiornato
        })

    except Exception as e:
        return jsonify({"errore": str(e)}), 500

@app.route('/api/profilo/<user_id>/change-password', methods=['PUT'])
def change_password(user_id):
    try:
        data = request.json
        current_password = data.get('current_password')
        new_password = data.get('new_password')

        if not current_password or not new_password:
            return jsonify({"errore": "Password attuale e nuova sono richieste."}), 400
        
        utente = utenti_collection.find_one({"_id": ObjectId(user_id)})
        if not utente:
            return jsonify({"errore": "Utente non trovato."}), 404

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
    carrello_data = request.json
    try:
        scontrino_calcolato = calcolatore.genera_scontrino(carrello_data)
        return jsonify(asdict(scontrino_calcolato))
    except (ValueError, TypeError) as e:
        return jsonify({"errore": str(e)}), 400
    except Exception as e:
        print(f"Errore non gestito: {e}")
        return jsonify({"errore": "Errore interno del server"}), 500

@app.route('/api/chat', methods=['POST'])
def handle_chat():
    data = request.json
    if not data or 'message' not in data:
        return jsonify({"error": "Messaggio mancante"}), 400

    user_message = data['message']
    ai_response = "Spiacente, si è verificato un errore."

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
        
        intent_response = model.generate_content(intent_prompt)
        intent_json_str = intent_response.text.strip().replace("```json", "").replace("```", "")
        intent_data = json.loads(intent_json_str)
        
        intenzione = intent_data.get("intenzione")
        
        context_data = ""
        if intenzione == "cerca_prodotto" and "nome" in intent_data:
            query = {"nome": {"$regex": intent_data["nome"], "$options": "i"}}
            prodotti_trovati = list(prodotti_collection.find(query))
            if prodotti_trovati:
                context_data = "Informazioni sui prodotti trovati nel database:\n"
                for p in prodotti_trovati:
                    context_data += f"- Nome: {p['nome']}, Prezzo: {p['prezzo_lordo']:.2f}€, Descrizione: {p.get('descrizione', 'N/D')}\n"
            else:
                context_data = "Nessun prodotto trovato con quel nome nel database."

        elif intenzione == "elenca_categoria" and "categoria" in intent_data:
            query = {"categoria": intent_data["categoria"]}
            prodotti_trovati = list(prodotti_collection.find(query))
            if prodotti_trovati:
                context_data = f"Elenco dei prodotti nella categoria '{intent_data['categoria']}':\n"
                for p in produtos_trovati:
                    context_data += f"- {p['nome']} a {p['prezzo_lordo']:.2f}€\n"
            else:
                context_data = f"Nessun prodotto trovato nella categoria '{intent_data['categoria']}'."
        
        if context_data:
            final_prompt = f"""
            Sei un assistente virtuale amichevole di un e-commerce.
            Usa ESCLUSIVAMENTE le seguenti informazioni di contesto per rispondere alla domanda dell'utente.
            Non inventare informazioni.
            Contesto:
            {context_data}
            Domanda dell'utente: "{user_message}"
            """
            final_response = model.generate_content(final_prompt)
            ai_response = final_response.text
        else:
            final_prompt = f"Rispondi in modo conciso e diretto come un assistente virtuale per un sito di e-commerce. Domanda dell'utente: '{user_message}'"
            final_response = model.generate_content(final_prompt)
            ai_response = final_response.text

        return jsonify({"reply": ai_response})

    except Exception as e:
        print(f"❌ ERRORE durante la chiamata a Gemini o elaborazione: {e}")
        return jsonify({"error": "Errore nella comunicazione con l'assistente AI"}), 500

# --- 5. POPOLAMENTO INIZIALE ---

def popola_db_mongo():
    if prodotti_collection.count_documents({}) > 0:
        prodotti_collection.delete_many({})
        print("🧹 Collezione 'prodotti' pulita.")

    if prodotti_collection.count_documents({}) == 0:
        print("Collezione 'prodotti' vuota. Popolamento in corso...")
        prodotti_da_inserire = [
    # Alimentari (IVA 4%)
    { "nome": "Pane Casereccio", "prezzo_lordo": 2.41, "categoria": "Alimentari", "immagine_url": "pane.jpg", "descrizione": "Immagina il profumo del pane appena sfornato che riempie la cucina. Questo è il nostro pane casereccio: una crosta dorata e croccante che scrocchia al primo morso, rivelando una mollica morbida e alveolata. Fatto come una volta, con lievito madre e una lenta lievitazione che gli conferisce un sapore rustico e inconfondibile." },
    { "nome": "Latte Intero 1L", "prezzo_lordo": 1.59, "categoria": "Alimentari", "immagine_url": "latte.jpg", "descrizione": "Questo non è un latte qualsiasi. È il latte fresco e cremoso che sa di buono, proveniente da stalle selezionate dove il benessere animale è al primo posto. Il suo gusto pieno e genuino lo rende perfetto per iniziare la giornata, per un cappuccino vellutato o come ingrediente segreto per rendere le tue torte ancora più soffici." },
    { "nome": "Uova Fresche (6)", "prezzo_lordo": 2.95, "categoria": "Alimentari", "immagine_url": "uova.jpg", "descrizione": "Direttamente da galline felici, libere di razzolare a terra, queste uova hanno un tuorlo di un colore giallo intenso che parla da solo. Sono l'ingrediente che fa la differenza in ogni ricetta: perfette per una carbonara cremosa, un uovo all'occhio di bue dal sapore ricco o una frittata alta e saporita." },
    { "nome": "Pasta di Semola 500g", "prezzo_lordo": 0.89, "categoria": "Alimentari", "immagine_url": "pasta.jpg", "descrizione": "La vera pasta della domenica, ma perfetta per ogni giorno. Prodotta con il miglior grano duro italiano e trafilata al bronzo, la sua superficie ruvida e porosa è fatta apposta per catturare ogni goccia di sugo. Sentirai la differenza sotto i denti: una consistenza sempre al dente." },
    { "nome": "Mela Rossa (1kg)", "prezzo_lordo": 1.80, "categoria": "Alimentari", "immagine_url": "mela.jpg", "descrizione": "Croccanti, succose e piene di sapore. Queste mele rosse sono lo spuntino sano per eccellenza. Ogni morso è un'esplosione di freschezza, con un equilibrio perfetto tra dolcezza e una punta di acidità, che ti ricarica di energia e benessere." },
    { "nome": "Olio Extra Vergine (1L)", "prezzo_lordo": 6.99, "categoria": "Alimentari", "immagine_url": "olio.jpg", "descrizione": "Un filo di quest'olio a crudo è pura poesia. Ottenuto dalla prima spremitura a freddo di olive selezionate, ha un carattere deciso, con note fruttate e un piacevole pizzicore finale che ne certifica la qualità. È l'anima della cucina mediterranea." },
    { "nome": "Caffè Macinato (250g)", "prezzo_lordo": 3.49, "categoria": "Alimentari", "immagine_url": "caffe.jpg", "descrizione": "Apri la confezione e lasciati avvolgere da un aroma intenso che sa di casa e di risvegli felici. Questa miscela 100% Arabica, macinata alla perfezione per la moka, regala un caffè equilibrato e vellutato, senza retrogusto amaro. La piccola coccola quotidiana che ti dà la carica." },
    { "nome": "Marmellata di Fragole", "prezzo_lordo": 2.15, "categoria": "Alimentari", "immagine_url": "marmellata.jpg", "descrizione": "Dimentica le marmellate industriali. Questa è fatta con il 70% di fragole fresche, come quella che preparava la nonna. Dentro ci trovi i pezzi di frutta, un profumo inebriante e un sapore autentico e non troppo dolce. Deliziosa sul pane tostato o con lo yogurt." },
    { "nome": "Tonno in Olio (3 scatolette)", "prezzo_lordo": 4.50, "categoria": "Alimentari", "immagine_url": "tonno.jpg", "descrizione": "Filetti di tonno compatti e saporiti, così teneri che si sciolgono in bocca. Non è il solito tonno sbriciolato, ma pezzi interi conservati in un ottimo olio d'oliva che ne esalta il gusto. Perfetto per un'insalata ricca o un sugo veloce." },
    { "nome": "Acqua Minerale Naturale (6x1.5L)", "prezzo_lordo": 1.95, "categoria": "Alimentari", "immagine_url": "acqua.jpg", "descrizione": "Leggera e pura, quest'acqua oligominerale è la tua alleata di benessere quotidiano. Sgorga da una fonte protetta, mantenendo intatte tutte le sue preziose proprietà. È l'idratazione perfetta per tutta la famiglia, con un gusto delicato e un residuo fisso basso." },
    
    # Medicinali (IVA 10%)
    { "nome": "Oki (antidol.)", "prezzo_lordo": 4.99, "categoria": "Medicinali", "immagine_url": "oki.jpg", "descrizione": "Un alleato fidato e veloce contro mal di testa, dolori muscolari o mestruali. La sua formula agisce rapidamente per darti sollievo proprio quando ne hai più bisogno. Le pratiche bustine monodose sono perfette da tenere in borsa o in ufficio." },
    { "nome": "Termometro Digitale", "prezzo_lordo": 8.90, "categoria": "Medicinali", "immagine_url": "termometro.jpg", "descrizione": "L'essenziale che non può mancare in nessuna casa. Facilissimo da usare, ti dà una lettura della temperatura precisa e affidabile in pochi secondi, senza l'ansia del vecchio mercurio. Il display digitale è chiaro e di facile lettura." },
    { "nome": "Cerotti Assortiti (20 pz)", "prezzo_lordo": 3.20, "categoria": "Medicinali", "immagine_url": "cerotti.jpg", "descrizione": "Perché i piccoli incidenti capitano, questo kit è la soluzione a portata di mano. Contiene cerotti di ogni forma e misura, perfetti per le dita o le ginocchia. Sono ipoallergenici e traspiranti, per proteggere la ferita e far respirare la pelle." },
    { "nome": "Spray Nasale", "prezzo_lordo": 5.50, "categoria": "Medicinali", "immagine_url": "spray.jpg", "descrizione": "Quando il raffreddore ti chiude il naso, questo spray è una vera boccata d'aria fresca. La sua soluzione ipertonica aiuta a liberare le vie respiratorie in modo naturale e delicato, offrendo un sollievo immediato dalla congestione per tornare a respirare liberamente." },
    { "nome": "Integratore Vitamina C (30 compresse)", "prezzo_lordo": 9.20, "categoria": "Medicinali", "immagine_url": "vitamina_c.jpg", "descrizione": "Il tuo scudo quotidiano per rafforzare le difese immunitarie. Con 1000mg di Vitamina C per compressa, è un potente supporto per il tuo organismo, specialmente durante i cambi di stagione o nei periodi di maggiore stress. Ti aiuta a combattere stanchezza e affaticamento." },
    { "nome": "Garze Sterili (10x10, 10 pz)", "prezzo_lordo": 2.50, "categoria": "Medicinali", "immagine_url": "garze.jpg", "descrizione": "Un prodotto fondamentale per la medicazione di piccole ferite. Morbide, super assorbenti e confezionate singolarmente per garantire la massima igiene e sterilità. Realizzate in tessuto che non si attacca alla ferita, rendendo il cambio più semplice." },
    { "nome": "Bende Elastiche", "prezzo_lordo": 4.10, "categoria": "Medicinali", "immagine_url": "benda.jpg", "descrizione": "Che si tratti di una leggera distorsione o di un affaticamento muscolare, questa benda offre il giusto supporto senza bloccare i movimenti. Il suo tessuto elastico e traspirante si adatta perfettamente al corpo, fornendo una compressione confortevole e stabile." },
    { "nome": "Sciroppo Tosse Secca", "prezzo_lordo": 6.80, "categoria": "Medicinali", "immagine_url": "sciroppo.jpg", "descrizione": "Quella tosse secca e fastidiosa che non ti dà tregua, soprattutto di notte, ha trovato il suo nemico. Questo sciroppo agisce creando un film protettivo che calma l'irritazione della gola, dando un sollievo immediato e duraturo." },

    # Altro (IVA 22%)
    { "nome": "Agenda 2024", "prezzo_lordo": 15.50, "categoria": "Altro", "immagine_url": "agenda.png", "descrizione": "Più di una semplice agenda, è il tuo assistente personale. Con una copertina elegante e pagine di alta qualità su cui la penna scorre che è un piacere, ti aiuta a tenere sotto controllo ogni impegno. La sua struttura intelligente ti permette di organizzare il tempo con stile." },
    { "nome": "Shampoo Neutro", "prezzo_lordo": 3.80, "categoria": "Altro", "immagine_url": "shampoo.jpg", "descrizione": "Uno shampoo delicato che si prende cura dei tuoi capelli giorno dopo giorno. La sua formula bilanciata è adatta a tutta la famiglia e a lavaggi frequenti, perché pulisce a fondo senza aggredire la cute. Lascia i capelli morbidi, leggeri e luminosi." },
    { "nome": "Quaderno a Righe", "prezzo_lordo": 1.99, "categoria": "Altro", "immagine_url": "quaderno.jpg", "descrizione": "La pagina a righe di un nuovo progetto. Che tu sia uno studente o un professionista, questo quaderno è il compagno ideale per i tuoi appunti. La carta spessa evita che l'inchiostro trapassi e la copertina robusta protegge le tue idee." },
    { "nome": "Penna Gel Nera", "prezzo_lordo": 1.20, "categoria": "Altro", "immagine_url": "penna.jpg", "descrizione": "Scopri il piacere di una scrittura fluida e senza interruzioni. L'inchiostro gel scivola sul foglio con facilità, lasciando un tratto nero, intenso e preciso che si asciuga in un attimo. L'impugnatura comoda la rende perfetta per lunghe sessioni di scrittura." },
    { "nome": "Detersivo Lavatrice (1.5L)", "prezzo_lordo": 7.30, "categoria": "Altro", "immagine_url": "detersivo.jpg", "descrizione": "Un pulito impeccabile e un profumo di bucato che sa di fresco e di casa. Questo detersivo concentrato è potente contro le macchie più ostinate, anche a basse temperature, rispettando i colori e i tessuti. Meno prodotto, più pulito." },
    { "nome": "Lampadina LED E27", "prezzo_lordo": 4.50, "categoria": "Altro", "immagine_url": "lampadina.jpg", "descrizione": "Illumina i tuoi spazi con una luce calda e accogliente, simile a quella di una volta, ma con un consumo energetico irrisorio. Dura anni, facendoti risparmiare sulla bolletta e riducendo gli sprechi. La scelta intelligente per la tua casa." },
    { "nome": "Carta Igienica (4 rotoli)", "prezzo_lordo": 2.55, "categoria": "Altro", "immagine_url": "carta_igienica.jpg", "descrizione": "Una piccola coccola quotidiana a cui non si può rinunciare. Realizzata con tre veli di pura cellulosa, offre una morbidezza eccezionale unita a una sorprendente resistenza. La garanzia di un comfort superiore per te e la tua famiglia." },
    { "nome": "Set Cacciaviti (6 pezzi)", "prezzo_lordo": 18.90, "categoria": "Altro", "immagine_url": "cacciaviti.jpg", "descrizione": "Il kit indispensabile per ogni piccolo lavoro di casa. Le impugnature ergonomiche ti offrono una presa salda e comoda, mentre le punte magnetiche sono un aiuto geniale per non perdere mai le viti. Un set robusto e affidabile che durerà nel tempo." },
    { "nome": "Mouse Ottico USB", "prezzo_lordo": 9.99, "categoria": "Altro", "immagine_url": "mouse.jpg", "descrizione": "Preciso, affidabile e pronto all'uso. Basta collegare il cavo USB e sei subito operativo. Il suo sensore ottico garantisce un controllo del cursore fluido e reattivo, mentre il design ambidestro lo rende comodo per ore di navigazione senza sforzo." },
    { "nome": "Batterie Alcaline AA (4 pz)", "prezzo_lordo": 3.90, "categoria": "Altro", "immagine_url": "batterie.jpg", "descrizione": "L'energia affidabile per tutti i tuoi dispositivi. Dai telecomandi ai giocattoli dei bambini, queste batterie alcaline garantiscono una lunga durata e una performance costante. La tranquillità di sapere che funzioneranno sempre quando ne avrai bisogno." }
]
        prodotti_collection.insert_many(prodotti_da_inserire)
        print("✅ Database MongoDB popolato con prodotti di esempio (lista estesa).")
    else:
        print("Database MongoDB ('prodotti') già popolato.")

def popola_utenti_mongo():
    if utenti_collection.count_documents({}) == 0:
        print("Collezione 'utenti' vuota. Popolamento in corso...")
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
    print("Avvio del server Flask su http://127.0.0.1:5000")
    app.run(debug=True)