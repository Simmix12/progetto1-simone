Progetto e-commerce "Buy Hub"
-
Questo progetto è un e-commerce online composto da due file principali, un forntend e un backend

**Architettura del Progetto** 
- Database: Utilizza MongoDb Atlas come database per la persistenza dei dati.
- Backend: Possiamo vederlo come il cervello dell' e-commerce, si occupa della gestione dei dati e dell'integrazione con servizi esterni (ia e geolocalizzazione)
- Frontend: Gestisce l'interfaccia utente, l'interazione con esso , la navigazione e  la comunicazione con  il backend.

Funzionalità Principali
-

**funzionalità Frontend**

File **Layout** è il file che definisce la struttura comune a tutte le pagine del sito

File **NavBar** è una barra di navigazione fissa che  include:
- Logo e nome del sito
- Login/Registrazione
- Icona del carrello
- Gestione autenticazione

Nella parte inferiore della pagina è presente un **Footer**(una inferiore) contenente:
- Informazioni di contatto
- Icone social
- Dettagli sui pagamenti

**Chat Widget** è un'icona  che permette all'utente di aprire una finestra, l'utente qui potrà chattare con um assistente ia.

Pagina del negozio
-
- **Visualizzazione dei prodotti**: Prodotti vengono caricati dal backend e mostrati in una griglia
- **sistema di filtri**
  - *per categoria*
  - *per mnome*
- **Dettagli prodotto**: Se un prodotto viene cliccato si azpre una pagina con i dettagli del prodotto    
- **Aggiunta al Carrello**: i prodotti possono essere aggiunti al carrello direttamente dalla griglia

Pagina Carrello
-
- **Lista prodotti**:mostra tutti gli articoli nel carrello con i dettagli
- **Gestione quantità**:Aumentare e diminuire le quantità da comprare di ogni prodotto
- **Riepilogo ordine**: Una colonna laterale fissa che mostra il totale provvisorio
- **Metodo pagamento**: Sezione per selezionare il metodo di pagamento

Pagina Pagamento
-
- **Dati fatturazione**: un form permette all'utente di inserire i propri dati anagrafici e l'indirizzo.
- **Form pagamento dinamico**: in base al metodo di pagamento scelto il form cambia in maniera automatica
- **Validazione dati**: I campi della carta di credito (numero, scadenza, CVC) vengono formattati e validati durante l'inserimento.


Profilo utente
-
- **Gestione Dati**: Form per inserire e aggiornare dati anagrafici e indirizzo di spedizione.
- **Geolocalizzazione**: Quando l'utente salva un indirizzo, il backend lo geolocalizza automaticamente e salva le coordinate, In caso si voglia sapere la posizione attuale del dispositivo basta cliccare il pulsante Gps per aggiornare le cordinate con quelle attuali

Reimposta Password
-
- **Verifica password attuale**
- **Controllo che le password nuove coincidano**

Il Backend 
-

Il  **backend**  Si occupa di parlare con il database, gestire la logica complessa e rispondere a tutte le richieste che arrivano dal frontend.

Gestione del Negozio️
-
**Catalogo Prodotti**: Il backend è il custode di tutti i nostri prodotti. Quando apri il negozio, è lui che invia al frontend la lista completa con nomi, prezzi e descrizioni. All'avvio, se il database è vuoto, lo riempie con una lista di prodotti predefiniti per avere subito qualcosa da mostrare.

**Creazione dello Scontrino**: Quando un utente completa un acquisto, il backend riceve il contenuto del carrello. Si mette al lavoro per calcolare i prezzi finali con l'IVA corretta, arrotonda le cifre, calcola i totali e infine salva una copia dello scontrino nel database prima di restituire la versione finale al frontend per essere visualizzata.

Utenti e Sicurezza
-

**Registrazione e Login**: Permette ai nuovi utenti di registrarsi, controllando che l'username o l'email non siano già stati presi. Le password non vengono mai salvate in chiaro, ma trasformate in un codice sicuro (hash) per proteggere la privacy.

**Profilo Personale**: Ogni utente ha un suo profilo. Il backend permette di recuperare e aggiornare queste informazioni (nome, cognome, indirizzo).

**Cambio Password**: Permette all'utente di cambiare la propria password

L'Assistente Virtuale
-
integrato troviamo un assistente intelligente nella chat del sito, potenziato dall'IA di Google Gemini.

