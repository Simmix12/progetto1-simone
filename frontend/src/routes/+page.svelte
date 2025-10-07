<script>
	import { onMount } from 'svelte';
	import { carrello } from '../stores.js'; // Usiamo lo store

	const API_URL = 'http://127.0.0.1:5000';

	let prodottiDisponibili = [];
	let errore = '';

	// Stato per il termine di ricerca
	let cercaTermine = '';
    // Stato per controllare la visibilità della tendina (autocomplete)
    let showSuggestions = false;

    // Categorie fisse definite in base al backend (ALIQUOTE_IVA)
    const categorieFisse = ['Alimentari', 'Medicinali', 'Altro'];
    // Stato per il filtro categoria. Inizializzato a 'Tutti'
    let categoriaSelezionata = 'Tutti';

	onMount(async () => {
		try {
			const response = await fetch(`${API_URL}/api/prodotti`);
			if (!response.ok) {
				throw new Error('Errore nel caricamento dei prodotti dal server.');
			}
			let prodottiRicevuti = await response.json();
            
            // ESSENZIALE: Aggiungiamo il campo 'categoria' ai prodotti ricevuti
            // basandoci sul nome. Questo è un HACK per compensare la mancanza nel backend.
            prodottiDisponibili = prodottiRicevuti.map(p => {
                // Tenta di indovinare o assegnare una categoria predefinita
                if (p.nome.includes('Pane') || p.nome.includes('Latte')) {
                    p.categoria = 'Alimentari';
                } else if (p.nome.includes('Oki') || p.nome.includes('Termometro')) {
                    p.categoria = 'Medicinali';
                } else {
                    // Categoria di fallback, come definita nel backend
                    p.categoria = 'Altro'; 
                }
                return p;
            });

		} catch (e) {
			errore = e.message;
		}
	});

    // Le categorie disponibili nel filtro
    $: categorieDisponibili = ['Tutti', ...categorieFisse];


	// Logica di filtraggio principale, ora usa la categoria assegnata
	$: prodottiFiltrati = prodottiDisponibili.filter(prodotto => {
        // Filtro per categoria
        const filtroCategoria = categoriaSelezionata === 'Tutti' || prodotto.categoria === categoriaSelezionata;
        
        // Filtro per termine di ricerca (nome)
        const filtroNome = prodotto.nome.toLowerCase().includes(cercaTermine.toLowerCase());
        
        return filtroCategoria && filtroNome;
	});

    // Variabile reattiva per i suggerimenti (mostrati nella tendina)
    $: suggerimenti = cercaTermine.length > 0
        ? prodottiDisponibili
            .filter(prodotto => prodotto.nome.toLowerCase().startsWith(cercaTermine.toLowerCase()))
            .slice(0, 5) // Limita a 5 suggerimenti
        : [];

    // Funzione per selezionare un suggerimento e aggiornare la ricerca
    function selezionaSuggerimento(nomeProdotto) {
        cercaTermine = nomeProdotto; // Imposta il termine di ricerca al nome completo
        showSuggestions = false; // Chiudi la tendina
    }

	function aggiungiAlCarrello(prodotto) {
		if ($carrello[prodotto.id]) {
			$carrello[prodotto.id].quantita++;
		} else {
			$carrello[prodotto.id] = { ...prodotto, quantita: 1 };
		}
	}
</script>

<svelte:head>
	<title>Negozio</title>
</svelte:head>

<h1>Prodotti Disponibili</h1>

{#if errore}
	<p class="errore">{errore}</p>
{/if}

<div class="filtri-container">
    
    <div class="category-filter">
        <label for="category-select">Filtra per Categoria:</label>
        <select id="category-select" bind:value={categoriaSelezionata}>
            {#each categorieDisponibili as categoria}
                <option value={categoria}>{categoria}</option>
            {/each}
        </select>
    </div>

    <div class="search-container">
        <input
            type="text"
            placeholder="Cerca un prodotto (es: Pane)"
            bind:value={cercaTermine}
            on:focus={() => (showSuggestions = true)}
            on:blur={() => setTimeout(() => (showSuggestions = false), 150)}
        />

        {#if showSuggestions && suggerimenti.length > 0}
            <div class="suggestions-dropdown">
                {#each suggerimenti as prodotto (prodotto.id)}
                    <div class="suggestion-item" on:mousedown|preventDefault={() => selezionaSuggerimento(prodotto.nome)}>
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
		{#each prodottiFiltrati as prodotto (prodotto.id)}
			<div class="prodotto-card">
				<h3>{prodotto.nome}</h3>
				<p>{prodotto.prezzo_lordo.toFixed(2)} €</p>
				<button on:click={() => aggiungiAlCarrello(prodotto)}>Aggiungi al Carrello</button>
			</div>
		{/each}
	</div>
{:else}
    <p>Nessun prodotto trovato per i criteri selezionati.</p>
{/if}

<style>
    /* -------------------------------------- */
    /* STILI FILTRI GLOBALI */
    /* -------------------------------------- */
    .filtri-container {
        display: flex;
        gap: 2rem;
        margin-bottom: 2rem;
        align-items: flex-end;
    }

    /* Stile per il selettore categoria */
    .category-filter {
        flex-shrink: 0;
        display: flex;
        flex-direction: column;
        align-items: flex-start;
    }

    .category-filter label {
        font-weight: bold;
        margin-bottom: 0.5rem;
        font-size: 0.9rem;
    }

    .category-filter select {
        padding: 0.9rem;
        border-radius: 8px;
        /* MODIFICATO: Sfondo bianco e bordo più scuro per contrasto */
        background-color: var(--colore-sfondo-principale); 
        border: 2px solid var(--colore-testo, #333); /* Usa il colore testo come bordo */
        color: var(--colore-testo); /* Assicura che il testo sia scuro */
        font-size: 1.1rem;
    }
    
    @media (max-width: 768px) {
        .filtri-container {
            flex-direction: column;
            align-items: stretch;
            gap: 1rem;
        }
        .search-container {
            width: 100%;
        }
    }


    /* -------------------------------------- */
    /* STILI RICERCA */
    /* -------------------------------------- */
    .search-container {
        position: relative; 
        flex-grow: 1;
        max-width: 500px;
    }

    .search-container input {
        width: 100%;
        padding: 1rem;
        border-radius: 8px;
        /* MODIFICATO: Sfondo bianco e bordo più scuro per contrasto */
        background-color: var(--colore-sfondo-principale);
        border: 2px solid var(--colore-testo, #333); 
        color: var(--colore-testo); /* Assicura che il testo digitato sia scuro */
        font-size: 1.1rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    
    /* La tendina usa già lo sfondo secondario che presumibilmente è chiaro/in contrasto */
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

    .suggestion-item:hover {
        background-color: var(--colore-bordi);
    }
    
    .suggestion-item .prezzo {
        font-weight: bold;
        color: var(--colore-accento);
        font-size: 0.9rem;
    }

    /* -------------------------------------- */
    /* STILI GRIGLIA PRODOTTI (precedenti) */
    /* -------------------------------------- */
	.prodotti-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
		gap: 1.5rem;
	}
	.prodotto-card {
		background-color: var(--colore-sfondo-secondario);
		padding: 1.5rem;
		border-radius: 8px;
		border: 1px solid var(--colore-bordi);
		text-align: center;
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
	}
	button:hover {
		opacity: 0.85;
	}
</style>