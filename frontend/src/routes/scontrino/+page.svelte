<script>
	import { onMount } from 'svelte';
	import { carrello } from '../../stores.js';

	const API_URL = 'http://127.0.0.1:5000';
	let scontrinoFinale = null;
	let errore = '';
    let isLoading = true;

	onMount(async () => {
		// ... la logica onMount rimane la stessa ...
		const carrelloCorrente = $carrello;
		if (Object.keys(carrelloCorrente).length === 0) {
			errore = "Operazione non valida: il carrello è già vuoto.";
            isLoading = false;
			return;
		}
		const carrelloArray = Object.values(carrelloCorrente).map(({ id, quantita }) => ({ id, quantita }));
		try {
			const response = await fetch(`${API_URL}/api/scontrino`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(carrelloArray) });
			const data = await response.json();
			if (!response.ok) throw new Error(data.errore || "Errore sconosciuto.");
			scontrinoFinale = data;
			$carrello = {};
		} catch (e) {
			errore = e.message;
		} finally {
            isLoading = false;
        }
	});

	// Funzione per la stampa
	function stampaRicevuta() {
		window.print();
	}
</script>

<svelte:head>
	<title>Scontrino</title>
</svelte:head>

<div class="contenitore-scontrino">
    {#if isLoading}
		<p>Generazione dello scontrino in corso...</p>
    {:else if scontrinoFinale}
		<h1>Grazie per il tuo acquisto!</h1>
        <h2>Riepilogo Scontrino</h2>
		<div class="dettagli">
			<ul>
				{#each scontrinoFinale.voci as voce}
					<li>
						<span>{voce.nome_prodotto} (x{voce.quantita})</span>
						<span>{voce.prezzo_totale.toFixed(2)} €</span>
					</li>
				{/each}
			</ul>
			<hr/>
			<div class="totali">
				<p><span>Totale IVA</span> <span>{scontrinoFinale.totale_iva.toFixed(2)} €</span></p>
				<p class="complessivo"><span>Totale Complessivo</span> <strong>{scontrinoFinale.totale_complessivo.toFixed(2)} €</strong></p>
			</div>
		</div>
		<div class="actions">
			<a href="/" class="torna-home">Torna al Negozio</a>
			<button on:click={stampaRicevuta}>Stampa Ricevuta</button>
		</div>
	{:else if errore}
        <h1>Oops! Qualcosa è andato storto.</h1>
		<p class="errore">{errore}</p>
        <a href="/carrello" class="torna-home">Torna al Carrello</a>
	{/if}
</div>

<style>
    .contenitore-scontrino { max-width: 600px; margin: 2rem auto; padding: 2rem; background-color: var(--colore-sfondo-secondario); border: 1px solid var(--colore-bordi); border-radius: 8px; }
    ul { list-style: none; padding: 0; }
    li, .totali p { display: flex; justify-content: space-between; padding: 0.75rem 0; }
    hr { border: none; border-top: 1px solid var(--colore-bordi); margin: 1rem 0; }
    .complessivo strong { font-size: 1.3rem; color: var(--colore-accento); }
	.actions { display: flex; justify-content: space-between; align-items: center; margin-top: 2rem; }
    .errore { color: #e53e3e; }

	/* Stili applicati SOLO durante la stampa */
	@media print {
		/* Nascondiamo tutto tranne la sezione dello scontrino */
		body * {
			visibility: hidden;
		}
		.contenitore-scontrino, .contenitore-scontrino * {
			visibility: visible;
		}
		/* Posizioniamo la sezione di stampa in cima alla pagina */
		.contenitore-scontrino {
			position: absolute;
			left: 0;
			top: 0;
			width: 100%;
			margin: 0;
			padding: 0;
			border: none;
			box-shadow: none;
			background-color: white;
			color: black;
		}
		/* Nascondiamo i bottoni durante la stampa */
		.actions {
			display: none;
		}
	}
</style>