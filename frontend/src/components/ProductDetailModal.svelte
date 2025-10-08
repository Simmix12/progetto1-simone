<script>
    import { createEventDispatcher } from 'svelte';

    export let prodotto;

    const dispatch = createEventDispatcher();
    const API_URL = 'http://127.0.0.1:5000';

    function handleClose() {
        dispatch('close');
    }

    function handleAddToCart() {
        dispatch('addToCart', prodotto);
    }

    // Funzione per gestire la pressione di un tasto sulla finestra
    function handleKeydown(event) {
        // Se il tasto premuto è 'Escape', chiudi il modale
        if (event.key === 'Escape') {
            handleClose();
        }
    }
</script>

<svelte:window on:keydown={handleKeydown}/>

<div
    class="modal-backdrop"
    on:click|self={handleClose}
    on:keydown={(e) => { if (e.key === 'Enter' || e.key === 'Space') handleClose(); }}
    role="button"
    tabindex="0"
    aria-label="Chiudi pop-up"
>
    <div class="modal-content" role="dialog" aria-modal="true" aria-labelledby="modal-title">
        <button class="close-btn" on:click={handleClose}>×</button>

        <div class="modal-layout">
            <div class="modal-left">
                <img 
                    src="{API_URL}/static/images/{prodotto.immagine_url}" 
                    alt="Immagine di {prodotto.nome}"
                >
            </div>

            <div class="modal-right">
                <h2 id="modal-title">{prodotto.nome}</h2>
                <p class="prezzo">{prodotto.prezzo_lordo.toFixed(2)} €</p>
                <p class="descrizione">{prodotto.descrizione}</p>
                
                <button class="add-to-cart-btn" on:click={handleAddToCart}>
                    Aggiungi al Carrello
                </button>
            </div>
        </div>
    </div>
</div>

<style>
    .modal-backdrop {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, 0.8);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 1000;
    }
    .modal-content {
        position: relative;
        width: 90%;
        max-width: 900px;
        height: 80%;
        max-height: 600px;
        background-color: var(--colore-sfondo-secondario);
        border-radius: 12px;
        box-shadow: 0 5px 20px rgba(0, 0, 0, 0.4);
        overflow: hidden;
    }
    .close-btn {
        position: absolute;
        top: 10px;
        right: 15px;
        background: none;
        border: none;
        font-size: 2.5rem;
        color: var(--colore-testo);
        cursor: pointer;
        line-height: 1;
        padding: 0;
    }
    .modal-layout {
        display: grid;
        grid-template-columns: 1fr 1fr;
        height: 100%;
        gap: 2rem;
    }
    .modal-left {
        width: 100%;
        height: 100%;
    }
    .modal-left img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }
    .modal-right {
        padding: 2.5rem;
        display: flex;
        flex-direction: column;
    }
    .modal-right h2 {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }
    .modal-right .prezzo {
        font-size: 1.5rem;
        color: var(--colore-accento);
        font-weight: bold;
        margin-bottom: 1.5rem;
    }
    .modal-right .descrizione {
        flex-grow: 1;
        line-height: 1.6;
        overflow-y: auto;
    }
    .add-to-cart-btn {
        width: 100%;
        padding: 1rem;
        font-size: 1.2rem;
        margin-top: 1.5rem;
    }
    @media (max-width: 768px) {
        .modal-layout {
            grid-template-columns: 1fr;
            overflow-y: auto;
        }
        .modal-left {
            height: 250px;
        }
        .modal-right {
            padding: 1.5rem;
        }
        .modal-right h2 {
            font-size: 2rem;
        }
    }
</style>