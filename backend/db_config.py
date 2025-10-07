from pymongo import MongoClient
import urllib.parse

# ===================================================================
# INSERISCI QUI I TUOI DATI PRESI DA ATLAS
# ===================================================================
USERNAME_DA_ATLAS = "simone_writer"  # <-- METTI QUI L'USERNAME CORRETTO
PASSWORD_DA_ATLAS = "rTSCLM484h1RBc3j" # <-- METTI QUI LA PASSWORD CORRETTA
HOST_DA_ATLAS = "cluster0.j5px3lo.mongodb.net" # <-- METTI QUI L'HOST CORRETTO
# ===================================================================

encoded_password = urllib.parse.quote_plus(PASSWORD_DA_ATLAS)
uri = f"mongodb+srv://{USERNAME_DA_ATLAS}:{encoded_password}@{HOST_DA_ATLAS}/?retryWrites=true&w=majority&appName=Cluster0"

print("Tentativo di connessione a MongoDB Atlas...")

client = None
try:
    client = MongoClient(uri)
    client.admin.command('ping')
    print("✅ Connessione a MongoDB riuscita!")

    # Seleziona il tuo database 'db1' e la collezione 'Carrello'
    db = client['db1']
    collection = db['Carrello']

    documento_da_inserire = {
        "prodotto": "Pane Casereccio",
        "quantita": 2,
        "inserito_da_script": True
    }

    risultato = collection.insert_one(documento_da_inserire)
    print(f"✅ Documento inserito con successo in 'db1.Carrello'! ID: {risultato.inserted_id}")

except Exception as e:
    print(f"❌ ERRORE: {e}")

finally:
    if client:
        client.close()
        print("Connessione chiusa.")