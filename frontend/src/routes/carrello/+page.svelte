<script>
    import { carrello } from '../../stores.js';//import dei prodotti del carrello
    import { goto } from '$app/navigation';//funzione di sveltekit  per navigare tra le pagine
    import MetodoPagamento from '../../components/MetodoPagamento.svelte';//componente importato per il metodo pagamento
    import Modal from '../../components/Modal.svelte';

    let carrelloItems = Object.values($carrello);
    let metodoPagamentoScelto = '';//variabile per memorizzare il metodo pagamento
    
    // Le variabili reattive $: si aggiorneranno automaticamente quando $carrello cambia
    $: isCartEmpty = carrelloItems.length === 0;//variabile che vede se il carrello è vuoto
    $: totaleCarrello = carrelloItems.reduce((acc, item) => acc + item.prezzo_lordo * item.quantita, 0);//variabile che conta quanti oggetti ci sono nel carrello
//acc accumulatore  //item oggettonel carrello 
    const API_URL = 'http://127.0.0.1:5000';

    function procediAlPagamento() {
        if (!metodoPagamentoScelto) return;// se non sono stati scelti metodi di pagamento, viene bloccato
        goto(`/pagamento?metodo=${metodoPagamentoScelto}`);//goto naviga sulla pagina di pagamento
    }

    // --- NUOVE FUNZIONI PER GESTIRE LA QUANTITÀ ---
    function incrementaQuantita(prodottoId) {
        if ($carrello[prodottoId]) {//verifica che il prodotto esista nel carrello
            $carrello[prodottoId].quantita++; //+1 quantità
            $carrello = $carrello; // Forza l'aggiornamento
            carrelloItems = Object.values($carrello);//aggiornamento array 
        }
    }
//funziona come quella sopra
    function decrementaQuantita(prodottoId) {
        if ($carrello[prodottoId]) {
            $carrello[prodottoId].quantita--;
            // Se la quantità arriva a 0, rimuovi il prodotto
            if ($carrello[prodottoId].quantita <= 0) {
                delete $carrello[prodottoId];
            }
            $carrello = $carrello; // Forza l'aggiornamento
            carrelloItems = Object.values($carrello);
        }
    }
    // ---------------------------------------------

    function svuotaCarrello() {
        $carrello = {};
        carrelloItems = [];
    }
</script>

<svelte:head>
    <title>Carrello</title>
</svelte:head>

{#if isCartEmpty}
    <Modal>
        <div class="empty-cart-container">
            <div class="empty-cart-icon">
                <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="8" cy="21" r="1"></circle>
                    <circle cx="19" cy="21" r="1"></circle>
                    <path d="M2.05 2.05h2l2.66 12.42a2 2 0 0 0 2 1.58h9.78a2 2 0 0 0 1.95-1.57l1.65-7.43H5.12"></path>
                </svg>
            </div>
            <h2 class="empty-cart-title">Il tuo carrello è vuoto!</h2>
            <p class="empty-cart-message">Sembra che tu non abbia ancora aggiunto nessun prodotto al carrello. Inizia a fare shopping per scoprire le nostre fantastiche offerte!</p>
            <a href="/" class="torna-negozio-btn">Esplora il Negozio</a>
        </div>
    </Modal>
{/if}

<div class:hidden={isCartEmpty}>
    <h1>Il Tuo Carrello</h1>

    <div class="carrello-layout">
        
        <div class="lista-prodotti">
            <div class="header-carrello">
                <h3>Prodotti</h3>
                <button class="svuota-carrello-btn" on:click={svuotaCarrello}>
                    Svuota Carrello
                </button>
            </div>
            <ul>
                {#each carrelloItems as item (item.id)}
                    <li class="prodotto-item">
                        <img src="{API_URL}/static/images/{item.immagine_url}" alt={item.nome} class="prodotto-img" />
                        
                        <div class="prodotto-info">
                            <span class="nome">{item.nome}</span>
                            <span class="prezzo-unitario">{item.prezzo_lordo.toFixed(2)} € / cad.</span>
                        </div>

                        <div class="quantita-controls">
                            <button on:click={() => decrementaQuantita(item.id)}>−</button>
                            <span>{item.quantita}</span>
                            <button on:click={() => incrementaQuantita(item.id)}>+</button>
                        </div>

                        <strong class="prezzo-totale-riga">{(item.prezzo_lordo * item.quantita).toFixed(2)} €</strong>
                    </li>
                {/each}
            </ul>
        </div>

        <div class="riepilogo-ordine">
            <h3>Riepilogo Ordine</h3>
            <div class="totale">
                <span>Totale Provvisorio</span>
                <strong>{totaleCarrello.toFixed(2)} €</strong>
            </div>
            <hr />
            <MetodoPagamento on:selectionChange={(event) => (metodoPagamentoScelto = event.detail)} />
            <button class="pagamento" on:click={procediAlPagamento} disabled={!metodoPagamentoScelto}>
                Vai al Pagamento
            </button>
        </div>

    </div>
</div>

<style>
    h1 {
        text-align: center;
        font-size: 2.5rem;
        color: var(--colore-testo-principale);
        margin-bottom: 2rem;
    }

    .hidden { display: none; }

    /* --- NUOVO STILE PER IL POP-UP CARRELLO VUOTO --- */
    .empty-cart-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        padding: 2rem;
        max-width: 500px;
        margin: 0 auto;
    }

    .empty-cart-icon {
        color: var(--colore-testo-secondario);
        margin-bottom: 1.5rem;
        opacity: 0.7;
    }

    .empty-cart-title {
        font-size: 1.8rem;
        color: var(--colore-testo-principale);
        margin-bottom: 1rem;
        font-weight: 600;
    }

    .empty-cart-message {
        color: var(--colore-testo-secondario);
        line-height: 1.6;
        margin-bottom: 2rem;
        font-size: 1.1rem;
    }

    .torna-negozio-btn {
        display: inline-block;
        padding: 0.75rem 2rem;
        background-color: var(--colore-primario, #007bff);
        color: white;
        text-decoration: none;
        border-radius: 8px;
        font-weight: 600;
        font-size: 1.1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    .torna-negozio-btn:hover {
        background-color: var(--colore-primario-scuro, #0056b3);
        transform: translateY(-2px);
        box-shadow: 0 6px 8px rgba(0, 0, 0, 0.15);
    }

    /* --- NUOVO STILE DEL LAYOUT --- */
    .carrello-layout {
        display: grid;
        grid-template-columns: 2fr 1fr; /* Layout 2/3 per la lista e 1/3 per il riepilogo */
        gap: 2rem;
        max-width: 1200px;
        margin: 0 auto;
        align-items: flex-start; /* Allinea gli elementi in cima */
    }

    .lista-prodotti, .riepilogo-ordine {
        background-color: var(--colore-sfondo-secondario);
        border: 1px solid var(--colore-bordi);
        border-radius: 8px;
        padding: 1.5rem;
    }
    
    .riepilogo-ordine {
        position: sticky; /* L'elemento rimane fisso quando si scorre */
        top: 20px;
    }

    .header-carrello {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid var(--colore-bordi);
    }
    .header-carrello h3 { margin: 0; font-size: 1.5rem; }

    ul { list-style: none; padding: 0; margin: 0; }

    .prodotto-item {
        display: flex;
        align-items: center;
        gap: 1rem;
        padding: 1rem 0;
        border-bottom: 1px solid var(--colore-bordi);
    }
    li:last-child { border-bottom: none; }

    .prodotto-img {
        width: 80px;
        height: 80px;
        object-fit: cover;
        border-radius: 6px;
    }

    .prodotto-info {
        flex-grow: 1;
        display: flex;
        flex-direction: column;
    }
    .prodotto-info .nome { font-weight: 600; }
    .prodotto-info .prezzo-unitario { font-size: 0.9rem; color: var(--colore-testo-secondario); }

    .quantita-controls {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .quantita-controls button {
        width: 30px;
        height: 30px;
        padding: 0;
        border-radius: 50%;
        font-size: 1.2rem;
        line-height: 1;
        background-color: var(--colore-bordi);
        color: var(--colore-testo-principale);
        border: none;
    }
    .quantita-controls span { font-weight: bold; min-width: 20px; text-align: center; }

    .prezzo-totale-riga {
        min-width: 80px;
        text-align: right;
        font-size: 1.1rem;
    }
    
    .svuota-carrello-btn {
        font-size: 0.9rem;
        padding: 0.5rem 1rem;
        border: 1px solid var(--colore-pericolo);
        border-radius: 5px;
        background: transparent;
        color: var(--colore-pericolo);
        font-weight: bold;
    }
    .svuota-carrello-btn:hover { background-color: var(--colore-pericolo); color: white; }

    .totale { display: flex; justify-content: space-between; font-size: 1.2rem; margin-top: 1rem; }
    .pagamento { width: 100%; margin-top: 2rem; padding: 1rem; font-size: 1.2rem; }

    /* RESPONSIVE PER MOBILE */
    @media (max-width: 900px) {
        .carrello-layout {
            grid-template-columns: 1fr; /* Le colonne si impilano */
        }
        .prodotto-item {
            flex-wrap: wrap; /* Permette agli elementi di andare a capo su schermi stretti */
        }
        .prodotto-info {
            flex-basis: 100%;
            order: -1; /* Sposta le info del prodotto in cima su mobile */
            margin-bottom: 0.5rem;
        }
        
        /* Responsive per il pop-up carrello vuoto */
        .empty-cart-container {
            padding: 1.5rem;
        }
        .empty-cart-title {
            font-size: 1.5rem;
        }
        .empty-cart-message {
            font-size: 1rem;
        }
    }
</style>