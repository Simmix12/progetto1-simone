<script>
    import { onMount } from 'svelte';
    import { utente } from '../../../stores.js'; // Assicurati che il percorso sia corretto
    import { goto } from '$app/navigation';

    // URL del tuo backend Python/Flask
    const API_URL = 'http://127.0.0.1:5000';

    // Variabili di stato per gestire la pagina
    let ordini = [];      // Conterrà la lista degli ordini scaricati
    let isLoading = true; // Mostra un messaggio di caricamento
    let error = null;     // Mostra un messaggio in caso di errore

    // Questa funzione viene eseguita appena il componente viene caricato nella pagina
    onMount(async () => {
        // 1. Protezione della pagina (Route Guard)
        // Se l'utente non è loggato, viene reindirizzato alla pagina di login.
        if (!$utente) { 
            goto('/login');
            return;
        }

        try {
            // 2. Chiamata all'API del backend
            // Viene richiesto lo storico degli ordini per l'utente attualmente loggato.
            const response = await fetch(`${API_URL}/api/ordini/${$utente.id}`);//$utente.id prende l'utente loggato
            
            // 3. Gestione degli errori della risposta
            // Se la risposta non è positiva (es. errore 404 o 500), viene generato un errore.
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.errore || 'Impossibile caricare lo storico degli ordini.');
            }

            // 4. Salvataggio dei dati
            // I dati JSON ricevuti dal backend vengono salvati nella variabile 'ordini'.
            ordini = await response.json();

        } catch (err) {
            // Se si verifica un qualsiasi errore durante il processo, viene salvato il messaggio.
            error = err.message;
            console.error("Errore nel caricamento dello storico ordini:", err);
        } finally {
            // 5. Fine del caricamento
            // In ogni caso (successo o errore), l'indicatore di caricamento viene disattivato.
            isLoading = false;
        }
    });

    // Funzione di utilità per formattare le date in un formato leggibile
    function formatDate(dateString) {
        const options = { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' };
        return new Date(dateString).toLocaleDateString('it-IT', options);
    }
</script>

<svelte:head>
    <title>I Miei Ordini</title>
</svelte:head>

<div class="container">
    <h1>🛍️ I Miei Ordini</h1>

    {#if isLoading}
        <p class="status-message">Caricamento storico ordini in corso...</p>
    {:else if error}
        <p class="status-message error">{error}</p>
    {:else if ordini.length === 0}
        <div class="no-orders-card">
            <p>Non hai ancora effettuato nessun ordine.</p>
            <a href="/" class="btn-primary">Inizia lo shopping</a>
        </div>
    {:else}
        <div class="ordini-list">
            {#each ordini as ordine (ordine._id)}
                <div class="ordine-card">
                    <div class="card-header">
                        <div>
                            <span class="ordine-id">Ordine #{ordine._id.slice(-6).toUpperCase()}</span>
                            <span class="ordine-data">{formatDate(ordine.data_creazione)}</span>
                        </div>
                        <strong class="ordine-totale">{ordine.totale_complessivo.toFixed(2)} €</strong>
                    </div>

                    <div class="card-body">
                        <h4>Prodotti Acquistati:</h4>
                        <ul>
                            {#each ordine.voci as voce}
                                <li>
                                    <span>{voce.nome_prodotto} (x{voce.quantita})</span>
                                    <span>{voce.prezzo_totale.toFixed(2)} €</span>
                                </li>
                            {/each}
                        </ul>
                    </div>

                    <div class="card-footer">
                        <span>IVA Inclusa: {ordine.totale_iva.toFixed(2)} €</span>
                    </div>
                </div>
            {/each}
        </div>
    {/if}
</div>

<style>
    .container {
        max-width: 900px;
        margin: 2rem auto;
        padding: 0 1rem;
    }

    h1 {
        color: var(--colore-accento);
        text-align: center;
        margin-bottom: 2rem;
    }

    .status-message {
        text-align: center;
        font-size: 1.1rem;
        color: var(--colore-testo-secondario);
        padding: 2rem;
        background: var(--colore-sfondo-secondario);
        border-radius: 12px;
    }
    
    .status-message.error {
        color: #e53e3e;
        border: 1px solid #e53e3e;
    }
    
    .no-orders-card {
        background: var(--colore-sfondo-secondario);
        padding: 2rem;
        border-radius: 12px;
        text-align: center;
        border: 1px solid var(--colore-bordi);
    }

    .no-orders-card p {
        margin: 0 0 1.5rem 0;
        font-size: 1.2rem;
    }

    .btn-primary {
        background-color: var(--colore-accento);
        color: white;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        text-decoration: none;
        font-weight: 600;
        transition: background-color 0.2s;
    }

    .btn-primary:hover {
        opacity: 0.9;
    }

    .ordini-list {
        display: grid;
        gap: 1.5rem;
    }

    .ordine-card {
        background: var(--colore-sfondo-secondario);
        border: 1px solid var(--colore-bordi);
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        overflow: hidden;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .ordine-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.1);
    }

    .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: var(--colore-sfondo-principale);
        padding: 1rem 1.5rem;
        border-bottom: 1px solid var(--colore-bordi);
    }

    .card-header div {
        display: flex;
        flex-direction: column;
        gap: 0.25rem;
    }

    .ordine-id {
        font-weight: 600;
        font-size: 1rem;
    }

    .ordine-data {
        font-size: 0.8rem;
        color: var(--colore-testo-secondario);
    }

    .ordine-totale {
        font-size: 1.2rem;
        font-weight: 700;
        color: var(--colore-accento);
    }

    .card-body {
        padding: 1.5rem;
    }

    .card-body h4 {
        margin: 0 0 1rem 0;
        font-size: 1rem;
    }

    .card-body ul {
        list-style: none;
        padding: 0;
        margin: 0;
        display: grid;
        gap: 0.75rem;
    }

    .card-body li {
        display: flex;
        justify-content: space-between;
        font-size: 0.9rem;
    }

    .card-footer {
        background: var(--colore-sfondo-principale);
        padding: 0.75rem 1.5rem;
        text-align: right;
        font-size: 0.85rem;
        color: var(--colore-testo-secondario);
        border-top: 1px solid var(--colore-bordi);
    }
</style>