<script>
    import { onMount } from 'svelte';
    import { carrello } from '../stores.js';
    import ProductDetailModal from '../components/ProductDetailModal.svelte';
    import { fly } from 'svelte/transition';

    // Indirizzo base del nostro server API.
    const API_URL = 'http://127.0.0.1:5000';

    // --- STATO DEL COMPONENTE ---
    let prodottiDisponibili = []; // Lista completa dei prodotti caricati dal server.
    let errore = ''; // Per mostrare un messaggio di errore se il caricamento fallisce.
    let cercaTermine = ''; // Il testo inserito dall'utente nella barra di ricerca.
    let categoriaSelezionata = 'Tutti'; // La categoria attualmente selezionata per filtrare.
    let showSuggestions = false; // Controlla la visibilità del menu a tendina con i suggerimenti di ricerca.
    let selectedProduct = null; // Il prodotto attualmente visualizzato nel modale di dettaglio.

    // Stato per la notifica "toast" che appare quando si aggiunge un prodotto al carrello.
    let toastMessage = '';
    let toastTimer; // Usato per far scomparire la notifica dopo qualche secondo.

    // Dati statici per il componente.
    const categorieFisse = ['Alimentari', 'Medicinali', 'Altro'];
    const pubblicita = [
        {
            id: 1,
            titolo: "Offerta Speciale -50%",
            videoUrl: "https://www.youtube.com/embed/-htPoFiTXTA?si=sbiRbuV9wEuggese",
            descrizione: "Scopri le nostre incredibili offerte"
        },
        {
            id: 2,
            titolo: "Nuovi Arrivi",
            videoUrl: "https://www.youtube.com/embed/0KsEo_nPgmI?si=LeKNKfW7k13e-S5U",
            descrizione: "I prodotti più recenti del mese"
        },
        {
            id: 3,
            titolo: "Migliori Acquisti",
            videoUrl: "https://www.youtube.com/embed/D-FFmP6pqRQ?si=opS7qIbPXgfnRnWm",
            descrizione: "I più venduti della settimana"
        }
    ];

    // --- PAGINAZIONE ---
    let currentPage = 1; // La pagina corrente visualizzata.
    const itemsPerPage = 9; // Quanti prodotti mostrare per pagina.

    // onMount viene eseguito appena il componente è pronto nel DOM.
    // Lo usiamo per caricare i dati iniziali dei prodotti.
    onMount(async () => {
        try {
            const response = await fetch(`${API_URL}/api/prodotti`);
            if (!response.ok) {
                throw new Error('Errore nel caricamento dei prodotti dal server.');
            }
            prodottiDisponibili = await response.json();
        } catch (e) {
            errore = e.message;
        }
    });

    // --- LOGICA REATTIVA (si aggiorna automaticamente quando le variabili cambiano) ---

    // Crea la lista completa delle categorie, aggiungendo "Tutti" a quelle fisse.
    $: categorieDisponibili = ['Tutti', ...categorieFisse];

    // Filtra i prodotti in base alla categoria e al termine di ricerca.
    // Questo blocco viene eseguito ogni volta che `prodottiDisponibili`, `categoriaSelezionata` o `cercaTermine` cambiano.
    $: prodottiFiltrati = prodottiDisponibili.filter((prodotto) => {
        const filtroCategoria =
            categoriaSelezionata === 'Tutti' || prodotto.categoria === categoriaSelezionata;
        const filtroNome = prodotto.nome.toLowerCase().includes(cercaTermine.toLowerCase());
        return filtroCategoria && filtroNome;
    });

    // Genera suggerimenti di ricerca basati su ciò che l'utente sta scrivendo.
    $: suggerimenti =
        cercaTermine.length > 0
            ? prodottiDisponibili
                  .filter((prodotto) =>
                      prodotto.nome.toLowerCase().startsWith(cercaTermine.toLowerCase())
                  )
                  .slice(0, 5) // Mostriamo al massimo 5 suggerimenti.
            : [];

    // Ogni volta che l'utente cambia i filtri (ricerca o categoria),
    // la paginazione viene resettata tornando alla prima pagina.
    $: (cercaTermine, categoriaSelezionata), (currentPage = 1);

    // Calcola il numero totale di pagine necessarie.
    $: totalPages = Math.ceil(prodottiFiltrati.length / itemsPerPage);

    // Estrae solo i prodotti per la pagina corrente dalla lista filtrata.
    $: paginatedProducts = prodottiFiltrati.slice(
        (currentPage - 1) * itemsPerPage,
        currentPage * itemsPerPage
    );


    // --- FUNZIONI ---

    function goToNextPage() {
        if (currentPage < totalPages) {
            currentPage++;
        }
    }

    function goToPrevPage() {
        if (currentPage > 1) {
            currentPage--;
        }
    }

    // Riporta i filtri al loro stato iniziale.
    function resetFiltri() {
        cercaTermine = '';
        categoriaSelezionata = 'Tutti';
    }

    // Imposta il termine di ricerca quando l'utente clicca su un suggerimento.
    function selezionaSuggerimento(nomeProdotto) {
        cercaTermine = nomeProdotto;
        showSuggestions = false; // Nasconde la lista dei suggerimenti.
    }

    // Gestisce l'aggiunta di un prodotto al carrello.
    function aggiungiAlCarrello(prodotto) {
        // Se il prodotto è già nel carrello, aumenta la quantità.
        if ($carrello[prodotto.id]) {
            $carrello[prodotto.id].quantita++;
        } else {
            // Altrimenti, aggiungilo con quantità 1.
            $carrello[prodotto.id] = { ...prodotto, quantita: 1 };
        }
        
        // Se il modale dei dettagli è aperto, chiudilo.
        if (selectedProduct) {
            selectedProduct = null;
        }

        // Mostra una notifica di conferma.
        toastMessage = `"${prodotto.nome}" aggiunto al carrello!`;
        
        // Resetta il timer precedente per evitare che la notifica si chiuda troppo presto.
        clearTimeout(toastTimer);

        // Imposta un nuovo timer per nascondere la notifica dopo 3 secondi.
        toastTimer = setTimeout(() => {
            toastMessage = '';
        }, 3000);
    }
</script>

<svelte:head>
    <title>Negozio</title>
</svelte:head>

{#if toastMessage}
    <div class="toast-notification" transition:fly={{ y: 20, duration: 300 }}>
        ✅ {toastMessage}
    </div>
{/if}

{#if selectedProduct}
    <ProductDetailModal
        prodotto={selectedProduct}
        on:close={() => (selectedProduct = null)}
        on:addToCart={(event) => aggiungiAlCarrello(event.detail)}
    />
{/if}

<h1>Inizia la tua spesa</h1>

{#if errore}
    <p class="errore">{errore}</p>
{/if}

<div class="negozio-layout">
    <aside class="filtri-sidebar">
        <div class="sidebar-content-wrapper">
            <div class="filtri-header">
                <h2>Filtri</h2>
                <button class="reset-btn" on:click={resetFiltri}>Resetta</button>
            </div>
            
            <div class="filtro-gruppo">
                <label for="search-input">Cerca Prodotto</label>
                <div class="search-container">
                    <div class="search-input-wrapper">
                        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="search-icon"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
                        <input
                            id="search-input"
                            type="text"
                            placeholder="Cosa stai cercando?"
                            bind:value={cercaTermine}
                            on:focus={() => (showSuggestions = true)}
                            on:blur={() => setTimeout(() => (showSuggestions = false), 150)}
                        />
                    </div>
                    {#if showSuggestions && suggerimenti.length > 0}
                        <div class="suggestions-dropdown">
                            {#each suggerimenti as prodotto (prodotto.id)}
                                <div
                                    class="suggestion-item"
                                    role="button"
                                    tabindex="0"
                                    on:mousedown|preventDefault={() => selezionaSuggerimento(prodotto.nome)}
                                    on:keydown={(e) => { if (e.key === 'Enter') selezionaSuggerimento(prodotto.nome); }}
                                >
                                    {prodotto.nome} <span class="prezzo">{prodotto.prezzo_lordo.toFixed(2)} €</span>
                                </div>
                            {/each}
                        </div>
                    {/if}
                </div>
            </div>

            <div class="filtro-gruppo">
                <label>Categoria</label>
                <div class="category-buttons">
                    {#each categorieDisponibili as categoria}
                        <button 
                            class="category-btn" 
                            class:active={categoria === categoriaSelezionata}
                            on:click={() => categoriaSelezionata = categoria}
                        >
                            {categoria}
                        </button>
                    {/each}
                </div>
            </div>

            <div class="pubblicita-section">
                <div class="pubblicita-header">
                    <h3> Offerte Speciali</h3>
                </div>
                <div class="pubblicita-list">
                    {#each pubblicita as spot (spot.id)}
                        <div class="pubblicita-item">
                            <h4>{spot.titolo}</h4>
                            <p class="pubblicita-descrizione">{spot.descrizione}</p>
                            <div class="video-container">
                                <iframe
                                    src="{spot.videoUrl}"
                                    title="{spot.titolo}"
                                    frameborder="0"
                                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                                    allowfullscreen
                                ></iframe>
                            </div>
                        </div>
                    {/each}
                </div>
            </div>
        </div>
    </aside>

    <main class="prodotti-principale">
        {#if prodottiDisponibili.length === 0 && !errore}
            <p>Caricamento prodotti...</p>
        {:else if prodottiFiltrati.length > 0}
            <div class="prodotti-grid">
                {#each paginatedProducts as prodotto (prodotto.id)}
                    <div
                        class="prodotto-card"
                        role="button"
                        tabindex="0"
                        on:click={() => (selectedProduct = prodotto)}
                        on:keydown={(e) => { if (e.key === 'Enter') selectedProduct = prodotto; }}
                    >
                        <img
                            class="prodotto-immagine"
                            src="{API_URL}/static/images/{prodotto.immagine_url}"
                            alt="Immagine di {prodotto.nome}"
                        />
                        <h3>{prodotto.nome}</h3>
                        <p>{prodotto.prezzo_lordo.toFixed(2)} €</p>
                        <button on:click|stopPropagation={() => aggiungiAlCarrello(prodotto)}>
                            Aggiungi al Carrello
                        </button>
                    </div>
                {/each}
            </div>

            {#if totalPages > 1}
                <div class="pagination-controls">
                    <button on:click={goToPrevPage} disabled={currentPage === 1}>
                        &larr; Precedente
                    </button>
                    <span>Pagina {currentPage} di {totalPages}</span>
                    <button on:click={goToNextPage} disabled={currentPage === totalPages}>
                        Successiva &rarr;
                    </button>
                </div>
            {/if}
        {:else}
            <p>Nessun prodotto trovato per i criteri selezionati.</p>
        {/if}
    </main>
</div>

<style>
    h1 {
        text-align: center;
        font-size: 3rem;
        color: var(--colore-accento);
        margin-bottom: 2.5rem;
        font-weight: 700;
        text-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    
    .errore {
        text-align: center;
        color: var(--colore-pericolo);
    }
    
    .negozio-layout {
        display: grid;
        grid-template-columns: 280px 1fr;
        gap: 2rem;
        max-width: 1400px;
        margin: 0 auto;
        align-items: flex-start;
    }

    .filtri-sidebar {
        display: flex;
        flex-direction: column;
        background-color: var(--colore-sfondo-secondario);
        border-radius: 12px;
        border: 1px solid var(--colore-bordi);
    }

    .sidebar-content-wrapper {
        overflow-y: auto;
        padding: 1.5rem;
        flex-grow: 1;
    }
    
    .filtri-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid var(--colore-bordi);
        padding-bottom: 1rem;
        margin-bottom: 1.5rem;
    }
    
    .filtri-header h2 {
        margin: 0;
    }

    .reset-btn {
        background: none;
        border: none;
        color: var(--colore-accento);
        cursor: pointer;
        font-weight: bold;
        font-size: 0.9rem;
        padding: 0;
    }
    .reset-btn:hover {
        text-decoration: underline;
    }

    .filtro-gruppo {
        margin-bottom: 2rem;
    }

    .filtro-gruppo label {
        font-size: 1rem;
        font-weight: bold;
        margin-bottom: 0.75rem;
        display: block;
        color: var(--colore-testo-principale);
    }
    
    .search-container { 
        position: relative; 
    }
    
    .search-input-wrapper {
        position: relative;
    }

    .search-icon {
        position: absolute;
        top: 50%;
        left: 12px;
        transform: translateY(-50%);
        color: #888;
        pointer-events: none;
    }

    #search-input {
        width: 100%;
        padding: 0.8rem 0.8rem 0.8rem 40px;
        font-size: 1rem;
        border: 1px solid var(--colore-bordi);
        border-radius: 8px;
        background-color: var(--colore-sfondo-principale);
        color: var(--colore-testo-principale);
        transition: border-color 0.2s, box-shadow 0.2s;
    }
    
    #search-input:focus {
        outline: none;
        border-color: var(--colore-accento);
        box-shadow: 0 0 0 3px rgba(var(--colore-accento-rgb), 0.2);
    }
    
    .category-buttons {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }
    
    .category-btn {
        width: 100%;
        padding: 0.8rem;
        font-size: 0.95rem;
        font-weight: 500;
        text-align: left;
        border: 1px solid var(--colore-bordi);
        background-color: var(--colore-sfondo-principale);
        color: var(--colore-testo-principale);
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .category-btn:hover {
        border-color: var(--colore-accento);
        color: var(--colore-accento);
    }

    .category-btn.active {
        background-color: var(--colore-accento);
        color: white;
        border-color: var(--colore-accento);
        font-weight: bold;
    }
    
    .pubblicita-section {
        margin-top: 2rem;
        padding-top: 1.5rem;
        border-top: 1px solid var(--colore-bordi);
    }
    
    .pubblicita-header {
        margin-bottom: 1rem;
    }
    
    .pubblicita-header h3 {
        margin: 0;
        font-size: 1.1rem;
        color: var(--colore-accento);
    }
    
    .pubblicita-list {
        display: flex;
        flex-direction: column;
        gap: 1.5rem;
    }
    
    .pubblicita-item {
        background: var(--colore-sfondo-principale);
        border-radius: 8px;
        padding: 1rem;
        border: 1px solid var(--colore-bordi);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .pubblicita-item:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    
    .pubblicita-item h4 {
        margin: 0 0 0.5rem 0;
        font-size: 1rem;
        color: var(--colore-testo-principale);
    }
    
    .pubblicita-descrizione {
        font-size: 0.85rem;
        color: var(--colore-testo-secondario);
        margin-bottom: 0.75rem;
    }
    
    .video-container {
        position: relative;
        width: 100%;
        height: 0;
        padding-bottom: 56.25%; /* Aspect ratio 16:9 */
        border-radius: 4px;
        overflow: hidden;
    }
    
    .video-container iframe {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        border-radius: 4px;
    }
    
    .prodotti-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1.5rem;
    }

    .prodotto-card {
        background-color: var(--colore-sfondo-secondario);
        padding: 1.5rem; border-radius: 8px; border: 1px solid var(--colore-bordi);
        text-align: center; display: flex; flex-direction: column;
        transition: transform 0.2s ease, box-shadow 0.2s ease; cursor: pointer;
    }
    .prodotto-card:hover { transform: translateY(-5px); box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1); }
    .prodotto-immagine { width: 100%; height: 180px; object-fit: cover; border-radius: 4px; margin-bottom: 1rem; }
    .prodotto-card h3 { flex-grow: 1; margin-top: 0.5rem; }
    .prodotto-card p { margin-bottom: 1rem; }
    button { padding: 0.5rem 1rem; cursor: pointer; border-radius: 5px; font-weight: bold; background-color: var(--colore-accento); color: var(--colore-sfondo-principale); border: 1px solid var(--colore-accento); transition: opacity 0.2s ease; z-index: 2; }
    button:hover { opacity: 0.85; }
    
    .suggestions-dropdown { position: absolute; top: 100%; left: 0; right: 0; z-index: 10; background-color: var(--colore-sfondo-secondario); border: 1px solid var(--colore-bordi); border-top: none; border-radius: 0 0 8px 8px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); overflow: hidden; }
    .suggestion-item { padding: 0.75rem 1rem; cursor: pointer; display: flex; justify-content: space-between; align-items: center; transition: background-color 0.15s; }
    .suggestion-item:hover { background-color: var(--colore-bordi); }
    .suggestion-item .prezzo { font-weight: bold; color: var(--colore-accento); font-size: 0.9rem; }
    
    .toast-notification { position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); background-color: #28a745; color: white; padding: 1rem 1.5rem; border-radius: 8px; box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2); font-weight: bold; z-index: 2000; white-space: nowrap; }

    .pagination-controls { display: flex; justify-content: center; align-items: center; gap: 1rem; margin-top: 2.5rem; }
    .pagination-controls button { padding: 0.6rem 1.2rem; font-weight: bold; border: 2px solid var(--colore-accento); background-color: transparent; color: var(--colore-accento); border-radius: 8px; cursor: pointer; transition: all 0.2s ease; }
    .pagination-controls button:hover:not(:disabled) { background-color: var(--colore-accento); color: var(--colore-sfondo-principale); }
    .pagination-controls button:disabled { border-color: var(--colore-bordi); color: var(--colore-bordi); cursor: not-allowed; }
    .pagination-controls span { font-weight: bold; font-size: 1.1rem; }
    
    @media (max-width: 1024px) { 
        .negozio-layout {
            grid-template-columns: 220px 1fr;
        }
        .prodotti-grid {
            grid-template-columns: repeat(2, 1fr);
        }
    }
    
    @media (max-width: 768px) {
        .negozio-layout {
            grid-template-columns: 1fr;
        }
        .filtri-sidebar {
            position: static;
            max-height: none;
        }
        .prodotti-grid {
            grid-template-columns: repeat(2, 1fr);
        }
    }

    @media (max-width: 500px) {
        .prodotti-grid {
            grid-template-columns: 1fr;
        }
    }
</style>