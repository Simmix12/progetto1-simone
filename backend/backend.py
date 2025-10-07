import math
import os
from dataclasses import dataclass, asdict
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

# --- CONFIGURAZIONE DELL'APPLICAZIONE E DEL DATABASE ---
app = Flask(__name__)
# CORS permette la comunicazione con il frontend Svelte che gira su un'altra porta
CORS(app) 

# Configurazione del database SQLite
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ==============================================================================
# MODELLI DEL DATABASE
# ==============================================================================

class Categoria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), unique=True, nullable=False)
    aliquota_iva = db.Column(db.Float, nullable=False)
    prodotti = db.relationship('Prodotto', backref='categoria', lazy=True)

class Prodotto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    prezzo_lordo = db.Column(db.Float, nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categoria.id'), nullable=False)

# Dataclass per una risposta JSON strutturata
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

# ==============================================================================
# LOGICA DI CALCOLO
# ==============================================================================

class CalcolatoreScontrino:
    def _arrotonda_a_0_05(self, prezzo):
        return math.floor(prezzo * 20) / 20.0

    def calcola_prezzo_finale_singolo(self, prodotto: Prodotto):
        prezzo_ivato = prodotto.prezzo_lordo * (1 + prodotto.categoria.aliquota_iva / 100)
        prezzo_finale = self._arrotonda_a_0_05(prezzo_ivato)
        if prezzo_finale < prodotto.prezzo_lordo:
             raise ValueError(f"Errore di calcolo per {prodotto.nome}: il prezzo finale ({prezzo_finale}) è inferiore al lordo ({prodotto.prezzo_lordo}).")
        return prezzo_finale

    def genera_scontrino(self, carrello: list[dict]):
        voci_scontrino = []
        totale_complessivo = 0.0
        totale_lordo_complessivo = 0.0

        for item in carrello:
            prodotto_id = item.get('id') 
            quantita = item.get('quantita')
            
            if not prodotto_id or not quantita:
                raise ValueError("Ogni item del carrello deve avere 'id' e 'quantita'.")

            prodotto = Prodotto.query.get(prodotto_id)
            if not prodotto:
                raise ValueError(f"Prodotto con ID {prodotto_id} non trovato.")

            prezzo_unitario_finale = self.calcola_prezzo_finale_singolo(prodotto)
            prezzo_riga = round(prezzo_unitario_finale * quantita, 2)
            
            voci_scontrino.append(VoceScontrino(
                nome_prodotto=prodotto.nome,
                quantita=quantita,
                prezzo_totale=prezzo_riga
            ))
            
            totale_complessivo += prezzo_riga
            totale_lordo_complessivo += prodotto.prezzo_lordo * quantita
        
        totale_iva = round(totale_complessivo - totale_lordo_complessivo, 2)
        totale_complessivo = round(totale_complessivo, 2)
        
        return Scontrino(
            voci=voci_scontrino,
            totale_iva=totale_iva,
            totale_complessivo=totale_complessivo
        )

# ==============================================================================
# ROTTE DELL'API
# ==============================================================================

calcolatore = CalcolatoreScontrino()

@app.route('/api/prodotti', methods=['GET'])
def get_prodotti():
    """Fornisce al frontend la lista completa dei prodotti dal database."""
    prodotti_list = Prodotto.query.all()
    prodotti_json = [
        {"id": p.id, "nome": p.nome, "prezzo_lordo": p.prezzo_lordo}
        for p in prodotti_list
    ]
    return jsonify(prodotti_json)

@app.route('/api/scontrino', methods=['POST'])
def handle_scontrino():
    """Riceve il carrello dal frontend, calcola lo scontrino e lo restituisce."""
    carrello_data = request.json
    if not carrello_data or not isinstance(carrello_data, list):
        return jsonify({"errore": "Il corpo della richiesta deve essere una lista (carrello)."}), 400

    try:
        scontrino_calcolato = calcolatore.genera_scontrino(carrello_data)
        return jsonify(asdict(scontrino_calcolato))
    except ValueError as e:
        return jsonify({"errore": str(e)}), 400
    except Exception as e:
        print(f"Errore non gestito: {e}") # Log per il debug
        return jsonify({"errore": "Errore interno del server"}), 500

def popola_db():
    """Funzione helper per creare e popolare il DB con dati di esempio."""
    print("Popolamento del database con dati iniziali...")
    
    db.create_all()

    # Creazione Categorie
    cat_alimentari = Categoria(nome="Alimentari", aliquota_iva=4.0)
    cat_medicinali = Categoria(nome="Medicinali", aliquota_iva=10.0)
    cat_altro = Categoria(nome="Altro", aliquota_iva=22.0)
    db.session.add_all([cat_alimentari, cat_medicinali, cat_altro])
    db.session.commit()

    # Creazione Prodotti
    prodotti_da_inserire = [
        Prodotto(nome="Pane Casereccio", prezzo_lordo=2.41, categoria=cat_alimentari),
        Prodotto(nome="Agenda 2024", prezzo_lordo=15.50, categoria=cat_altro),
        Prodotto(nome="Oki (antidolorifico)", prezzo_lordo=4.99, categoria=cat_medicinali),
        Prodotto(nome="Latte Intero 1L", prezzo_lordo=1.59, categoria=cat_alimentari),
        Prodotto(nome="Termometro Digitale", prezzo_lordo=8.90, categoria=cat_medicinali),
        Prodotto(nome="Shampoo Neutro", prezzo_lordo=3.80, categoria=cat_altro),
        Prodotto(nome="Barretta Proteica", prezzo_lordo=1.99, categoria=cat_alimentari),
    ]
    db.session.add_all(prodotti_da_inserire)
    db.session.commit()
    print("Database popolato con successo.")


if __name__ == '__main__':
    with app.app_context():
        # Crea e popola il database solo se non esiste già.
        if not os.path.exists(os.path.join(basedir, 'database.db')):
            print("Database non trovato. Creazione in corso...")
            popola_db()
        else:
            print("Database esistente trovato.")

    print("Avvio del server Flask su http://127.0.0.1:5000")
    app.run(debug=True)