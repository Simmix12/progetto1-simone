<script>
    import { utente } from '../../stores.js';
    import { goto } from '$app/navigation';
    import { onMount, afterUpdate } from 'svelte';
    import { browser } from '$app/environment'; // Necessario per eseguire il codice solo nel browser

    const API_URL = 'http://127.0.0.1:5000';

    let profilo = {
        nome: '', cognome: '', via: '', citta: '',
        cap: '', provincia: '', lat: null, lon: null
    };

    let isLoading = true;
    let feedbackMessage = '';
    
    // Variabili per la mappa
    let map = null; 
    let L = null;

    onMount(async () => {
        if (!$utente) {
            goto('/');
            return;
        }
        try {
            const response = await fetch(`${API_URL}/api/profilo/${$utente.id}`);
            if (!response.ok) throw new Error("Profilo non trovato.");
            const data = await response.json();
            
            profilo = { 
                ...profilo, ...data, 
                ...(data.indirizzo || {}), 
                ...(data.geolocalizzazione || {}) 
            };
            delete profilo.indirizzo;
            delete profilo.geolocalizzazione;
        } catch (error) {
            console.warn("Nessun profilo trovato, si parte da un form vuoto.");
        } finally {
            isLoading = false;
        }
    });

    // Questa funzione viene eseguita dopo che i dati del profilo sono stati caricati o aggiornati
    afterUpdate(async () => {
        // Eseguiamo questo codice SOLO nel browser e se abbiamo le coordinate
        if (browser && profilo.lat && profilo.lon && document.getElementById('map')) {
            // Carichiamo la libreria Leaflet solo la prima volta
            if (!L) {
                L = (await import('leaflet')).default;
                await import('leaflet/dist/leaflet.css');
            }
            
            // Se la mappa non è ancora stata creata, la inizializziamo
            if (!map) {
                map = L.map('map').setView([profilo.lat, profilo.lon], 17); // Zoom 17 per vista ravvicinata

                // Aggiungiamo il layer con le immagini satellitari ("vista dall'alto")
                L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
                    attribution: 'Tiles &copy; Esri'
                }).addTo(map);

                // Aggiungiamo un segnaposto
                L.marker([profilo.lat, profilo.lon]).addTo(map);
            } else {
                // Se la mappa esiste già, la centriamo sulle nuove coordinate
                map.setView([profilo.lat, profilo.lon], 17);
            }
        }
    });

    // Funzione per salvare i dati nel database (modificata per aggiornare la mappa)
    async function handleUpdate() {
        if (!$utente) return;
        feedbackMessage = 'Salvataggio in corso...';
        try {
            const response = await fetch(`${API_URL}/api/profilo/${$utente.id}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(profilo)
            });
            const data = await response.json();
            if (!response.ok) throw new Error(data.errore || 'Si è verificato un errore.');
            
            feedbackMessage = data.messaggio;
            
            // Aggiorniamo lo stato locale con i dati freschi dal backend (incluse le nuove coordinate)
            if (data.profilo) {
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

    // Funzione per ottenere la geolocalizzazione dal browser (modificata per aggiornare la mappa)
    function handleGeolocate() {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(position => {
                // Aggiorniamo l'oggetto profilo in modo reattivo per far scattare afterUpdate
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
                    <label> Nome <input type="text" bind:value={profilo.nome} placeholder="Mario" /> </label>
                    <label> Cognome <input type="text" bind:value={profilo.cognome} placeholder="Rossi" /> </label>
                </div>
            </fieldset>

            <fieldset>
                <legend>Indirizzo di Spedizione</legend>
                <label> Via e Numero Civico <input type="text" bind:value={profilo.via} placeholder="Via Roma, 10" /> </label>
                <div class="form-grid">
                    <label> Città <input type="text" bind:value={profilo.citta} placeholder="Milano" /> </label>
                    <label> CAP <input type="text" bind:value={profilo.cap} placeholder="20121" /> </label>
                    <label> Provincia <input type="text" bind:value={profilo.provincia} placeholder="MI" maxlength="2" /> </label>
                </div>
            </fieldset>

            <fieldset>
                <legend>La Tua Posizione</legend>
                
                <!-- Se abbiamo le coordinate, mostra la mappa -->
                {#if profilo.lat && profilo.lon}
                    <p>Questa è la posizione associata al tuo indirizzo. Usa il GPS per una maggiore precisione.</p>
                    <div id="map" class="map-container"></div>
                {:else}
                    <p>Salva il tuo indirizzo per visualizzare la tua posizione su una mappa.</p>
                {/if}

                <button type="button" class="secondary-btn" on:click={handleGeolocate}>Usa Posizione GPS</button>
            </fieldset>

            {#if feedbackMessage}
                <p class="feedback">{feedbackMessage}</p>
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
    label { display: flex; flex-direction: column; font-weight: bold; font-size: 0.9rem; }
    input { margin-top: 0.5rem; padding: 0.75rem; font-size: 1rem; border-radius: 5px; border: 1px solid var(--colore-bordi); background-color: var(--colore-sfondo-principale); color: var(--colore-testo); }
    button { padding: 0.8rem; font-size: 1.1rem; font-weight: bold; cursor: pointer; border-radius: 5px; background-color: var(--colore-accento); color: var(--colore-sfondo-principale); border: none; margin-top: 1rem; }
    .secondary-btn { background-color: var(--colore-bordi); color: var(--colore-testo); margin-top: 0; }
    .feedback { text-align: center; font-weight: bold; }
    
    /* Stile per il contenitore della mappa */
    .map-container {
        height: 350px;
        width: 100%;
        border-radius: 6px;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }
</style>

