<script>
    import { onMount } from 'svelte';
    import { carrello } from '../stores.js';
    import ProductDetailModal from '../components/ProductDetailModal.svelte';
    import { fly } from 'svelte/transition';

    const API_URL = 'http://127.0.0.1:5000';

    let prodottiDisponibili = [];
    let errore = '';
    let cercaTermine = '';
    let showSuggestions = false;
    let selectedProduct = null;

    let toastMessage = '';
    let toastTimer;

    const categorieFisse = ['Alimentari', 'Medicinali', 'Altro'];
    let categoriaSelezionata = 'Tutti';

    // --- VARIABILI PER LA PAGINAZIONE ---
    let currentPage = 1;
    const itemsPerPage = 9;

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

    $: categorieDisponibili = ['Tutti', ...categorieFisse];

    $: prodottiFiltrati = prodottiDisponibili.filter((prodotto) => {
        const filtroCategoria =
            categoriaSelezionata === 'Tutti' || prodotto.categoria === categoriaSelezionata;
        const filtroNome = prodotto.nome.toLowerCase().includes(cercaTermine.toLowerCase());
        return filtroCategoria && filtroNome;
    });

    // --- LOGICA DI PAGINAZIONE ---
    $: (cercaTermine, categoriaSelezionata), (currentPage = 1);
    $: totalPages = Math.ceil(prodottiFiltrati.length / itemsPerPage);
    $: paginatedProducts = prodottiFiltrati.slice(
        (currentPage - 1) * itemsPerPage,
        currentPage * itemsPerPage
    );

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

    // --- FUNZIONE PER RESETTARE I FILTRI ---
    function resetFiltri() {
        cercaTermine = '';
        categoriaSelezionata = 'Tutti';
    }

    $: suggerimenti =
        cercaTermine.length > 0
            ? prodottiDisponibili
                  .filter((prodotto) =>
                      prodotto.nome.toLowerCase().startsWith(cercaTermine.toLowerCase())
                  )
                  .slice(0, 5)
            : [];

    function selezionaSuggerimento(nomeProdotto) {
        cercaTermine = nomeProdotto;
        showSuggestions = false;
    }

    function aggiungiAlCarrello(prodotto) {
        if ($carrello[prodotto.id]) {
            $carrello[prodotto.id].quantita++;
        } else {
            $carrello[prodotto.id] = { ...prodotto, quantita: 1 };
        }
        
        if (selectedProduct) {
            selectedProduct = null;
        }

        toastMessage = `"${prodotto.nome}" aggiunto al carrello!`;
        
        clearTimeout(toastTimer);

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

<h1>Prodotti Disponibili</h1>

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
        position: sticky;
        top: 20px;
        max-height: calc(100vh - 40px);
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
    
    /* ========= NUOVA REGOLA CSS AGGIUNTA QUI ========= */
    .filtri-header h2 {
        margin: 0; /* Annulla il margine di default che causa il taglio */
    }
    /* ================================================ */

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