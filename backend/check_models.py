import google.generativeai as genai
import os
from dotenv import load_dotenv

# Carica la tua chiave API dal file .env
load_dotenv()

try:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if not GEMINI_API_KEY:
        raise ValueError("Chiave API non trovata nel file .env")
        
    genai.configure(api_key=GEMINI_API_KEY)

    print("\nSto cercando i modelli disponibili per la tua chiave API...")
    print("---------------------------------------------------------")

    found_models = False
    for model in genai.list_models():
        # Controlliamo solo i modelli che supportano la generazione di testo
        if 'generateContent' in model.supported_generation_methods:
            print(model.name)
            found_models = True

    print("---------------------------------------------------------")
    if found_models:
        print("✅ Fatto! Copia uno dei nomi qui sopra (es. 'models/gemini-1.0-pro') e usalo nel tuo file principale.")
    else:
        print("❌ Nessun modello trovato. Controlla che la tua chiave API sia corretta e attiva.")

except Exception as e:
    print(f"❌ Si è verificato un errore: {e}")