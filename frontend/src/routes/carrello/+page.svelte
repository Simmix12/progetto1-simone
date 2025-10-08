<script>
    import { carrello } from '../../stores.js';
    import { goto } from '$app/navigation';
    import MetodoPagamento from '../../components/MetodoPagamento.svelte';
    import Modal from '../../components/Modal.svelte';

    let carrelloItems = Object.values($carrello);
    let metodoPagamentoScelto = '';
    
    // Le variabili reattive $: si aggiorneranno automaticamente quando $carrello cambia
    $: isCartEmpty = carrelloItems.length === 0;
    $: totaleCarrello = carrelloItems.reduce((acc, item) => acc + item.prezzo_lordo * item.quantita, 0);

    const API_URL = 'http://127.0.0.1:5000';

    function procediAlPagamento() {
        if (!metodoPagamentoScelto) return;
        goto(`/pagamento?metodo=${metodoPagamentoScelto}`);
    }

    // --- NUOVE FUNZIONI PER GESTIRE LA QUANTITÀ ---
    function incrementaQuantita(prodottoId) {
        if ($carrello[prodottoId]) {
            $carrello[prodottoId].quantita++;
            $carrello = $carrello; // Forza l'aggiornamento
            carrelloItems = Object.values($carrello);
        }
    }

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
        <h2>Il tuo carrello è vuoto!</h2>
        <p>Sembra che tu non abbia ancora aggiunto nessun prodotto.</p>
        <a href="/" class="torna-negozio-btn">Torna al Negozio</a>
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
    .torna-negozio-btn { display: inline-block; margin-top: 1.5rem; padding: 0.75rem 1.5rem; font-weight: bold; text-decoration: none; border-radius: 8px; }

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
    }
</style>