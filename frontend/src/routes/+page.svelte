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

    // --- NUOVE VARIABILI PER LA PAGINAZIONE ---
    let currentPage = 1;
    const itemsPerPage = 9; // 3 colonne * 3 righe

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

    // --- NUOVA LOGICA DI PAGINAZIONE ---
    // Resetta la pagina corrente quando i filtri cambiano
    $: (cercaTermine, categoriaSelezionata), (currentPage = 1);

    // Calcola il numero totale di pagine
    $: totalPages = Math.ceil(prodottiFiltrati.length / itemsPerPage);

    // Estrae solo i prodotti per la pagina corrente
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
    // --- FINE LOGICA DI PAGINAZIONE ---


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

<div class="filtri-container command-bar">
    <div class="category-filter">
        <label for="category-select">Categoria</label>
        <select id="category-select" bind:value={categoriaSelezionata}>
            {#each categorieDisponibili as categoria}
                <option value={categoria}>{categoria}</option>
            {/each}
        </select>
    </div>
    <div class="search-container">
        <label for="search-input">Cerca Prodotto</label>
        <input
            id="search-input"
            type="text"
            placeholder="Cosa stai cercando?"
            bind:value={cercaTermine}
            on:focus={() => (showSuggestions = true)}
            on:blur={() => setTimeout(() => (showSuggestions = false), 150)}
        />
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

{#if prodottiDisponibili.length === 0 && !errore}
    <p>Caricamento prodotti...</p>
{:else if prodottiFiltrati.length > 0}
    <div class="prodotti-grid">
        <!-- MODIFICA: Utilizza i prodotti paginati -->
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

    <!-- NUOVO HTML: Controlli di paginazione -->
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

<style>
    h1 {
        text-align: center;
        font-size: 3rem;
        color: var(--colore-accento);
        margin-bottom: 2.5rem;
        font-weight: 700;
        text-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    .prodotti-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1.5rem;
        max-width: 1000px;
        margin: 0 auto;
    }
    .prodotto-card {
        background-color: var(--colore-sfondo-secondario);
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid var(--colore-bordi);
        text-align: center;
        display: flex;
        flex-direction: column;
        transition:
            transform 0.2s ease,
            box-shadow 0.2s ease;
        cursor: pointer;
    }
    .prodotto-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1);
    }
    .prodotto-immagine {
        width: 100%;
        height: 180px;
        object-fit: cover;
        border-radius: 4px;
        margin-bottom: 1rem;
    }
    .prodotto-card h3 {
        flex-grow: 1; 
        margin-top: 0.5rem;
    }
    .prodotto-card p {
        margin-bottom: 1rem;
    }
    button {
        padding: 0.5rem 1rem;
        cursor: pointer;
        border-radius: 5px;
        font-weight: bold;
        background-color: var(--colore-accento);
        color: var(--colore-sfondo-principale);
        border: 1px solid var(--colore-accento);
        transition: opacity 0.2s ease;
        z-index: 2;
    }
    button:hover {
        opacity: 0.85;
    }
    
    .filtri-container.command-bar {
        display: flex;
        max-width: 800px;
        margin: 0 auto 3rem auto;
        background-color: var(--colore-sfondo-secondario);
        padding: 1rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        border: 1px solid var(--colore-bordi);
        gap: 1rem;
    }

    .command-bar .category-filter,
    .command-bar .search-container {
        flex-grow: 1;
    }

    .command-bar label {
        font-size: 0.8rem;
        font-weight: bold;
        color: white;
        margin-bottom: 0.4rem;
        display: block;
    }

    .command-bar select,
    .command-bar input {
        width: 100%;
        padding: 0.8rem;
        font-size: 1rem;
        border: 1px solid var(--colore-bordi);
        border-radius: 8px;
        background-color: var(--colore-sfondo-principale);
        color: white;
    }

    .search-container { 
        position: relative; 
    }

    .suggestions-dropdown { 
        position: absolute; 
        top: 100%; 
        left: 0; 
        right: 0; 
        z-index: 10; 
        background-color: var(--colore-sfondo-secondario); 
        border: 1px solid var(--colore-bordi); 
        border-top: none; 
        border-radius: 0 0 8px 8px; 
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); 
        overflow: hidden; 
    }
    .suggestion-item { 
        padding: 0.75rem 1rem; 
        cursor: pointer; 
        display: flex; 
        justify-content: space-between; 
        align-items: center; 
        transition: background-color 0.15s; 
    }
    .suggestion-item:hover { background-color: var(--colore-bordi); }
    .suggestion-item .prezzo { font-weight: bold; color: var(--colore-accento); font-size: 0.9rem; }
    
    .toast-notification {
        position: fixed; 
        bottom: 20px;
        left: 50%;
        transform: translateX(-50%); 
        background-color: #28a745;
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
        font-weight: bold;
        z-index: 2000;
        white-space: nowrap;
    }

    /* --- NUOVI STILI PER LA PAGINAZIONE --- */
    .pagination-controls {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 1rem;
        margin-top: 2.5rem;
    }

    .pagination-controls button {
        padding: 0.6rem 1.2rem;
        font-weight: bold;
        border: 2px solid var(--colore-accento);
        background-color: transparent;
        color: var(--colore-accento);
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.2s ease;
    }

    .pagination-controls button:hover:not(:disabled) {
        background-color: var(--colore-accento);
        color: var(--colore-sfondo-principale);
    }

    .pagination-controls button:disabled {
        border-color: var(--colore-bordi);
        color: var(--colore-bordi);
        cursor: not-allowed;
    }

    .pagination-controls span {
        font-weight: bold;
        font-size: 1.1rem;
    }
    
    @media (max-width: 768px) { 
        .filtri-container.command-bar { 
            flex-direction: column; 
            align-items: stretch; 
            gap: 1rem; 
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

