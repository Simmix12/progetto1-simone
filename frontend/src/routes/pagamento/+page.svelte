<script>
    import { carrello, utente } from '../../stores.js';
    import { page } from '$app/stores';
    import { goto } from '$app/navigation';
    import { onMount } from 'svelte';

    const API_URL = 'http://127.0.0.1:5000';

    // Oggetto per contenere i dati di fatturazione
    let datiFatturazione = {
        nome: '',
        cognome: '',
        via: '',
        citta: '',
        cap: '',
        provincia: ''
    };
    
    // --- LOGICA DI CONTROLLO ACCESSO E CARICAMENTO DATI ---
    onMount(async () => {
        if (!$utente) {
            // 1. Se l'utente non è loggato, reindirizza alla pagina di login
            goto('/login?redirect=/checkout'); // Torna qui dopo il login
            return; // Interrompe l'esecuzione
        }

        // 2. Se l'utente è loggato, recupera i dati del suo profilo
        try {
            const response = await fetch(`${API_URL}/api/profilo/${$utente.id}`);
            if (response.ok) {
                const profilo = await response.json();
                // 3. Popola i dati di fatturazione con le informazioni del profilo
                datiFatturazione = {
                    nome: profilo.nome || '',
                    cognome: profilo.cognome || '',
                    via: profilo.indirizzo?.via || '',
                    citta: profilo.indirizzo?.citta || '',
                    cap: profilo.indirizzo?.cap || '',
                    provincia: profilo.indirizzo?.provincia || ''
                };
            }
        } catch (error) {
            console.error("Errore nel caricamento dei dati di fatturazione:", error);
        }
    });

    const metodoPagamento = $page.url.searchParams.get('metodo');

    const carrelloItems = Object.values($carrello);
    const totaleCarrello = carrelloItems.reduce(
        (acc, item) => acc + item.prezzo_lordo * item.quantita,
        0
    );

    // ... (la logica di validazione della carta rimane invariata) ...
    let cardNumber = '', expiryDate = '', cvc = '';
    let errors = {}, validatedFields = {};

    function formatCardNumber(e) {
        const value = e.target.value.replace(/\D/g, '');
        cardNumber = (value.match(/.{1,4}/g) || []).join(' ').slice(0, 19);
    }

    function formatExpiryDate(e) {
        const value = e.target.value.replace(/\D/g, '');
        expiryDate = value.length > 2 ? `${value.slice(0, 2)}/${value.slice(2, 4)}` : value;
    }

    function validateField(fieldName) {
        delete errors[fieldName];
        delete validatedFields[fieldName];

        switch (fieldName) {
            case 'cardNumber':
                if (!/^\d{16}$/.test(cardNumber.replace(/\s/g, ''))) errors.cardNumber = 'Il numero della carta deve essere di 16 cifre.';
                else validatedFields.cardNumber = true;
                break;
            case 'expiryDate':
                const expiryRegex = /^(0[1-9]|1[0-2])\/?([0-9]{2})$/;
                if (!expiryRegex.test(expiryDate)) errors.expiryDate = 'Usa il formato MM/AA.';
                else {
                    const [, month, year] = expiryDate.match(expiryRegex);
                    const expiry = new Date(`20${year}`, month - 1);
                    const today = new Date();
                    if (expiry < new Date(today.getFullYear(), today.getMonth())) errors.expiryDate = 'La carta è scaduta.';
                    else validatedFields.expiryDate = true;
                }
                break;
            case 'cvc':
                if (!/^\d{3,4}$/.test(cvc)) errors.cvc = 'Il CVC deve avere 3 o 4 cifre.';
                else validatedFields.cvc = true;
                break;
        }
        errors = { ...errors };
        validatedFields = { ...validatedFields };
    }

    function confermaPagamento() {
        validateField('cardNumber');
        validateField('expiryDate');
        validateField('cvc');
        if (Object.keys(errors).length > 0) return;
        console.log("Dati di pagamento e fatturazione inviati:", { ...datiFatturazione });
        goto('/scontrino');
    }
</script>

<svelte:head>
    <title>Completa il tuo ordine</title>
</svelte:head>

<h1>Completa il tuo ordine</h1>

<!-- Layout modificato per avere la colonna riepilogo a destra -->
<div class="checkout-layout">
    <div class="colonna-principale">
        <!-- NUOVA SEZIONE: Dati di Fatturazione -->
        <section class="dati-fatturazione">
            <h2>Dati di Fatturazione</h2>
            <div class="form-row">
                <label>
                    Nome
                    <input type="text" placeholder="Mario" bind:value={datiFatturazione.nome} required />
                </label>
                <label>
                    Cognome
                    <input type="text" placeholder="Rossi" bind:value={datiFatturazione.cognome} required />
                </label>
            </div>
            <label>
                Indirizzo (Via e Numero Civico)
                <input type="text" placeholder="Via Roma, 10" bind:value={datiFatturazione.via} required />
            </label>
            <div class="form-row">
                <label>
                    Città
                    <input type="text" placeholder="Milano" bind:value={datiFatturazione.citta} required />
                </label>
                <label>
                    CAP
                    <input type="text" placeholder="20121" bind:value={datiFatturazione.cap} required />
                </label>
                <label>
                    Provincia
                    <input type="text" placeholder="MI" maxlength="2" bind:value={datiFatturazione.provincia} required />
                </label>
            </div>
        </section>

        <section class="dettagli-pagamento">
            <h2>Dettagli Pagamento</h2>
            {#if metodoPagamento === 'carta'}
                <form on:submit|preventDefault={confermaPagamento}>
                    <label>
                        Numero Carta
                        <input type="text" placeholder="0000 0000 0000 0000"
                               value={cardNumber} on:input={formatCardNumber} on:blur={() => validateField('cardNumber')}
                               class:invalid={errors.cardNumber} class:valid={validatedFields.cardNumber} required />
                        {#if errors.cardNumber}<p class="error-message">{errors.cardNumber}</p>{/if}
                    </label>
                    <div class="form-row">
                        <label>
                            Scadenza (MM/AA)
                            <input type="text" placeholder="MM/AA"
                                   value={expiryDate} on:input={formatExpiryDate} on:blur={() => validateField('expiryDate')}
                                   class:invalid={errors.expiryDate} class:valid={validatedFields.expiryDate} required />
                            {#if errors.expiryDate}<p class="error-message">{errors.expiryDate}</p>{/if}
                        </label>
                        <label>
                            CVC
                            <input type="text" placeholder="123" bind:value={cvc} maxlength="4"
                                   on:blur={() => validateField('cvc')}
                                   class:invalid={errors.cvc} class:valid={validatedFields.cvc} required />
                            {#if errors.cvc}<p class="error-message">{errors.cvc}</p>{/if}
                        </label>
                    </div>
                    <button type="submit" disabled={Object.keys(errors).length > 0 || Object.keys(validatedFields).length < 3}>
                        Paga {totaleCarrello.toFixed(2)} €
                    </button>
                </form>
            {:else if metodoPagamento === 'paypal'}
                <div class="paypal-info">
                    <p>Verrai reindirizzato a PayPal per completare il pagamento.</p>
                    <button on:click={() => goto('/scontrino')}>Continua su PayPal</button>
                </div>
            {:else if metodoPagamento === 'bonifico'}
                 <div class="bonifico-info">
                    <p>Effettua il bonifico alle seguenti coordinate:</p>
                    <p><strong>IBAN:</strong> IT00 A123 4567 8901 2345 6789 0</p>
                    <p><strong>Causale:</strong> Ordine #{Math.floor(Math.random() * 10000)}</p>
                    <button on:click={() => goto('/scontrino')}>Ho effettuato il bonifico</button>
                </div>
            {:else}
                <p>Metodo di pagamento non valido. <a href="/carrello">Torna indietro</a>.</p>
            {/if}
        </section>
    </div>

    <section class="riepilogo-ordine">
        <h2>Riepilogo Ordine</h2>
        {#if carrelloItems.length > 0}
            <ul>
                {#each carrelloItems as item}
                    <li>
                        <span>{item.nome} (x{item.quantita})</span>
                        <strong>{(item.prezzo_lordo * item.quantita).toFixed(2)} €</strong>
                    </li>
                {/each}
            </ul>
            <hr />
            <div class="totale">
                <span>Totale</span>
                <strong>{totaleCarrello.toFixed(2)} €</strong>
            </div>
        {:else}
            <p>Il carrello è vuoto.</p>
        {/if}
    </section>
</div>

<style>
    h1 {
        text-align: center;
        color: var(--colore-accento);
        margin-bottom: 2rem;
    }

    /* MODIFICA: Layout a due colonne asimmetriche */
    .checkout-layout { 
        display: grid; 
        grid-template-columns: 2fr 1fr; /* Colonna principale più larga */
        gap: 2rem; 
        max-width: 1200px; 
        margin: 2rem auto; 
        align-items: start;
    }
    
    .colonna-principale {
        display: flex;
        flex-direction: column;
        gap: 2rem;
    }

    section { 
        background-color: var(--colore-sfondo-secondario); 
        padding: 2rem; 
        border: 1px solid var(--colore-bordi); 
        border-radius: 8px; 
    }
    
    section h2 {
        margin-top: 0;
        margin-bottom: 1.5rem;
    }

    ul { list-style: none; padding: 0; }
    li, .totale { display: flex; justify-content: space-between; padding: 0.75rem 0; }
    .totale { font-size: 1.2rem; }
    form, .dati-fatturazione { display: flex; flex-direction: column; gap: 1rem; }
    .form-row { display: flex; gap: 1rem; }
    .form-row > * { flex: 1; }
    label { display: flex; flex-direction: column; font-size: 0.9rem; font-weight: 500; }
    input { 
        padding: 0.75rem; 
        border-radius: 5px; 
        border: 1px solid var(--colore-bordi); 
        background-color: var(--colore-sfondo-principale); 
        color: var(--colore-testo); 
        margin-top: 0.25rem; 
        transition: border-color 0.2s, box-shadow 0.2s; 
    }
    button { width: 100%; margin-top: 1rem; padding: 1rem; font-size: 1.2rem; }

    input.invalid {
        border-color: #e53e3e;
        box-shadow: 0 0 0 1px #e53e3e;
    }
    input.valid {
        border-color: #28a745;
        box-shadow: 0 0 0 1px #28a745;
    }
    .error-message {
        color: #e53e3e;
        font-size: 0.8rem;
        margin-top: 0.25rem;
    }
    button:disabled {
        background-color: #4a5568;
        cursor: not-allowed;
        opacity: 0.7;
    }

    @media (max-width: 900px) {
        .checkout-layout {
            grid-template-columns: 1fr;
        }
        .riepilogo-ordine {
            grid-row: 1; /* Su mobile, il riepilogo va in cima */
        }
    }
</style>

