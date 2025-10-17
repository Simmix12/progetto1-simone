<script>
    import { utente } from '../../stores.js';
    import { goto } from '$app/navigation';
    import { onMount, afterUpdate } from 'svelte';
    import { browser } from '$app/environment';// indica che lo stor sta girando nel browser

    const API_URL = 'http://127.0.0.1:5000';

    let profilo = {
        nome: '', cognome: '', via: '', citta: '',
        cap: '', provincia: '', lat: null, lon: null
    };

    let isLoading = true;
    let feedbackMessage = '';
    
    // NUOVA variabile per gli errori di validazione
    let errors = {};

    let map = null; 
    let L = null;

    onMount(async () => {//se l'utente non  è registrato torna alla home
        if (!$utente) {
            goto('/');
            return;
        }
        try {
            const response = await fetch(`${API_URL}/api/profilo/${$utente.id}`);//recupero dati profilo
            if (!response.ok) throw new Error("Profilo non trovato.");
            const data = await response.json();
            
            profilo = { //dati
                ...profilo, ...data, //aggiunge dati
                ...(data.indirizzo || {}), //aggiunge indirizzo
                ...(data.geolocalizzazione || {}) //aggiunge posiziione (coordinate)
            };
            delete profilo.indirizzo;//rimuove
            delete profilo.geolocalizzazione;
        } catch (error) {
            console.warn("Nessun profilo trovato, si parte da un form vuoto.");
        } finally {
            isLoading = false;
        }
    });

    afterUpdate(async () => {//se soddisfiamo questi campi
        if (browser && profilo.lat && profilo.lon && document.getElementById('map')) {
            if (!L) {
                L = (await import('leaflet')).default;
                await import('leaflet/dist/leaflet.css');
            }
            //creazione mappa
            if (!map) {
                map = L.map('map').setView([profilo.lat, profilo.lon], 17)//centramento (posizione)
                L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {//satellite
                    attribution: 'Tiles &copy; Esri'
                }).addTo(map);
                L.marker([profilo.lat, profilo.lon]).addTo(map);//aggiunta marcatore sulla posizione
            } else {
                map.setView([profilo.lat, profilo.lon], 17);
            }
        }
    });
    
    // --- NUOVA FUNZIONE DI VALIDAZIONE ---
    function validateForm() {
        const newErrors = {};//creazioen oggetto errore e ne inserisce i campi obbligatori
        const requiredFields = ['nome', 'cognome', 'via', 'citta', 'cap', 'provincia'];

        requiredFields.forEach(field => {//verifica all' interno dei campi che non siano vuoti
            if (!profilo[field] || !profilo[field].trim()) {
                newErrors[field] = 'Questo campo è obbligatorio.';
            }
        });
        
        errors = newErrors;
        return Object.keys(newErrors).length === 0; // Ritorna true se non ci sono errori
    }

    // --- FUNZIONE DI SALVATAGGIO MODIFICATA ---
    async function handleUpdate() {
        if (!$utente) return;
        
        // Pulisce i messaggi precedenti e valida il form
        feedbackMessage = '';
        const isFormValid = validateForm();

        // Se il form non è valido, si ferma qui
        if (!isFormValid) {
            feedbackMessage = 'Errore: Compila tutti i campi obbligatori evidenziati.';
            return;
        }

        feedbackMessage = 'Salvataggio in corso...';
        try {
            const response = await fetch(`${API_URL}/api/profilo/${$utente.id}`, {//fatch che aggiorna il profilo
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(profilo)
            });
            const data = await response.json();
            if (!response.ok) throw new Error(data.errore || 'Si è verificato un errore.');
            
            feedbackMessage = data.messaggio;//messaggio di successo
            
            if (data.profilo) {//aggiornamento profilo con i dati ritornati dals erver 
                profilo = { 
                    ...profilo, ...data.profilo,
                    ...(data.profilo.indirizzo || {}), 
                    ...(data.profilo.geolocalizzazione || {}) 
                };
                delete profilo.indirizzo;
                delete profilo.geolocalizzazione;
            }
        } catch (e) {
            feedbackMessage = `Errore: ${e.message}`;
        }
    }

    function handleGeolocate() {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(position => {
                profilo = {
                    ...profilo,
                    lat: position.coords.latitude,
                    lon: position.coords.longitude
                };
                feedbackMessage = 'Posizione GPS acquisita! Salva il profilo per memorizzarla.';
            }, () => {
                feedbackMessage = 'Impossibile ottenere la posizione. Assicurati di aver dato i permessi.';
            });
        } else {
            feedbackMessage = 'La geolocalizzazione non è supportata dal tuo browser.';
        }
    }
</script>

<svelte:head>
    <title>Il Mio Profilo</title>
</svelte:head>

<div class="profilo-container">
    <h1>Gestisci il Tuo Profilo</h1>

    {#if isLoading}
        <p>Caricamento del profilo...</p>
    {:else}
        <form class="profilo-form" on:submit|preventDefault={handleUpdate}>
            
            <fieldset>
                <legend>Dati Anagrafici</legend>
                <div class="form-grid">
                    <div class="form-group">
                        <label for="nome">Nome</label>
                        <input id="nome" type="text" bind:value={profilo.nome} placeholder="Mario" class:invalid={errors.nome} />
                        {#if errors.nome}<p class="error-message">{errors.nome}</p>{/if}
                    </div>
                    <div class="form-group">
                        <label for="cognome">Cognome</label>
                        <input id="cognome" type="text" bind:value={profilo.cognome} placeholder="Rossi" class:invalid={errors.cognome} />
                        {#if errors.cognome}<p class="error-message">{errors.cognome}</p>{/if}
                    </div>
                </div>
            </fieldset>

            <fieldset>
                <legend>Indirizzo di Spedizione</legend>
                 <div class="form-group">
                    <label for="via">Via e Numero Civico</label>
                    <input id="via" type="text" bind:value={profilo.via} placeholder="Via Roma, 10" class:invalid={errors.via} />
                    {#if errors.via}<p class="error-message">{errors.via}</p>{/if}
                 </div>
                <div class="form-grid">
                    <div class="form-group">
                        <label for="citta">Città</label>
                        <input id="citta" type="text" bind:value={profilo.citta} placeholder="Milano" class:invalid={errors.citta} />
                        {#if errors.citta}<p class="error-message">{errors.citta}</p>{/if}
                    </div>
                    <div class="form-group">
                        <label for="cap">CAP</label>
                        <input id="cap" type="text" bind:value={profilo.cap} placeholder="20121" class:invalid={errors.cap} />
                        {#if errors.cap}<p class="error-message">{errors.cap}</p>{/if}
                    </div>
                    <div class="form-group">
                        <label for="provincia">Provincia</label>
                        <input id="provincia" type="text" bind:value={profilo.provincia} placeholder="MI" maxlength="2" class:invalid={errors.provincia} />
                        {#if errors.provincia}<p class="error-message">{errors.provincia}</p>{/if}
                    </div>
                </div>
            </fieldset>

            <fieldset>
                <legend>La Tua Posizione</legend>
                {#if profilo.lat && profilo.lon}
                    <p>Questa è la posizione associata al tuo indirizzo. Usa il GPS per una maggiore precisione.</p>
                    <div id="map" class="map-container"></div>
                {:else}
                    <p>Salva il tuo indirizzo per visualizzare la tua posizione su una mappa.</p>
                {/if}
                <button type="button" class="secondary-btn" on:click={handleGeolocate}>Usa Posizione GPS</button>
            </fieldset>

            {#if feedbackMessage}
                <p class="feedback" class:error={feedbackMessage.startsWith('Errore:')}>{feedbackMessage}</p>
            {/if}

            <button type="submit">Salva Profilo</button>
        </form>
    {/if}
</div>

<style>
    .profilo-container { max-width: 800px; margin: 2rem auto; padding: 2rem; background-color: var(--colore-sfondo-secondario); border: 1px solid var(--colore-bordi); border-radius: 8px; }
    h1 { text-align: center; color: var(--colore-accento); margin-bottom: 2rem; }
    .profilo-form { display: flex; flex-direction: column; gap: 2rem; }
    fieldset { border: 1px solid var(--colore-bordi); border-radius: 6px; padding: 1.5rem; }
    legend { padding: 0 0.5rem; font-weight: bold; color: var(--colore-accento); }
    .form-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem; }
    
    /* MODIFICA: Separato il form-group per una migliore struttura */
    .form-group {
        display: flex;
        flex-direction: column;
    }
    label { font-weight: bold; font-size: 0.9rem; }
    input { margin-top: 0.5rem; padding: 0.75rem; font-size: 1rem; border-radius: 5px; border: 1px solid var(--colore-bordi); background-color: var(--colore-sfondo-principale); color: var(--colore-testo); }
    
    /* --- NUOVI STILI PER LA VALIDAZIONE --- */
    input.invalid {
        border-color: #e53e3e; /* Rosso per errore */
        box-shadow: 0 0 0 1px #e53e3e;
    }
    .error-message {
        color: #e53e3e;
        font-size: 0.8rem;
        margin-top: 4px;
        font-weight: normal;
    }
    .feedback.error {
        color: #e53e3e;
    }
    /* --- FINE NUOVI STILI --- */

    button { padding: 0.8rem; font-size: 1.1rem; font-weight: bold; cursor: pointer; border-radius: 5px; background-color: var(--colore-accento); color: var(--colore-sfondo-principale); border: none; margin-top: 1rem; }
    .secondary-btn { background-color: var(--colore-bordi); color: var(--colore-testo); margin-top: 0; }
    .feedback { text-align: center; font-weight: bold; }
    
    .map-container {
        height: 350px;
        width: 100%;
        border-radius: 6px;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }
</style>